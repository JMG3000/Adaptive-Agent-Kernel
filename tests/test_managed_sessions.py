import unittest
from unittest.mock import patch

from google.adk.sessions import Session as AdkSession

from aak.managed_sessions import ManagedSessionAdapter, build_vertex_session_adapter
from aak.sessions import (
    AuthenticatedIdentity,
    AuthenticationError,
    AuthorizationError,
    SessionService,
)


class FakeManagedSessionProvider:
    def __init__(self, *, returned_user_id=None):
        self.returned_user_id = returned_user_id
        self.create_calls = []
        self.get_calls = []
        self.sessions = {}

    async def create_session(self, *, app_name, user_id, ttl):
        self.create_calls.append(
            {"app_name": app_name, "user_id": user_id, "ttl": ttl}
        )
        session = AdkSession(
            id="managed-session-1",
            appName=app_name,
            userId=self.returned_user_id or user_id,
        )
        self.sessions[session.id] = session
        return session

    async def get_session(self, *, app_name, user_id, session_id):
        self.get_calls.append(
            {
                "app_name": app_name,
                "user_id": user_id,
                "session_id": session_id,
            }
        )
        return self.sessions.get(session_id)


class ManagedSessionAdapterTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.authority = SessionService()
        self.provider = FakeManagedSessionProvider()
        self.adapter = ManagedSessionAdapter(
            provider=self.provider,
            session_authority=self.authority,
            app_name="adaptive_agent_kernel",
        )
        self.user_a = AuthenticatedIdentity(user_id="user-a", scope="tenant-1")

    async def test_authenticated_identity_supplies_managed_user_and_aak_scope(self):
        session = await self.adapter.create_session(self.user_a, ttl="3600s")

        self.assertEqual("managed-session-1", session.session_id)
        self.assertEqual("user-a", session.user_id)
        self.assertEqual("tenant-1", session.scope)
        self.assertEqual(
            [
                {
                    "app_name": "adaptive_agent_kernel",
                    "user_id": "user-a",
                    "ttl": "3600s",
                }
            ],
            self.provider.create_calls,
        )

    async def test_caller_and_provider_cannot_substitute_authenticated_user(self):
        with self.assertRaises(AuthenticationError):
            await self.adapter.create_session(object(), ttl="3600s")
        self.assertEqual([], self.provider.create_calls)

        provider = FakeManagedSessionProvider(returned_user_id="user-b")
        adapter = ManagedSessionAdapter(
            provider=provider,
            session_authority=SessionService(),
            app_name="adaptive_agent_kernel",
        )
        with self.assertRaises(AuthorizationError):
            await adapter.create_session(self.user_a, ttl="3600s")

    async def test_cross_user_and_wrong_scope_fail_before_provider_access(self):
        session = await self.adapter.create_session(self.user_a, ttl="3600s")
        user_b = AuthenticatedIdentity(user_id="user-b", scope="tenant-1")
        wrong_scope = AuthenticatedIdentity(user_id="user-a", scope="tenant-2")

        for identity in (user_b, wrong_scope):
            with self.subTest(identity=identity), self.assertRaises(
                AuthorizationError
            ):
                await self.adapter.get_session(identity, session.session_id)

        self.assertEqual([], self.provider.get_calls)

    async def test_authorized_identity_retrieves_managed_session(self):
        session = await self.adapter.create_session(self.user_a, ttl="3600s")

        retrieved = await self.adapter.get_session(self.user_a, session.session_id)

        self.assertEqual(session, retrieved)
        self.assertEqual(
            [
                {
                    "app_name": "adaptive_agent_kernel",
                    "user_id": "user-a",
                    "session_id": "managed-session-1",
                }
            ],
            self.provider.get_calls,
        )

    def test_vertex_adapter_requires_explicit_provider_coordinates(self):
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
                    build_vertex_session_adapter(**values)

        with patch("aak.managed_sessions.VertexAiSessionService") as provider_type:
            adapter = build_vertex_session_adapter(
                project="project-1",
                location="us",
                agent_runtime_id="runtime-1",
                session_authority=self.authority,
            )

        provider_type.assert_called_once_with(
            project="project-1",
            location="us",
            agent_engine_id="runtime-1",
        )
        self.assertIs(self.authority, adapter.session_authority)


if __name__ == "__main__":
    unittest.main()
