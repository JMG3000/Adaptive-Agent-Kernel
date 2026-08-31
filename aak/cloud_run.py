"""Private Cloud Run HTTP composition for the AAK kernel."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Mapping, Protocol

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
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


IAP_CERTS_URL = "https://www.gstatic.com/iap/verify/public_key"
IAP_ISSUER = "https://cloud.google.com/iap"
LOGGER = logging.getLogger(__name__)
_REQUEST_FIELDS = frozenset({"request", "session_id", "correction"})
_VALIDATION_TYPES = frozenset(
    {"extra_forbidden", "json_invalid", "missing", "string_type", "value_error"}
)

_JUDGE_UI_SCRIPT = Path(__file__).with_name("judge_ui.js").read_text(encoding="utf-8")

_JUDGE_UI_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Adaptive Agent Kernel</title>
  <style>
    :root { color-scheme: light; font-family: system-ui, sans-serif; }
    body { margin: 0; background: #f4f7fb; color: #172033; }
    main { max-width: 760px; margin: 3rem auto; padding: 0 1rem; }
    section { background: white; border: 1px solid #dbe3ef; border-radius: 16px; padding: 1.5rem; box-shadow: 0 12px 35px #1b315014; }
    h1 { margin-top: 0; }
    label { display: block; margin: 1rem 0 .35rem; font-weight: 650; }
    textarea, input { box-sizing: border-box; width: 100%; border: 1px solid #aebbd0; border-radius: 8px; padding: .75rem; font: inherit; }
    textarea { min-height: 8rem; resize: vertical; }
    .actions { display: flex; gap: .75rem; margin-top: 1rem; }
    button { border: 0; border-radius: 8px; padding: .7rem 1rem; font: inherit; font-weight: 700; cursor: pointer; }
    button[type=submit] { background: #2457d6; color: white; }
    button[type=button] { background: #e8edf6; color: #172033; }
    #response { display: flex; flex-direction: column; gap: 1rem; min-height: 4rem; margin-top: 1rem; padding: 1rem; border-radius: 8px; background: #f7f9fc; white-space: pre-wrap; }
    #response > :first-child { margin-top: 0; }
    #response > :last-child { margin-bottom: 0; }
    .message { max-width: 88%; padding: .8rem 1rem; border-radius: 10px; }
    .message-user { align-self: flex-end; background: #e8edf6; }
    .message-agent { align-self: flex-start; background: white; border: 1px solid #dbe3ef; }
    .message-label { margin: 0 0 .45rem; color: #526079; font-size: .8rem; font-weight: 700; text-transform: uppercase; letter-spacing: .04em; }
    .message-body > :first-child { margin-top: 0; }
    .message-body > :last-child { margin-bottom: 0; }
    #interaction-feedback:empty { display: none; }
    #response h1, #response h2, #response h3, #response h4, #response h5, #response h6 { line-height: 1.25; }
    #response pre { overflow-x: auto; padding: .8rem; border-radius: 6px; background: #172033; color: #f4f7fb; white-space: pre; }
    #response code { padding: .1rem .25rem; border-radius: 4px; background: #e8edf6; font-family: ui-monospace, SFMono-Regular, Consolas, monospace; }
    #response pre code { padding: 0; background: transparent; color: inherit; }
    #response a { color: #2457d6; }
    .meta { color: #526079; font-size: .9rem; }
  </style>
</head>
<body>
  <main>
    <section>
      <h1>Adaptive Agent Kernel</h1>
      <p>Work with an adaptive agent that can use relevant remembered context while preserving authenticated Session and scope boundaries.</p>
      <form id="interaction-form" action="/v1/interactions" method="post">
        <label for="request">What would you like help with?</label>
        <textarea id="request" name="request" required></textarea>
        <label for="correction">Optional explicit Correction</label>
        <input id="correction" name="correction" placeholder="Correct a remembered preference or fact">
        <div class="actions">
          <button type="submit" disabled>Send</button>
          <button type="button" id="new-session">New Session</button>
        </div>
      </form>
      <p class="meta" id="session-status">New Session — no conversation continuity yet.</p>
      <div id="response" role="log" aria-live="polite" aria-relevant="additions">Your response will appear here.</div>
      <p class="meta" id="interaction-feedback" role="status" aria-live="polite"></p>
      <p class="meta">Built with Google ADK, Gemini 3.5 Flash, Vertex AI, and Cloud Run.</p>
    </section>
  </main>
  <script>__AAK_JUDGE_UI_SCRIPT__</script>
</body>
</html>
"""

