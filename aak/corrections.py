"""Typed explicit-correction boundary and gated persistence path."""

from __future__ import annotations

from dataclasses import dataclass

from aak.memory import MemoryWriteGate, MemoryWriteRejected
from aak.sessions import AuthenticatedIdentity, SessionEvent, SessionService


@dataclass(frozen=True, slots=True)
class ExplicitCorrection:
    """Correction explicitly identified by the trusted application boundary."""

    statement: str

    def __post_init__(self) -> None:
        if (
            not isinstance(self.statement, str)
            or not self.statement
            or self.statement != self.statement.strip()
        ):
            raise ValueError(
                "correction statement must be a non-empty canonical string"
            )


class CorrectionService:
    """Record an authorized correction through the existing Memory Write Gate."""

    def __init__(
        self,
        *,
        sessions: SessionService,
        memory_write_gate: MemoryWriteGate,
    ) -> None:
        self._sessions = sessions
        self._memory_write_gate = memory_write_gate

    async def persist(
        self,
        identity: AuthenticatedIdentity,
        session_id: str,
        correction: ExplicitCorrection,
    ) -> SessionEvent:
        session = self._sessions.get_session(identity, session_id)
        if not isinstance(correction, ExplicitCorrection):
            raise MemoryWriteRejected("typed explicit correction is required")

        updated = self._sessions.append_event(
            identity,
            session.session_id,
            source="prompt",
            data={
                "authority": "USER_DATA",
                "event_type": "explicit_correction",
                "statement": correction.statement,
            },
        )
        event_index = len(updated.history) - 1
        event = updated.history[event_index]
        await self._memory_write_gate.persist_selected_events(
            identity,
            session.session_id,
            event_indexes=(event_index,),
        )
        return event
