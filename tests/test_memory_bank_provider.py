import unittest
from types import SimpleNamespace
from unittest.mock import patch

from aak.memory_bank import (
    MemoryBankProviderError,
    NativeMemoryBankAdapter,
    build_memory_write_gate,
    build_native_memory_bank_adapter,
    native_memory_scope,
)
from aak.sessions import AuthenticatedIdentity, AuthorizationError, SessionService


class FakeAsyncPager:
    def __init__(self, items):
        self._items = tuple(items)

    def __aiter__(self):
        async def iterate():
            for item in self._items:
                yield item

        return iterate()


class FakeNativeMemoryProvider:
    def __init__(self):
        self.ingest_calls = []
        self.retrieve_calls = []
        self.retrieved_by_scope = {}
        self.operation = SimpleNamespace(
            name="operations/ingest-1",
            done=True,
            error=None,
        )

    async def ingest_events(self, **kwargs):
        self.ingest_calls.append(kwargs)
        return self.operation

    async def retrieve(self, **kwargs):
        self.retrieve_calls.append(kwargs)
        key = tuple(sorted(kwargs["scope"].items()))
        return FakeAsyncPager(self.retrieved_by_scope.get(key, ()))


def retrieved_memory(*, memory_id, fact, scope, distance=None):
    return SimpleNamespace(
        distance=distance,
        memory=SimpleNamespace(
            name=(
                "projects/project-1/locations/us/reasoningEngines/runtime-1/"
                f"memories/{memory_id}"
            ),
            fact=fact,
            scope=scope,
        )
    )


class MemoryBankProviderTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.sessions = SessionService()
        self.provider = FakeNativeMemoryProvider()
        self.adapter = NativeMemoryBankAdapter(
            provider=self.provider,
            resource_name=(
                "projects/project-1/locations/us/reasoningEngines/runtime-1"
            ),
        )
        self.gate = build_memory_write_gate(
            sessions=self.sessions,
            adapter=self.adapter,
        )
        self.user_a = AuthenticatedIdentity(user_id="user-a", scope="tenant-1")
        self.session = self.sessions.create_session(
            self.user_a,
            session_id="session-a",
        )
        self.session = self.sessions.append_event(
            self.user_a,
            self.session.session_id,
            source="prompt",
            data={
                "message": "remember this",
                "user_id": "forged-user",
                "scope": "forged-scope",
            },
        )

    def test_native_scope_is_deterministic_and_preserves_both_dimensions(self):
        same_authority = AuthenticatedIdentity(user_id="user-a", scope="tenant-1")
        wrong_scope = AuthenticatedIdentity(user_id="user-a", scope="tenant-2")
        wrong_user = AuthenticatedIdentity(user_id="user-b", scope="tenant-1")

        self.assertEqual(
            {"aak_scope": "tenant-1", "user_id": "user-a"},
            native_memory_scope(self.user_a),
        )
        self.assertEqual(
            native_memory_scope(self.user_a),
            native_memory_scope(same_authority),
        )
        self.assertNotEqual(
            native_memory_scope(self.user_a),
            native_memory_scope(wrong_scope),
        )
        self.assertNotEqual(
            native_memory_scope(self.user_a),
            native_memory_scope(wrong_user),
        )

    async def test_authorized_gate_write_uses_native_exact_scope_and_force_flush(self):
        await self.gate.persist_selected_events(
            self.user_a,
            self.session.session_id,
            event_indexes=(0,),
        )

        self.assertEqual(1, len(self.provider.ingest_calls))
        call = self.provider.ingest_calls[0]
        self.assertEqual(
            "projects/project-1/locations/us/reasoningEngines/runtime-1",
            call["name"],
        )
        self.assertEqual(
            {"aak_scope": "tenant-1", "user_id": "user-a"},
            call["scope"],
        )
        self.assertEqual("session-a", call["stream_id"])
        self.assertEqual(
            {"force_flush": True, "wait_for_completion": True},
            call["config"],
        )
        events = call["direct_contents_source"]["events"]
        self.assertEqual(1, len(events))
        self.assertEqual("user", events[0]["content"]["role"])
        self.assertEqual(
            '{"data":{"message":"remember this","scope":"forged-scope",'
            '"user_id":"forged-user"},"source":"prompt"}',
            events[0]["content"]["parts"][0]["text"],
        )

    async def test_cross_user_and_wrong_scope_fail_before_native_ingestion(self):
        identities = (
            AuthenticatedIdentity(user_id="user-b", scope="tenant-1"),
            AuthenticatedIdentity(user_id="user-a", scope="tenant-2"),
        )

        for identity in identities:
            with self.subTest(identity=identity), self.assertRaises(
                AuthorizationError
            ):
                await self.gate.persist_selected_events(
                    identity,
                    self.session.session_id,
                    event_indexes=(0,),
                )

        self.assertEqual([], self.provider.ingest_calls)

    def test_native_adapter_exposes_no_direct_persistent_mutation(self):
        self.assertFalse(hasattr(self.adapter, "add_events_to_memory"))

    async def test_exact_scope_retrieval_reaches_provider_for_each_authority(self):
        user_a_scope_1 = {"aak_scope": "tenant-1", "user_id": "user-a"}
        self.provider.retrieved_by_scope[tuple(sorted(user_a_scope_1.items()))] = (
            retrieved_memory(
                memory_id="memory-1",
                fact="synthetic durable preference",
                scope=user_a_scope_1,
            ),
        )
        wrong_scope = AuthenticatedIdentity(user_id="user-a", scope="tenant-2")
        wrong_user = AuthenticatedIdentity(user_id="user-b", scope="tenant-1")

        intended = await self.adapter.retrieve_scoped_memories(self.user_a)
        cross_scope = await self.adapter.retrieve_scoped_memories(wrong_scope)
        cross_user = await self.adapter.retrieve_scoped_memories(wrong_user)

        self.assertEqual("synthetic durable preference", intended[0].fact)
        self.assertEqual((), cross_scope)
        self.assertEqual((), cross_user)
        self.assertEqual(
            [
                {"aak_scope": "tenant-1", "user_id": "user-a"},
                {"aak_scope": "tenant-2", "user_id": "user-a"},
                {"aak_scope": "tenant-1", "user_id": "user-b"},
            ],
            [call["scope"] for call in self.provider.retrieve_calls],
        )

    async def test_similarity_retrieval_uses_current_request_and_preserves_ranking(self):
        scope = {"aak_scope": "tenant-1", "user_id": "user-a"}
        self.provider.retrieved_by_scope[tuple(sorted(scope.items()))] = (
            retrieved_memory(
                memory_id="memory-relevant",
                fact="prioritize secure delivery",
                scope=scope,
                distance=0.12,
            ),
            retrieved_memory(
                memory_id="memory-unrelated",
                fact="enjoys watercolor painting",
                scope=scope,
                distance=0.83,
            ),
        )
        retrieve_similar = getattr(self.adapter, "retrieve_similar_memories", None)
        self.assertIsNotNone(
            retrieve_similar,
            "native similarity retrieval is unavailable",
        )

        retrieved = await retrieve_similar(
            self.user_a,
            query="Which MVP option should I choose?",
            top_k=2,
        )

        self.assertEqual(
            ["prioritize secure delivery", "enjoys watercolor painting"],
            [memory.fact for memory in retrieved],
        )
        self.assertEqual([0.12, 0.83], [memory.distance for memory in retrieved])
        self.assertEqual(
            {
                "name": (
                    "projects/project-1/locations/us/reasoningEngines/runtime-1"
                ),
                "scope": {"aak_scope": "tenant-1", "user_id": "user-a"},
                "similarity_search_params": {
                    "search_query": "Which MVP option should I choose?",
                    "top_k": 2,
                },
            },
            self.provider.retrieve_calls[-1],
        )

    async def test_provider_response_with_mismatched_scope_fails_closed(self):
        requested = native_memory_scope(self.user_a)
        self.provider.retrieved_by_scope[tuple(sorted(requested.items()))] = (
            retrieved_memory(
                memory_id="memory-1",
                fact="untrusted provider data",
                scope={"aak_scope": "tenant-2", "user_id": "user-a"},
            ),
        )

        with self.assertRaises(MemoryBankProviderError):
            await self.adapter.retrieve_scoped_memories(self.user_a)

    def test_native_adapter_requires_explicit_provider_coordinates(self):
        invalid_values = ("", "   ", None)
        for field_name in ("project", "location", "agent_runtime_id"):
            for invalid in invalid_values:
                values = {
                    "project": "project-1",
                    "location": "us",
                    "agent_runtime_id": "runtime-1",
                }
                values[field_name] = invalid
                with self.subTest(field=field_name, value=invalid), self.assertRaises(
                    ValueError
                ):
                    build_native_memory_bank_adapter(**values)

        with patch("aak.memory_bank.agentplatform.Client") as client_type:
            client_type.return_value.aio.agent_engines.memories = self.provider
            adapter = build_native_memory_bank_adapter(
                project="project-1",
                location="us",
                agent_runtime_id="runtime-1",
            )

        client_type.assert_called_once_with(project="project-1", location="us")
        self.assertIsInstance(adapter, NativeMemoryBankAdapter)
        self.assertEqual(
            "projects/project-1/locations/us/reasoningEngines/runtime-1",
            adapter.resource_name,
        )


if __name__ == "__main__":
    unittest.main()
