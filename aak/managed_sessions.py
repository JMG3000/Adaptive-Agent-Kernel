"""AAK-authorized adapter for managed Agent Platform Sessions."""

from __future__ import annotations

from typing import Protocol

from google.adk.sessions import VertexAiSessionService

from aak.adk_app.application import APP_NAME
from aak.sessions import (
    AuthenticatedIdentity,
    AuthenticationError,
    AuthorizationError,
    Session,
    SessionService,
)


class ManagedSessionRecord(Protocol):
    id: str
    user_id: str


class ManagedSessionProvider(Protocol):
    async def create_session(
        self,
        *,
        app_name: str,
        user_id: str,
        ttl: str,
    ) -> ManagedSessionRecord: ...

    async def get_session(
        self,
        *,
        app_name: str,
        user_id: str,
        session_id: str,
    ) -> ManagedSessionRecord | None: ...


def _require_canonical(value: object, label: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise ValueError(f"{label} must be a non-empty canonical string")
    return value


class ManagedSessionAdapter:
    """Bind managed Session persistence to the existing AAK authority."""

    def __init__(
        self,
        *,
        provider: ManagedSessionProvider,
        session_authority: SessionService,
        app_name: str = APP_NAME,
    ) -> None:
        self._provider = provider
        self._session_authority = session_authority
        self._app_name = _require_canonical(app_name, "ADK app name")

    @property
    def session_authority(self) -> SessionService:
        return self._session_authority

    async def create_session(
        self,
        identity: AuthenticatedIdentity,
        *,
        ttl: str,
    ) -> Session:
        principal = self._require_identity(identity)
        canonical_ttl = _require_canonical(ttl, "Session ttl")
        managed = await self._provider.create_session(
            app_name=self._app_name,
            user_id=principal.user_id,
            ttl=canonical_ttl,
        )
        session_id = self._validate_managed_session(managed, principal)
        return self._session_authority.create_session(
            principal,
            session_id=session_id,
        )

    async def get_session(
        self,
        identity: AuthenticatedIdentity,
        session_id: str,
    ) -> Session:
        principal = self._require_identity(identity)
        authorized = self._session_authority.get_session(principal, session_id)
        managed = await self._provider.get_session(
            app_name=self._app_name,
            user_id=principal.user_id,
            session_id=authorized.session_id,
        )
        managed_id = self._validate_managed_session(managed, principal)
        if managed_id != authorized.session_id:
            raise AuthorizationError("managed Session identity validation failed")
        return authorized

    @staticmethod
    def _require_identity(identity: object) -> AuthenticatedIdentity:
        if not isinstance(identity, AuthenticatedIdentity):
            raise AuthenticationError("authenticated identity is required")
        return identity

    @staticmethod
    def _validate_managed_session(
        managed: ManagedSessionRecord | None,
        identity: AuthenticatedIdentity,
    ) -> str:
        if managed is None or getattr(managed, "user_id", None) != identity.user_id:
            raise AuthorizationError("managed Session identity validation failed")
        try:
            return _require_canonical(getattr(managed, "id", None), "managed Session id")
        except ValueError as error:
            raise AuthorizationError(
                "managed Session identity validation failed"
            ) from error


def build_vertex_session_adapter(
    *,
    project: str,
    location: str,
    agent_runtime_id: str,
    session_authority: SessionService | None = None,
) -> ManagedSessionAdapter:
    """Build the real Vertex-backed adapter from explicit provider inputs."""

    provider = VertexAiSessionService(
        project=_require_canonical(project, "Google Cloud project"),
        location=_require_canonical(location, "Agent Platform location"),
        agent_engine_id=_require_canonical(agent_runtime_id, "Agent Runtime id"),
    )
    return ManagedSessionAdapter(
        provider=provider,
        session_authority=session_authority or SessionService(),
    )
