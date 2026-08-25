"""Policy gate for incremental persistence of selected Session events."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from .sessions import (
    AuthenticatedIdentity,
    AuthorizationError,
    Session,
    SessionEvent,
    SessionService,
)


class MemoryWriteRejected(AuthorizationError):
    """The requested persistent-memory mutation failed closed."""


class IncrementalMemorySink(Protocol):
    """Local seam matching incremental add-events persistence."""

    def add_events_to_memory(
        self,
        *,
        user_id: str,
        scope: str,
        session_id: str,
        events: tuple[SessionEvent, ...],
    ) -> None: ...


class MemoryWriteGate:
    """The only supported AAK persistent-memory mutation boundary."""

    def __init__(
        self,
        sessions: SessionService,
        sink: IncrementalMemorySink,
    ) -> None:
        self._sessions = sessions
        self._sink = sink

    def persist_selected_events(
        self,
        identity: AuthenticatedIdentity,
        session_id: str,
        *,
        event_indexes: Sequence[int],
    ) -> None:
        session = self._sessions.get_session(identity, session_id)
        selected_events = self._authorize_selection(session, event_indexes)
        self._sink.add_events_to_memory(
            user_id=session.user_id,
            scope=session.scope,
            session_id=session.session_id,
            events=selected_events,
        )

    @staticmethod
    def _authorize_selection(
        session: Session,
        event_indexes: Sequence[int],
    ) -> tuple[SessionEvent, ...]:
        if not isinstance(event_indexes, Sequence) or not event_indexes:
            raise MemoryWriteRejected("at least one Session event must be selected")

        selected = []
        for index in event_indexes:
            if (
                not isinstance(index, int)
                or isinstance(index, bool)
                or index < 0
                or index >= len(session.history)
            ):
                raise MemoryWriteRejected("Session event selection is invalid")
            selected.append(session.history[index])
        return tuple(selected)
