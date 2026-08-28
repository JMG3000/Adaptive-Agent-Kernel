"""Native Memory Bank composition behind the AAK Memory Write Gate."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Protocol

import agentplatform

from aak.memory import MemoryWriteGate, MemoryWriteRejected
from aak.sessions import (
    AuthenticatedIdentity,
    AuthenticationError,
    SessionEvent,
    SessionService,
)


class MemoryBankProviderError(RuntimeError):
    """The native Memory Bank boundary returned an unusable result."""


class NativeMemoryBankProvider(Protocol):
    async def ingest_events(
        self,
        *,
        name: str,
        scope: dict[str, str],
        stream_id: str,
        direct_contents_source: dict[str, object],
        config: dict[str, bool],
    ) -> Any: ...

    async def retrieve(
        self,
        *,
        name: str,
        scope: dict[str, str],
        similarity_search_params: dict[str, str | int] | None = None,
        simple_retrieval_params: dict[str, int] | None = None,
    ) -> Any: ...


@dataclass(frozen=True, slots=True)
class ScopedMemory:
    """Minimal untrusted Memory Bank result exposed by this proof boundary."""

    memory_id: str
    fact: str
    distance: float | None = None


def _require_canonical(value: object, label: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise ValueError(f"{label} must be a non-empty canonical string")
    return value


def _require_resource_segment(value: object, label: str) -> str:
    canonical = _require_canonical(value, label)
    if "/" in canonical:
        raise ValueError(f"{label} must be a resource identifier, not a path")
    return canonical


def native_memory_scope(identity: AuthenticatedIdentity) -> dict[str, str]:
    """Construct the native provider namespace from authenticated AAK authority."""

    if not isinstance(identity, AuthenticatedIdentity):
        raise AuthenticationError("authenticated identity is required")
    if "*" in identity.scope or "*" in identity.user_id:
        raise AuthenticationError("authenticated memory scope cannot contain '*'")
    return {
        "aak_scope": identity.scope,
        "user_id": identity.user_id,
    }


def _provider_event(
    session_id: str,
    position: int,
    event: SessionEvent,
) -> dict[str, object]:
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
    return {
        "event_id": event_id,
        "content": {
            "role": role,
            "parts": [{"text": payload}],
        },
    }


class NativeMemoryBankAdapter:
    """Native exact-scope Memory Bank write and proof-only read boundary."""

    def __init__(
        self,
        *,
        provider: NativeMemoryBankProvider,
        resource_name: str,
    ) -> None:
        self._provider = provider
        self._resource_name = _require_canonical(
            resource_name,
            "Agent Runtime resource name",
        )

    @property
    def resource_name(self) -> str:
        return self._resource_name

    async def _ingest_authorized_events(
        self,
        *,
        user_id: str,
        scope: str,
        session_id: str,
        events: tuple[SessionEvent, ...],
    ) -> None:
        identity = AuthenticatedIdentity(user_id=user_id, scope=scope)
        canonical_session_id = _require_canonical(session_id, "session_id")
        provider_events = [
            _provider_event(canonical_session_id, position, event)
            for position, event in enumerate(events)
        ]
        operation = await self._provider.ingest_events(
            name=self._resource_name,
            scope=native_memory_scope(identity),
            stream_id=canonical_session_id,
            direct_contents_source={"events": provider_events},
            config={"force_flush": True, "wait_for_completion": True},
        )
        if getattr(operation, "error", None):
            raise MemoryBankProviderError("native Memory Bank ingestion failed")
        if getattr(operation, "done", None) is not True:
            raise MemoryBankProviderError(
                "native Memory Bank ingestion/generation did not complete"
            )

    async def retrieve_scoped_memories(
        self,
        identity: AuthenticatedIdentity,
        *,
        limit: int = 100,
    ) -> tuple[ScopedMemory, ...]:
        """Read one exact provider scope for acceptance evidence, not agent context."""

        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 100:
            raise ValueError("memory retrieval limit must be between 1 and 100")
        expected_scope = native_memory_scope(identity)
        pager = await self._provider.retrieve(
            name=self._resource_name,
            scope=expected_scope,
            simple_retrieval_params={"page_size": limit},
        )
        return await self._validated_memories(
            pager,
            expected_scope=expected_scope,
            limit=limit,
        )

    async def retrieve_similar_memories(
        self,
        identity: AuthenticatedIdentity,
        *,
        query: str,
        top_k: int,
    ) -> tuple[ScopedMemory, ...]:
        """Retrieve bounded provider-ranked candidates in one exact AAK scope."""

        canonical_query = _require_canonical(query, "memory retrieval query")
        if not isinstance(top_k, int) or isinstance(top_k, bool) or not 1 <= top_k <= 10:
            raise ValueError("similarity retrieval top_k must be between 1 and 10")
        expected_scope = native_memory_scope(identity)
        pager = await self._provider.retrieve(
            name=self._resource_name,
            scope=expected_scope,
            similarity_search_params={
                "search_query": canonical_query,
                "top_k": top_k,
            },
        )
        return await self._validated_memories(
            pager,
            expected_scope=expected_scope,
            limit=top_k,
        )

    @staticmethod
    async def _validated_memories(
        pager: Any,
        *,
        expected_scope: dict[str, str],
        limit: int,
    ) -> tuple[ScopedMemory, ...]:
        retrieved: list[ScopedMemory] = []
        async for item in pager:
            memory = getattr(item, "memory", None)
            if memory is None or getattr(memory, "scope", None) != expected_scope:
                raise MemoryBankProviderError(
                    "native Memory Bank returned a mismatched or malformed scope"
                )
            try:
                memory_id = _require_canonical(
                    getattr(memory, "name", None),
                    "Memory resource name",
                )
                fact = _require_canonical(
                    getattr(memory, "fact", None),
                    "Memory fact",
                )
            except ValueError as error:
                raise MemoryBankProviderError(
                    "native Memory Bank returned a malformed memory"
                ) from error
            distance = getattr(item, "distance", None)
            if distance is not None:
                if isinstance(distance, bool) or not isinstance(distance, (int, float)):
                    raise MemoryBankProviderError(
                        "native Memory Bank returned a malformed similarity distance"
                    )
                distance = float(distance)
            retrieved.append(
                ScopedMemory(
                    memory_id=memory_id,
                    fact=fact,
                    distance=distance,
                )
            )
            if len(retrieved) == limit:
                break
        return tuple(retrieved)


class _NativeIncrementalMemorySink:
    """Private sink keeping the provider mutation behind MemoryWriteGate."""

    def __init__(self, adapter: NativeMemoryBankAdapter) -> None:
        self._adapter = adapter

    async def add_events_to_memory(
        self,
        *,
        user_id: str,
        scope: str,
        session_id: str,
        events: tuple[SessionEvent, ...],
    ) -> None:
        await self._adapter._ingest_authorized_events(
            user_id=user_id,
            scope=scope,
            session_id=session_id,
            events=events,
        )


def build_memory_write_gate(
    *,
    sessions: SessionService,
    adapter: NativeMemoryBankAdapter,
) -> MemoryWriteGate:
    """Compose the native provider writer behind the existing AAK gate."""

    return MemoryWriteGate(sessions, _NativeIncrementalMemorySink(adapter))


def build_native_memory_bank_adapter(
    *,
    project: str,
    location: str,
    agent_runtime_id: str,
) -> NativeMemoryBankAdapter:
    """Build the native Memory Bank adapter from explicit provider coordinates."""

    canonical_project = _require_resource_segment(project, "Google Cloud project")
    canonical_location = _require_resource_segment(
        location,
        "Agent Platform location",
    )
    canonical_runtime_id = _require_resource_segment(
        agent_runtime_id,
        "Agent Runtime id",
    )
    client = agentplatform.Client(
        project=canonical_project,
        location=canonical_location,
    )
    return NativeMemoryBankAdapter(
        provider=client.aio.agent_engines.memories,
        resource_name=(
            f"projects/{canonical_project}/locations/{canonical_location}/"
            f"reasoningEngines/{canonical_runtime_id}"
        ),
    )
