"""Authenticated identity and Session integrity boundary."""

from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any


_UNSET = object()


class AuthenticationError(PermissionError):
    """The application did not provide one unambiguous identity."""


class AuthorizationError(PermissionError):
    """The authenticated identity is not authorized for the Session."""


def _require_unambiguous(value: object, label: str, error: type[Exception]) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise error(f"{label} must be a non-empty canonical string")
    return value


@dataclass(frozen=True, slots=True)
class AuthenticatedIdentity:
    """Identity established by the application's authentication boundary."""

    user_id: str
    scope: str

    def __post_init__(self) -> None:
        _require_unambiguous(self.user_id, "authenticated user_id", AuthenticationError)
        _require_unambiguous(self.scope, "authenticated scope", AuthenticationError)


@dataclass(frozen=True, slots=True)
class SessionEvent:
    """Untrusted persisted history data."""

    source: str
    data: Mapping[str, Any]

    def __post_init__(self) -> None:
        _require_unambiguous(self.source, "event source", ValueError)
        if not isinstance(self.data, Mapping):
            raise TypeError("event data must be a mapping")
        object.__setattr__(self, "data", MappingProxyType(deepcopy(dict(self.data))))


@dataclass(frozen=True, slots=True)
class Session:
    session_id: str
    user_id: str
    scope: str
    history: tuple[SessionEvent, ...] = field(default_factory=tuple)


class SessionService:
    """In-memory seam enforcing authorization on every supported operation."""

    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}

    def create_session(
        self,
        identity: AuthenticatedIdentity,
        *,
        session_id: str,
        requested_user_id: object = _UNSET,
        requested_scope: object = _UNSET,
    ) -> Session:
        principal = self._require_identity(identity)
        canonical_session_id = _require_unambiguous(session_id, "session_id", ValueError)
        self._require_matching_claim(
            requested_user_id,
            principal.user_id,
            "requested user_id",
        )
        self._require_matching_claim(
            requested_scope,
            principal.scope,
            "requested scope",
        )

        existing = self._sessions.get(canonical_session_id)
        if existing is not None:
            self._authorize(principal, existing)
            return existing

        session = Session(
            session_id=canonical_session_id,
            user_id=principal.user_id,
            scope=principal.scope,
        )
        self._sessions[canonical_session_id] = session
        return session

    def get_session(
        self,
        identity: AuthenticatedIdentity,
        session_id: str,
    ) -> Session:
        principal = self._require_identity(identity)
        canonical_session_id = _require_unambiguous(session_id, "session_id", ValueError)
        session = self._sessions.get(canonical_session_id)
        if session is None:
            raise AuthorizationError("Session access denied")
        self._authorize(principal, session)
        return session

    def append_event(
        self,
        identity: AuthenticatedIdentity,
        session_id: str,
        *,
        source: str,
        data: Mapping[str, Any],
    ) -> Session:
        session = self.get_session(identity, session_id)
        updated = Session(
            session_id=session.session_id,
            user_id=session.user_id,
            scope=session.scope,
            history=session.history + (SessionEvent(source=source, data=data),),
        )
        self._sessions[session.session_id] = updated
        return updated

    @staticmethod
    def _require_identity(identity: object) -> AuthenticatedIdentity:
        if not isinstance(identity, AuthenticatedIdentity):
            raise AuthenticationError("authenticated identity is required")
        return identity

    @staticmethod
    def _require_matching_claim(
        requested: object,
        authenticated: str,
        label: str,
    ) -> None:
        if requested is _UNSET:
            return
        canonical = _require_unambiguous(requested, label, AuthorizationError)
        if canonical != authenticated:
            raise AuthorizationError(f"{label} does not match authenticated identity")

    @staticmethod
    def _authorize(identity: AuthenticatedIdentity, session: Session) -> None:
        if identity.user_id != session.user_id or identity.scope != session.scope:
            raise AuthorizationError("Session access denied")
