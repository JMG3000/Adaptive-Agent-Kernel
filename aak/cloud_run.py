"""Private Cloud Run HTTP composition for the AAK kernel."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Callable, Mapping, Protocol

from fastapi import FastAPI, Header, HTTPException
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from google.adk.sessions import VertexAiSessionService
from pydantic import BaseModel, ConfigDict, field_validator

from aak.adaptive_recall import RetrievalGate, run_adaptive_interaction
from aak.adk_app.application import ProviderBackedInteractionExecutor, build_vertex_app
from aak.corrections import CorrectionService, ExplicitCorrection
from aak.managed_sessions import build_vertex_session_adapter
from aak.memory_bank import build_memory_write_gate, build_native_memory_bank_adapter
from aak.sessions import AuthenticatedIdentity, AuthenticationError, AuthorizationError, SessionService


@dataclass(frozen=True, slots=True)
class CloudRunSettings:
    project: str
    vertex_model_location: str
    agent_platform_location: str
    agent_runtime_id: str
    oidc_audience: str
    scope: str

    @classmethod
    def from_env(cls) -> "CloudRunSettings":
        names = {
            "project": "GOOGLE_CLOUD_PROJECT",
            "vertex_model_location": "VERTEX_MODEL_LOCATION",
            "agent_platform_location": "AGENT_PLATFORM_LOCATION",
            "agent_runtime_id": "AGENT_RUNTIME_ID",
            "oidc_audience": "AAK_OIDC_AUDIENCE",
            "scope": "AAK_SCOPE",
        }
        values: dict[str, str] = {}
        for field, name in names.items():
            value = os.environ.get(name)
            if not isinstance(value, str) or not value or value != value.strip():
                raise ValueError(f"{name} must be configured as a non-empty canonical value")
            values[field] = value
        return cls(**values)


class TokenVerifier(Protocol):
    def verify(self, token: str, *, audience: str) -> Mapping[str, object]: ...


class GoogleTokenVerifier:
    def verify(self, token: str, *, audience: str) -> Mapping[str, object]:
        claims = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            audience=audience,
        )
        issuer = claims.get("iss")
        if issuer not in {"accounts.google.com", "https://accounts.google.com"}:
            raise ValueError("invalid token issuer")
        return claims


class InteractionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request: str
    session_id: str | None = None
    correction: str | None = None

    @field_validator("request", "session_id", "correction")
    @classmethod
    def canonical_strings(cls, value: str | None) -> str | None:
        if value is not None and (not value or value != value.strip()):
            raise ValueError("value must be a non-empty canonical string")
        return value


class InteractionResponse(BaseModel):
    session_id: str
    response: str


@dataclass(slots=True)
class CloudRunComponents:
    managed_sessions: object
    correction_service: CorrectionService
    retrieval_gate: RetrievalGate
    application: object
    executor: object


def _build_components(settings: CloudRunSettings) -> CloudRunComponents:
    sessions = SessionService()
    managed_sessions = build_vertex_session_adapter(
        project=settings.project,
        location=settings.agent_platform_location,
        agent_runtime_id=settings.agent_runtime_id,
        session_authority=sessions,
    )
    memory_adapter = build_native_memory_bank_adapter(
        project=settings.project,
        location=settings.agent_platform_location,
        agent_runtime_id=settings.agent_runtime_id,
    )
    memory_write_gate = build_memory_write_gate(sessions=sessions, adapter=memory_adapter)
    provider_sessions = VertexAiSessionService(
        project=settings.project,
        location=settings.agent_platform_location,
        agent_engine_id=settings.agent_runtime_id,
    )
    return CloudRunComponents(
        managed_sessions=managed_sessions,
        correction_service=CorrectionService(
            sessions=sessions,
            memory_write_gate=memory_write_gate,
        ),
        retrieval_gate=RetrievalGate(memory_adapter),
        application=build_vertex_app(
            project=settings.project,
            location=settings.vertex_model_location,
        ),
        executor=ProviderBackedInteractionExecutor(
            session_service=provider_sessions,
        ),
    )


def _bearer_token(header: str | None) -> str:
    if not isinstance(header, str):
        raise AuthenticationError("authentication required")
    parts = header.split(" ")
    if len(parts) != 2 or parts[0].lower() != "bearer" or not parts[1]:
        raise AuthenticationError("malformed authentication header")
    return parts[1]


def _identity(
    header: str | None,
    *,
    verifier: TokenVerifier,
    settings: CloudRunSettings,
) -> AuthenticatedIdentity:
    token = _bearer_token(header)
    try:
        claims = verifier.verify(token, audience=settings.oidc_audience)
    except Exception as error:
        raise AuthenticationError("authentication failed") from error
    try:
        if not isinstance(claims, Mapping):
            raise TypeError("verified claims must be a mapping")
        subject = claims.get("sub")
        return AuthenticatedIdentity(user_id=subject, scope=settings.scope)
    except (AuthenticationError, TypeError) as error:
        raise AuthenticationError("authentication failed") from error


def create_app(
    *,
    settings_loader: Callable[[], CloudRunSettings] | None = None,
    token_verifier: TokenVerifier | None = None,
    components_loader: Callable[[CloudRunSettings], CloudRunComponents] | None = None,
) -> FastAPI:
    load_settings = settings_loader or CloudRunSettings.from_env
    verifier = token_verifier or GoogleTokenVerifier()
    load_components = components_loader or _build_components
    app = FastAPI(title="Adaptive Agent Kernel")
    components: CloudRunComponents | None = None

    def get_components(settings: CloudRunSettings) -> CloudRunComponents:
        nonlocal components
        if components is None:
            components = load_components(settings)
        return components

    @app.get("/healthz")
    async def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/v1/interactions", response_model=InteractionResponse)
    async def interaction(
        payload: InteractionRequest,
        authorization: str | None = Header(default=None),
    ) -> InteractionResponse:
        try:
            settings = load_settings()
            identity = _identity(authorization, verifier=verifier, settings=settings)
            current = get_components(settings)
            if payload.session_id is None:
                session = await current.managed_sessions.create_session(identity, ttl="86400s")
            else:
                session = await current.managed_sessions.get_session(identity, payload.session_id)
            if payload.correction is not None:
                await current.correction_service.persist(
                    identity,
                    session.session_id,
                    ExplicitCorrection(statement=payload.correction),
                )
            result = await run_adaptive_interaction(
                current.application,
                sessions=current.managed_sessions.session_authority,
                retrieval_gate=current.retrieval_gate,
                identity=identity,
                session_id=session.session_id,
                current_request=payload.request,
                interaction_executor=current.executor,
            )
            return InteractionResponse(session_id=session.session_id, response=result.response)
        except (AuthenticationError, AuthorizationError) as error:
            raise HTTPException(status_code=401, detail="authentication or authorization failed") from error
        except ValueError as error:
            raise HTTPException(status_code=422, detail="invalid request or configuration") from error
        except Exception as error:
            raise HTTPException(status_code=502, detail="interaction unavailable") from error

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "aak.cloud_run:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8080")),
    )
