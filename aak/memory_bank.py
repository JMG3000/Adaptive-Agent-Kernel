"""Provider-backed incremental Memory Bank composition."""

from __future__ import annotations

import hashlib
import json
from typing import Protocol

from google.adk.events import Event
from google.adk.memory import VertexAiMemoryBankService
from google.genai import types

from aak.adk_app.application import APP_NAME
from aak.memory import MemoryWriteGate, MemoryWriteRejected
from aak.sessions import SessionEvent, SessionService


class MemoryBankProvider(Protocol):
    async def add_events_to_memory(
        self,
        *,
        app_name: str,
        user_id: str,
        events: tuple[Event, ...],
        session_id: str,
        custom_metadata: dict[str, object],
    ) -> None: ...


def _require_canonical(value: object, label: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise ValueError(f"{label} must be a non-empty canonical string")
    return value


def _provider_event(
    session_id: str,
    position: int,
    event: SessionEvent,
) -> Event:
    roles = {"prompt": "user", "model": "model"}
    try:
        role = roles[event.source]
    except KeyError as error:
        raise MemoryWriteRejected(
            f"Session event source {event.source!r} is unsupported for Memory Bank"
        ) from error

    try:
        payload = json.dumps(
            {"source": event.source, "data": dict(event.data)},
            sort_keys=True,
            separators=(",", ":"),
        )
    except (TypeError, ValueError) as error:
        raise MemoryWriteRejected("Session event is not serializable") from error

    event_id = hashlib.sha256(
        f"{session_id}\0{position}\0{payload}".encode()
    ).hexdigest()
    return Event(
        id=event_id,
        author=event.source,
        content=types.Content(
            role=role,
            parts=[types.Part(text=payload)],
        ),
    )


class _ProviderIncrementalMemorySink:
    def __init__(self, *, provider: MemoryBankProvider, app_name: str) -> None:
        self._provider = provider
        self._app_name = _require_canonical(app_name, "ADK app name")

    async def add_events_to_memory(
        self,
        *,
        user_id: str,
        scope: str,
        session_id: str,
        events: tuple[SessionEvent, ...],
    ) -> None:
        canonical_user_id = _require_canonical(user_id, "authenticated user_id")
        _require_canonical(scope, "authenticated scope")
        canonical_session_id = _require_canonical(session_id, "session_id")
        provider_events = tuple(
            _provider_event(canonical_session_id, position, event)
            for position, event in enumerate(events)
        )
        await self._provider.add_events_to_memory(
            app_name=self._app_name,
            user_id=canonical_user_id,
            events=provider_events,
            session_id=canonical_session_id,
            custom_metadata={"force_flush": True},
        )


def build_memory_write_gate(
    *,
    sessions: SessionService,
    provider: MemoryBankProvider,
    app_name: str = APP_NAME,
) -> MemoryWriteGate:
    """Compose the only supported provider write path behind the AAK gate."""

    return MemoryWriteGate(
        sessions,
        _ProviderIncrementalMemorySink(provider=provider, app_name=app_name),
    )


def build_vertex_memory_write_gate(
    *,
    sessions: SessionService,
    project: str,
    location: str,
    agent_runtime_id: str,
) -> MemoryWriteGate:
    """Build the gated Vertex Memory Bank writer from explicit coordinates."""

    provider = VertexAiMemoryBankService(
        project=_require_canonical(project, "Google Cloud project"),
        location=_require_canonical(location, "Agent Platform location"),
        agent_engine_id=_require_canonical(agent_runtime_id, "Agent Runtime id"),
    )
    return build_memory_write_gate(sessions=sessions, provider=provider)
