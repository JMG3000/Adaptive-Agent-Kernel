"""Bounded adaptive recall path for authenticated AAK requests."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Protocol

from google.adk.apps import App

from aak.adk_app.application import (
    ADAPTIVE_CONTROL_INSTRUCTION,
    run_local_interaction,
)
from aak.corrections import ExplicitCorrection
from aak.memory_bank import MemoryBankProviderError, ScopedMemory
from aak.sessions import AuthenticatedIdentity, AuthenticationError, SessionService


class SimilarityRetriever(Protocol):
    async def retrieve_similar_memories(
        self,
        identity: AuthenticatedIdentity,
        *,
        query: str,
        top_k: int,
    ) -> tuple[ScopedMemory, ...]: ...


class InteractionExecutor(Protocol):
    async def execute(
        self,
        application: App,
        *,
        identity: AuthenticatedIdentity,
        session_id: str,
        prompt: str,
    ) -> str: ...


@dataclass(frozen=True, slots=True)
class AdmittedMemory:
    memory_id: str
    text: str
    distance: float | None
    provenance: str = "MEMORY_BANK"
    authority: str = "UNTRUSTED_DATA"


@dataclass(frozen=True, slots=True)
class PreparedContext:
    control: str
    current_request: str
    retrieved_memory_data: tuple[AdmittedMemory, ...]
    current_correction: ExplicitCorrection | None = None

    def render_user_payload(self) -> str:
        payload: dict[str, object] = {
            "current_user": {"request": self.current_request},
            "retrieved_memory_data": [
                {
                    "memory_id": memory.memory_id,
                    "text": memory.text,
                    "distance": memory.distance,
                    "provenance": memory.provenance,
                    "authority": memory.authority,
                }
                for memory in self.retrieved_memory_data
            ],
        }
        if self.current_correction is not None:
            payload["current_correction"] = {
                "statement": self.current_correction.statement,
                "provenance": "AUTHENTICATED_CURRENT_USER",
                "authority": "USER_DATA",
                "precedence": "GOVERNS_OVER_CONFLICTING_RETRIEVED_MEMORY",
            }
        return json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
        )


@dataclass(frozen=True, slots=True)
class AdaptiveInteraction:
    response: str
    context: PreparedContext


class ContextBuilder:
    """Build the one data payload while keeping control out of user content."""

    def build(
        self,
        *,
        current_request: str,
        admitted_memories: tuple[AdmittedMemory, ...],
        current_correction: ExplicitCorrection | None = None,
    ) -> PreparedContext:
        if (
            not isinstance(current_request, str)
            or not current_request
            or current_request != current_request.strip()
        ):
            raise ValueError("current request must be a non-empty canonical string")
        if current_correction is not None and not isinstance(
            current_correction,
            ExplicitCorrection,
        ):
            raise ValueError("typed explicit correction is required")
        return PreparedContext(
            control=ADAPTIVE_CONTROL_INSTRUCTION,
            current_request=current_request,
            retrieved_memory_data=admitted_memories,
            current_correction=current_correction,
        )


class RetrievalGate:
    """Admit only the provider's highest-ranked exact-scope candidate."""

    def __init__(self, retriever: SimilarityRetriever) -> None:
        self._retriever = retriever

    async def retrieve(
        self,
        identity: AuthenticatedIdentity,
        *,
        current_request: str,
    ) -> tuple[AdmittedMemory, ...]:
        if not isinstance(identity, AuthenticatedIdentity):
            raise AuthenticationError("authenticated identity is required")
        candidates = await self._retriever.retrieve_similar_memories(
            identity,
            query=current_request,
            top_k=2,
        )
        if not candidates:
            return ()
        candidate = candidates[0]
        if (
            not isinstance(candidate, ScopedMemory)
            or not candidate.memory_id
            or candidate.memory_id != candidate.memory_id.strip()
            or not candidate.fact
            or candidate.fact != candidate.fact.strip()
        ):
            raise MemoryBankProviderError(
                "Retrieval Gate received a malformed rank-one memory"
            )
        return (
            AdmittedMemory(
                memory_id=candidate.memory_id,
                text=candidate.fact,
                distance=candidate.distance,
            ),
        )


async def run_adaptive_interaction(
    application: App,
    *,
    sessions: SessionService,
    retrieval_gate: RetrievalGate,
    identity: AuthenticatedIdentity,
    session_id: str,
    current_request: str,
    current_correction: ExplicitCorrection | None = None,
    interaction_executor: InteractionExecutor | None = None,
) -> AdaptiveInteraction:
    """Authorize, retrieve, build separated context, and run one ADK interaction."""

    sessions.get_session(identity, session_id)
    admitted = await retrieval_gate.retrieve(
        identity,
        current_request=current_request,
    )
    context = ContextBuilder().build(
        current_request=current_request,
        admitted_memories=admitted,
        current_correction=current_correction,
    )
    if application.root_agent.instruction != context.control:
        raise RuntimeError("ADK application control does not match Context Builder")
    if interaction_executor is None:
        response = await run_local_interaction(
            application,
            prompt=context.render_user_payload(),
        )
    else:
        response = await interaction_executor.execute(
            application,
            identity=identity,
            session_id=session_id,
            prompt=context.render_user_payload(),
        )
    return AdaptiveInteraction(response=response, context=context)
