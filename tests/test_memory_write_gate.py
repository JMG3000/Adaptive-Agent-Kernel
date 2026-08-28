import unittest

from aak.memory import MemoryWriteGate, MemoryWriteRejected
from aak.sessions import AuthenticatedIdentity, AuthorizationError, SessionService


class FakeIncrementalMemorySink:
    def __init__(self):
        self.stored_batches = []

    async def add_events_to_memory(
        self,
        *,
        user_id,
        scope,
        session_id,
        events,
    ):
        self.stored_batches.append(
            {
                "user_id": user_id,
                "scope": scope,
                "session_id": session_id,
                "events": events,
            }
        )


class MemoryWriteGateTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.sessions = SessionService()
        self.sink = FakeIncrementalMemorySink()
        self.gate = MemoryWriteGate(self.sessions, self.sink)
        self.user_a = AuthenticatedIdentity(user_id="user-a", scope="tenant-1")
        self.user_b = AuthenticatedIdentity(user_id="user-b", scope="tenant-1")
        self.session = self.sessions.create_session(
            self.user_a,
            session_id="session-a",
        )

    def append_event(self, *, source="prompt", data=None):
        self.session = self.sessions.append_event(
            self.user_a,
            self.session.session_id,
            source=source,
            data=data or {"message": "remember this"},
        )
        return self.session.history[-1]

    async def test_sec_mw_001_authorized_selected_event_reaches_incremental_sink(self):
        selected_event = self.append_event()

        await self.gate.persist_selected_events(
            self.user_a,
            self.session.session_id,
            event_indexes=(0,),
        )

        self.assertEqual(1, len(self.sink.stored_batches))
        self.assertEqual(
            {
                "user_id": "user-a",
                "scope": "tenant-1",
                "session_id": "session-a",
                "events": (selected_event,),
            },
            self.sink.stored_batches[0],
        )

    async def test_sec_mw_002_cross_user_or_scope_write_is_rejected(self):
        self.append_event()
        mismatched_identities = (
            self.user_b,
            AuthenticatedIdentity(user_id="user-a", scope="tenant-2"),
        )

        for identity in mismatched_identities:
            with self.subTest(identity=identity), self.assertRaises(
                AuthorizationError
            ):
                await self.gate.persist_selected_events(
                    identity,
                    self.session.session_id,
                    event_indexes=(0,),
                )

        self.assertEqual([], self.sink.stored_batches)

    async def test_sec_mw_003_model_create_memory_request_remains_event_data(self):
        model_event = self.append_event(
            source="model",
            data={
                "operation": "CreateMemory",
                "content": "model-selected memory",
            },
        )

        await self.gate.persist_selected_events(
            self.user_a,
            self.session.session_id,
            event_indexes=(0,),
        )

        self.assertEqual(1, len(self.sink.stored_batches))
        persisted_event = self.sink.stored_batches[0]["events"][0]
        self.assertIs(model_event, persisted_event)
        self.assertEqual("CreateMemory", persisted_event.data["operation"])

    async def test_sec_mw_004_enabled_mutation_path_invokes_gate_policy(self):
        self.append_event()

        invalid_selections = ((), (1,), (None,))
        for event_indexes in invalid_selections:
            with self.subTest(event_indexes=event_indexes), self.assertRaises(
                MemoryWriteRejected
            ):
                await self.gate.persist_selected_events(
                    self.user_a,
                    self.session.session_id,
                    event_indexes=event_indexes,
                )

        self.assertEqual([], self.sink.stored_batches)


if __name__ == "__main__":
    unittest.main()