JUDGE_UI = _JUDGE_UI_TEMPLATE.replace("__AAK_JUDGE_UI_SCRIPT__", _JUDGE_UI_SCRIPT)


@dataclass(frozen=True, slots=True)
class CloudRunSettings:
    project: str
    vertex_model_location: str
    agent_platform_location: str
    agent_runtime_id: str
    oidc_audience: str
    iap_audience: str
    scope: str

    @classmethod
    def from_env(cls) -> "CloudRunSettings":
        names = {
            "project": "GOOGLE_CLOUD_PROJECT",
            "vertex_model_location": "VERTEX_MODEL_LOCATION",
            "agent_platform_location": "AGENT_PLATFORM_LOCATION",
            "agent_runtime_id": "AGENT_RUNTIME_ID",
            "oidc_audience": "AAK_OIDC_AUDIENCE",
            "iap_audience": "AAK_IAP_AUDIENCE",
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


class GoogleIapVerifier:
    def verify(self, token: str, *, audience: str) -> Mapping[str, object]:
        claims = id_token.verify_token(
            token,
            google_requests.Request(),
            audience=audience,
            certs_url=IAP_CERTS_URL,
        )
        if claims.get("iss") != IAP_ISSUER:
            raise ValueError("invalid token issuer")
        return claims


class InteractionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request: str
    session_id: str | None = None
    correction: str | None = None

    @field_validator("request", "correction")
    @classmethod
    def normalize_user_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        canonical = value.strip()
        if not canonical:
            raise ValueError("value must be a non-empty canonical string")
        return canonical

    @field_validator("session_id")
    @classmethod
    def canonical_session_id(cls, value: str | None) -> str | None:
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
    authorization: str | None,
    iap_assertion: str | None,
    *,
    token_verifier: TokenVerifier,
    iap_verifier: TokenVerifier,
    settings: CloudRunSettings,
) -> AuthenticatedIdentity:
    if iap_assertion is not None:
        if not iap_assertion or iap_assertion != iap_assertion.strip():
            raise AuthenticationError("malformed IAP assertion")
        token = iap_assertion
        verifier = iap_verifier
        audience = settings.iap_audience
    else:
        token = _bearer_token(authorization)
        verifier = token_verifier
        audience = settings.oidc_audience
    try:
        claims = verifier.verify(token, audience=audience)
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
    iap_verifier: TokenVerifier | None = None,
    components_loader: Callable[[CloudRunSettings], CloudRunComponents] | None = None,
) -> FastAPI:
    load_settings = settings_loader or CloudRunSettings.from_env
    bearer_verifier = token_verifier or GoogleTokenVerifier()
    signed_iap_verifier = iap_verifier or GoogleIapVerifier()
    load_components = components_loader or _build_components
    app = FastAPI(title="Adaptive Agent Kernel")
    components: CloudRunComponents | None = None

    @app.exception_handler(RequestValidationError)
    async def request_validation_error(
        _request: Request,
        error: RequestValidationError,
    ) -> JSONResponse:
        fields: set[str] = set()
        types: set[str] = set()
        for issue in error.errors():
            location = issue.get("loc")
            field = (
                location[-1]
                if isinstance(location, (list, tuple)) and location
                else None
            )
            fields.add(
                f"body.{field}" if field in _REQUEST_FIELDS else "body.unknown"
            )
            issue_type = issue.get("type")
            types.add(
                issue_type if issue_type in _VALIDATION_TYPES else "validation_error"
            )
        LOGGER.warning(
            "boundary=request_validation fields=%s types=%s",
            ",".join(sorted(fields)),
            ",".join(sorted(types)),
        )
        return JSONResponse(status_code=422, content={"detail": "invalid request"})

    def get_components(settings: CloudRunSettings) -> CloudRunComponents:
        nonlocal components
        if components is None:
            components = load_components(settings)
        return components

    @app.get("/healthz")
    async def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/", response_class=HTMLResponse)
    async def judge_ui() -> HTMLResponse:
        return HTMLResponse(JUDGE_UI)

    @app.post("/v1/interactions", response_model=InteractionResponse)
    async def interaction(
        payload: InteractionRequest,
        authorization: str | None = Header(default=None),
        iap_assertion: str | None = Header(
            default=None,
            alias="X-Goog-IAP-JWT-Assertion",
        ),
    ) -> InteractionResponse:
        try:
            settings = load_settings()
            identity = _identity(
                authorization,
                iap_assertion,
                token_verifier=bearer_verifier,
                iap_verifier=signed_iap_verifier,
                settings=settings,
            )
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
