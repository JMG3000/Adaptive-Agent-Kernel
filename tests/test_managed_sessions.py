import hashlib
import re
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
    def __init__(
        self,
        *,
        create_returned_user_id=None,
        create_returned_session_id=None,
        get_returned_user_id=None,
        get_returned_session_id=None,
        returned_state=None,
        create_error=None,
    ):
        self.create_returned_user_id = create_returned_user_id
        self.create_returned_session_id = create_returned_session_id
        self.get_returned_user_id = get_returned_user_id
        self.get_returned_session_id = get_returned_session_id
        self.returned_state = returned_state
        self.create_error = create_error
        self.create_calls = []
        self.get_calls = []
        self.sessions = {}

    async def create_session(self, *, app_name, user_id, ttl, session_id):
        self.create_calls.append(
            {
                "app_name": app_name,
                "user_id": user_id,
                "ttl": ttl,
                "session_id": session_id,
            }
        )
        if self.create_error is not None:
            raise self.create_error
        session = AdkSession(
            id=self.create_returned_session_id or session_id,
            appName=app_name,
            userId=self.create_returned_user_id or user_id,
            state=self.returned_state or {},
        )
        self.sessions[session_id] = session
        return session

    async def get_session(self, *, app_name, user_id, session_id):
        self.get_calls.append(
            {
                "app_name": app_name,
                "user_id": user_id,
                "session_id": session_id,
            }
        )
        session = self.sessions.get(session_id)
        if session is None:
            return None
        return AdkSession(
            id=self.get_returned_session_id or session.id,
            appName=app_name,
            userId=self.get_returned_user_id or session.user_id,
            state=self.returned_state or session.state,
        )


FIXED_NONCE = "ab" * 12


