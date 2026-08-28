import unittest
from unittest.mock import patch

from aak.memory import MemoryWriteGate
from aak.memory_bank import build_memory_write_gate, build_vertex_memory_write_gate
from aak.sessions import AuthenticatedIdentity, AuthorizationError, SessionService


class FakeMemoryBankProvider:
    def __init__(self):
        self.calls = []

    async def add_events_to_memory(
        self,
        *,
        app_name,
        user_id,
        events,
        session_id,
        custom_metadata,
    ):
        self.calls.append(
            {
                "app_name": app_name,
                "user_id": user_id,
                "events": events,
                "session_id": session_id,
                "custom_metadata": custom_metadata,
            }
        )


class MemoryBankProviderTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.sessions = SessionService()
        self.provider = FakeMemoryBankProvider()
        self.gate = build_memory_write_gate(
            sessions=self.sessions,
            provider=self.provider,
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

    async def test_authorized_gate_write_reaches_incremental_provider_boundary(self):
        await self.gate.persist_selected_events(
            self.user_a,
            self.session.session_id,
            event_indexes=(0,),
        )

        self.assertEqual(1, len(self.provider.calls))
        call = self.provider.calls[0]
        self.assertEqual("adaptive_agent_kernel", call["app_name"])
        self.assertEqual("user-a", call["user_id"])
        self.assertEqual("session-a", call["session_id"])
        self.assertEqual({"force_flush": True}, call["custom_metadata"])
        self.assertEqual(1, len(call["events"]))
        provider_event = call["events"][0]
        self.assertEqual("prompt", provider_event.author)
        self.assertEqual("user", provider_event.content.role)
        self.assertEqual(
            '{"data":{"message":"remember this","scope":"forged-scope",'
            '"user_id":"forged-user"},"source":"prompt"}',
            provider_event.content.parts[0].text,
        )

    async def test_cross_user_and_wrong_scope_fail_before_provider_write(self):
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

        self.assertEqual([], self.provider.calls)

    def test_vertex_gate_requires_explicit_provider_coordinates(self):
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
                    build_vertex_memory_write_gate(
                        sessions=self.sessions,
                        **values,
                    )

        with patch("aak.memory_bank.VertexAiMemoryBankService") as provider_type:
            gate = build_vertex_memory_write_gate(
                sessions=self.sessions,
                project="project-1",
                location="us",
                agent_runtime_id="runtime-1",
            )

        provider_type.assert_called_once_with(
            project="project-1",
            location="us",
            agent_engine_id="runtime-1",
        )
        self.assertIsInstance(gate, MemoryWriteGate)


if __name__ == "__main__":
    unittest.main()