def expected_scoped_session_id(identity, nonce=FIXED_NONCE):
    version = b"aak1"
    nonce_bytes = nonce.encode("ascii")
    user_id = identity.user_id.encode("utf-8")
    scope = identity.scope.encode("utf-8")
    encoded_identity = b"".join(
        len(value).to_bytes(4, "big") + value
        for value in (version, nonce_bytes, user_id, scope)
    )
    binding = hashlib.sha256(encoded_identity).hexdigest()[:32]
    return f"aak1-{nonce}-{binding}"


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

    async def create_scoped_session(self, adapter=None, identity=None):
        with patch("aak.managed_sessions.secrets.token_hex") as token_hex:
            token_hex.return_value = FIXED_NONCE
            session = await (adapter or self.adapter).create_session(
                identity or self.user_a,
                ttl="86400s",
            )
        token_hex.assert_called_once_with(12)
        return session

    async def test_scoped_creation_binds_identity_and_supplies_exact_provider_id(self):
        session = await self.create_scoped_session()
        expected_id = expected_scoped_session_id(self.user_a)

        self.assertEqual(expected_id, session.session_id)
        self.assertEqual(62, len(session.session_id))
        self.assertRegex(
            session.session_id,
            re.compile(r"^aak1-[0-9a-f]{24}-[0-9a-f]{32}$"),
        )
        self.assertEqual("user-a", session.user_id)
        self.assertEqual("tenant-1", session.scope)
        self.assertEqual(
            [
                {
                    "app_name": "adaptive_agent_kernel",
                    "user_id": "user-a",
                    "ttl": "86400s",
                    "session_id": expected_id,
                }
            ],
            self.provider.create_calls,
        )

    async def test_same_identity_sessions_have_nonce_dependent_bindings(self):
        nonces = ("11" * 12, "22" * 12)
        with patch(
            "aak.managed_sessions.secrets.token_hex",
            side_effect=nonces,
        ) as token_hex:
            first = await self.adapter.create_session(self.user_a, ttl="86400s")
            second = await self.adapter.create_session(self.user_a, ttl="86400s")

        self.assertEqual(2, token_hex.call_count)
        self.assertEqual(
            expected_scoped_session_id(self.user_a, nonces[0]),
            first.session_id,
        )
        self.assertEqual(
            expected_scoped_session_id(self.user_a, nonces[1]),
            second.session_id,
        )
        self.assertNotEqual(
            first.session_id.split("-")[2],
            second.session_id.split("-")[2],
        )

        fresh_adapter = ManagedSessionAdapter(
            provider=self.provider,
            session_authority=SessionService(),
            app_name="adaptive_agent_kernel",
        )
        self.assertEqual(
            first,
            await fresh_adapter.get_session(self.user_a, first.session_id),
        )
        self.assertEqual(
            second,
            await fresh_adapter.get_session(self.user_a, second.session_id),
        )

    async def test_provider_create_failure_creates_no_local_authority(self):
        provider_error = RuntimeError("injected provider create failure")
        provider = FakeManagedSessionProvider(create_error=provider_error)
        authority = SessionService()
        adapter = ManagedSessionAdapter(
            provider=provider,
            session_authority=authority,
            app_name="adaptive_agent_kernel",
        )

        with self.assertRaises(RuntimeError) as raised:
            await self.create_scoped_session(adapter)

        self.assertIs(provider_error, raised.exception)
        self.assertEqual(1, len(provider.create_calls))
        requested_id = provider.create_calls[0]["session_id"]
        with self.assertRaises(AuthorizationError):
            authority.get_session(self.user_a, requested_id)

    async def test_caller_and_provider_cannot_substitute_authenticated_user(self):
        with self.assertRaises(AuthenticationError):
            await self.adapter.create_session(object(), ttl="3600s")
        self.assertEqual([], self.provider.create_calls)

        provider = FakeManagedSessionProvider(create_returned_user_id="user-b")
        adapter = ManagedSessionAdapter(
            provider=provider,
            session_authority=SessionService(),
            app_name="adaptive_agent_kernel",
        )
        with self.assertRaises(AuthorizationError):
            await self.create_scoped_session(adapter)
        requested_id = provider.create_calls[0]["session_id"]
        with self.assertRaises(AuthorizationError):
            adapter.session_authority.get_session(self.user_a, requested_id)

    async def test_provider_id_substitution_does_not_create_local_authority(self):
        provider = FakeManagedSessionProvider(
            create_returned_session_id="aak1-" + "1" * 24 + "-" + "0" * 32
        )
        adapter = ManagedSessionAdapter(
            provider=provider,
            session_authority=SessionService(),
            app_name="adaptive_agent_kernel",
        )

        with self.assertRaises(AuthorizationError):
            await self.create_scoped_session(adapter)

        requested_id = provider.create_calls[0]["session_id"]
        with self.assertRaises(AuthorizationError):
            adapter.session_authority.get_session(self.user_a, requested_id)

    async def test_cross_user_and_wrong_scope_fail_before_provider_access(self):
        session = await self.create_scoped_session()
        user_b = AuthenticatedIdentity(user_id="user-b", scope="tenant-1")
        wrong_scope = AuthenticatedIdentity(user_id="user-a", scope="tenant-2")

        for identity in (user_b, wrong_scope):
            with self.subTest(identity=identity), self.assertRaises(
                AuthorizationError
            ):
                await self.adapter.get_session(identity, session.session_id)

        self.assertEqual([], self.provider.get_calls)

    async def test_authorized_identity_retrieves_managed_session(self):
        session = await self.create_scoped_session()

        retrieved = await self.adapter.get_session(self.user_a, session.session_id)

        self.assertEqual(session, retrieved)
        self.assertEqual(
            [
                {
                    "app_name": "adaptive_agent_kernel",
                    "user_id": "user-a",
                    "session_id": session.session_id,
                }
            ],
            self.provider.get_calls,
        )

    async def test_fresh_process_restores_same_session_for_same_identity(self):
        created = await self.create_scoped_session()
        fresh_authority = SessionService()
        fresh_adapter = ManagedSessionAdapter(
            provider=self.provider,
            session_authority=fresh_authority,
            app_name="adaptive_agent_kernel",
        )

        restored = await fresh_adapter.get_session(self.user_a, created.session_id)

        self.assertEqual(created, restored)
        self.assertEqual(
            restored,
            fresh_authority.get_session(self.user_a, created.session_id),
        )
        self.assertEqual(1, len(self.provider.get_calls))
        self.assertEqual(
            {
                "app_name": "adaptive_agent_kernel",
                "user_id": self.user_a.user_id,
                "session_id": created.session_id,
            },
            self.provider.get_calls[0],
        )

    async def test_fresh_process_wrong_scope_denies_before_provider_access(self):
        created = await self.create_scoped_session()
        fresh_adapter = ManagedSessionAdapter(
            provider=self.provider,
            session_authority=SessionService(),
            app_name="adaptive_agent_kernel",
        )
        wrong_scope = AuthenticatedIdentity(user_id="user-a", scope="tenant-2")

        with self.assertRaises(AuthorizationError):
            await fresh_adapter.get_session(wrong_scope, created.session_id)

        self.assertEqual([], self.provider.get_calls)

    async def test_fresh_process_wrong_user_denies_before_provider_access(self):
        created = await self.create_scoped_session()
        fresh_adapter = ManagedSessionAdapter(
            provider=self.provider,
            session_authority=SessionService(),
            app_name="adaptive_agent_kernel",
        )
        wrong_user = AuthenticatedIdentity(user_id="user-b", scope="tenant-1")

        with self.assertRaises(AuthorizationError):
            await fresh_adapter.get_session(wrong_user, created.session_id)

        self.assertEqual([], self.provider.get_calls)

    async def test_malformed_wrong_version_and_binding_mismatch_deny_before_provider(self):
        fresh_adapter = ManagedSessionAdapter(
            provider=self.provider,
            session_authority=SessionService(),
            app_name="adaptive_agent_kernel",
        )
        invalid_ids = (
            " malformed ",
            "aak2-" + "1" * 24 + "-" + "0" * 32,
            "aak1-" + "1" * 24 + "-" + "0" * 32,
        )

        for session_id in invalid_ids:
            with self.subTest(session_id=session_id), self.assertRaises(
                AuthorizationError
            ):
                await fresh_adapter.get_session(self.user_a, session_id)

        self.assertEqual([], self.provider.get_calls)

    async def test_legacy_id_without_local_authority_denies_without_scope_inference(self):
        legacy_id = "provider-generated-session"
        self.provider.sessions[legacy_id] = AdkSession(
            id=legacy_id,
            appName="adaptive_agent_kernel",
            userId=self.user_a.user_id,
            state={"scope": self.user_a.scope, "authorized": True},
        )
        fresh_adapter = ManagedSessionAdapter(
            provider=self.provider,
            session_authority=SessionService(),
            app_name="adaptive_agent_kernel",
        )

        with self.assertRaises(AuthorizationError):
            await fresh_adapter.get_session(self.user_a, legacy_id)

        self.assertEqual([], self.provider.get_calls)

    async def test_provider_absence_denies_without_reconstructing_authority(self):
        created = await self.create_scoped_session()
        self.provider.sessions.clear()
        fresh_authority = SessionService()
        fresh_adapter = ManagedSessionAdapter(
            provider=self.provider,
            session_authority=fresh_authority,
            app_name="adaptive_agent_kernel",
        )

        with self.assertRaises(AuthorizationError):
            await fresh_adapter.get_session(self.user_a, created.session_id)

        with self.assertRaises(AuthorizationError):
            fresh_authority.get_session(self.user_a, created.session_id)
        self.assertEqual(1, len(self.provider.get_calls))

    async def test_provider_user_substitution_denies_without_reconstruction(self):
        created = await self.create_scoped_session()
        self.provider.get_returned_user_id = "user-b"
        fresh_authority = SessionService()
        fresh_adapter = ManagedSessionAdapter(
            provider=self.provider,
            session_authority=fresh_authority,
            app_name="adaptive_agent_kernel",
        )

        with self.assertRaises(AuthorizationError):
            await fresh_adapter.get_session(self.user_a, created.session_id)

        with self.assertRaises(AuthorizationError):
            fresh_authority.get_session(self.user_a, created.session_id)
        self.assertEqual(1, len(self.provider.get_calls))

    async def test_provider_id_substitution_denies_without_reconstruction(self):
        created = await self.create_scoped_session()
        self.provider.get_returned_session_id = (
            "aak1-" + "1" * 24 + "-" + "0" * 32
        )
        fresh_authority = SessionService()
        fresh_adapter = ManagedSessionAdapter(
            provider=self.provider,
            session_authority=fresh_authority,
            app_name="adaptive_agent_kernel",
        )

        with self.assertRaises(AuthorizationError):
            await fresh_adapter.get_session(self.user_a, created.session_id)

        with self.assertRaises(AuthorizationError):
            fresh_authority.get_session(self.user_a, created.session_id)
        self.assertEqual(1, len(self.provider.get_calls))

    async def test_existing_local_conflict_denies_and_preserves_authority(self):
        created = await self.create_scoped_session()
        conflicting_identity = AuthenticatedIdentity(
            user_id="user-b",
            scope="tenant-2",
        )
        conflicting_authority = SessionService()
        conflicting = conflicting_authority.create_session(
            conflicting_identity,
            session_id=created.session_id,
        )
        adapter = ManagedSessionAdapter(
            provider=self.provider,
            session_authority=conflicting_authority,
            app_name="adaptive_agent_kernel",
        )

        with self.assertRaises(AuthorizationError):
            await adapter.get_session(self.user_a, created.session_id)

        self.assertEqual([], self.provider.get_calls)
        self.assertEqual(
            conflicting,
            conflicting_authority.get_session(
                conflicting_identity,
                created.session_id,
            ),
        )

    async def test_provider_state_is_not_authority_during_restoration(self):
        created = await self.create_scoped_session()
        self.provider.returned_state = {
            "user_id": "user-b",
            "scope": "tenant-2",
            "authorized": True,
        }
        fresh_adapter = ManagedSessionAdapter(
            provider=self.provider,
            session_authority=SessionService(),
            app_name="adaptive_agent_kernel",
        )

        restored = await fresh_adapter.get_session(self.user_a, created.session_id)

        self.assertEqual(self.user_a.user_id, restored.user_id)
        self.assertEqual(self.user_a.scope, restored.scope)
        self.assertEqual((), restored.history)

    async def test_noncanonical_inputs_fail_closed_before_provider_access(self):
        with self.assertRaises(AuthenticationError):
            await self.adapter.get_session(
                object(),
                expected_scoped_session_id(self.user_a),
            )
        with self.assertRaises(AuthorizationError):
            await self.adapter.get_session(
                self.user_a,
                " " + expected_scoped_session_id(self.user_a),
            )

        self.assertEqual([], self.provider.get_calls)

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
