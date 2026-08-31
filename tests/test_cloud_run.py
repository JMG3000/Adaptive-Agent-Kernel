import unittest
from dataclasses import dataclass
from types import SimpleNamespace
from unittest.mock import patch

import httpx
from google.adk.apps import App
from google.adk.sessions import VertexAiSessionService

import aak.cloud_run as cloud_run
from aak.adaptive_recall import ADAPTIVE_CONTROL_INSTRUCTION
from aak.cloud_run import (
    CloudRunSettings,
    ProviderBackedInteractionExecutor,
    create_app,
)
from aak.corrections import ExplicitCorrection
from aak.sessions import AuthenticatedIdentity, Session


class FakeVerifier:
    def __init__(self, claims=None, error=None):
        self.claims = {"sub": "verified-subject"} if claims is None else claims
        self.error = error
        self.calls = []

    def verify(self, token, *, audience):
        self.calls.append((token, audience))
        if self.error:
            raise ValueError(self.error)
        return self.claims


class FakeManagedSessions:
    def __init__(self):
        self.created = []
        self.restored = []
        self.session_authority = FakeAuthority()

    async def create_session(self, identity, *, ttl):
        self.created.append((identity, ttl))
        return Session("aak1-session", identity.user_id, identity.scope)

    async def get_session(self, identity, session_id):
        self.restored.append((identity, session_id))
        return Session(session_id, identity.user_id, identity.scope)


class FakeCorrectionService:
    def __init__(self):
        self.calls = []

    async def persist(self, identity, session_id, correction):
        self.calls.append((identity, session_id, correction))
        return None


class FakeRetrievalGate:
    def __init__(self):
        self.calls = []

    async def retrieve(self, identity, *, current_request):
        self.calls.append((identity, current_request))
        return ()


class FakeExecutor:
    def __init__(self):
        self.calls = []

    async def execute(self, application, *, identity, session_id, prompt):
        self.calls.append((application, identity, session_id, prompt))
        return "deterministic response"


class FakeAuthority:
    def get_session(self, identity, session_id):
        return Session(session_id, identity.user_id, identity.scope)


class FakeApplication:
    class RootAgent:
        instruction = ADAPTIVE_CONTROL_INSTRUCTION

    root_agent = RootAgent()


@dataclass
class FakeComponents:
    managed_sessions: FakeManagedSessions
    correction_service: FakeCorrectionService
    retrieval_gate: FakeRetrievalGate
    application: object
    executor: FakeExecutor


def settings():
    return CloudRunSettings(
        project="test-project",
        vertex_model_location="us",
        agent_platform_location="us",
        agent_runtime_id="123",
        oidc_audience="https://aak.example",
        iap_audience="/projects/491899793855/locations/us-central1/services/aak-mvp",
        scope="tenant-a",
    )


def build_test_app(verifier, components, *, iap_verifier=None):
    return create_app(
        settings_loader=settings,
        token_verifier=verifier,
        iap_verifier=iap_verifier,
        components_loader=lambda config: components,
    )


class CloudRunAuthenticationTests(unittest.IsolatedAsyncioTestCase):
    async def request(self, app, method, path, **kwargs):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.request(method, path, **kwargs)

    async def test_health_is_local_and_does_not_load_components(self):
        verifier = FakeVerifier()
        called = []
        app = create_app(
            settings_loader=lambda: (_ for _ in ()).throw(AssertionError("settings")),
            token_verifier=verifier,
            components_loader=lambda config: called.append(config),
        )

        response = await self.request(app, "GET", "/healthz")

        self.assertEqual(200, response.status_code)
        self.assertEqual({"status": "ok"}, response.json())
        self.assertEqual([], called)
        self.assertEqual([], verifier.calls)

    async def test_judge_ui_loads_without_provider_or_authentication_work(self):
        verifier = FakeVerifier()
        iap_verifier = FakeVerifier()
        loaded = []
        app = create_app(
            settings_loader=lambda: (_ for _ in ()).throw(AssertionError("settings")),
            token_verifier=verifier,
            components_loader=lambda config: loaded.append(config),
        )

        response = await self.request(app, "GET", "/")

        self.assertEqual(200, response.status_code)
        self.assertEqual("text/html; charset=utf-8", response.headers["content-type"])
        self.assertIn("Adaptive Agent Kernel", response.text)
        self.assertIn('action="/v1/interactions"', response.text)
        self.assertIn("New Session", response.text)
        self.assertIn("Google ADK", response.text)
        self.assertIn("Gemini 3.5 Flash", response.text)
        self.assertNotIn("Authorization", response.text)
        self.assertNotIn("Bearer", response.text)
        self.assertEqual([], loaded)
        self.assertEqual([], verifier.calls)
        self.assertEqual([], iap_verifier.calls)

    async def test_verified_iap_subject_and_server_scope_reach_existing_path(self):
        bearer_verifier = FakeVerifier(error="bearer must not be used")
        iap_verifier = FakeVerifier({"sub": "iap-subject-9"})
        sessions = FakeManagedSessions()
        retrieval = FakeRetrievalGate()
        executor = FakeExecutor()
        components = FakeComponents(
            sessions,
            FakeCorrectionService(),
            retrieval,
            FakeApplication(),
            executor,
        )

        response = await self.request(
            build_test_app(
                bearer_verifier,
                components,
                iap_verifier=iap_verifier,
            ),
            "POST",
            "/v1/interactions",
            headers={"X-Goog-IAP-JWT-Assertion": "signed-iap-assertion"},
            json={"request": "Help me decide."},
        )

        self.assertEqual(200, response.status_code)
        identity, ttl = sessions.created[0]
        self.assertEqual(AuthenticatedIdentity("iap-subject-9", "tenant-a"), identity)
        self.assertEqual("86400s", ttl)
        self.assertEqual(
            [("signed-iap-assertion", settings().iap_audience)],
            iap_verifier.calls,
        )
        self.assertEqual([], bearer_verifier.calls)
        self.assertEqual((identity, "Help me decide."), retrieval.calls[0])
        self.assertEqual(identity, executor.calls[0][1])
        self.assertEqual("aak1-session", response.json()["session_id"])

    async def test_invalid_or_missing_iap_subject_fails_closed(self):
        components = FakeComponents(
            FakeManagedSessions(),
            FakeCorrectionService(),
            FakeRetrievalGate(),
            FakeApplication(),
            FakeExecutor(),
        )
        cases = (
            FakeVerifier(error="invalid signature or audience"),
            FakeVerifier({}),
            FakeVerifier({"sub": ""}),
            FakeVerifier({"sub": " noncanonical "}),
            FakeVerifier({"sub": 7}),
        )
        for iap_verifier in cases:
            with self.subTest(iap_verifier=iap_verifier):
                response = await self.request(
                    build_test_app(
                        FakeVerifier(error="bearer must not be used"),
                        components,
                        iap_verifier=iap_verifier,
                    ),
                    "POST",
                    "/v1/interactions",
                    headers={"X-Goog-IAP-JWT-Assertion": "untrusted-assertion"},
                    json={"request": "hello"},
                )
                self.assertEqual(401, response.status_code)
                self.assertEqual(
                    {"detail": "authentication or authorization failed"},
                    response.json(),
                )
                self.assertNotIn("untrusted-assertion", response.text)

    async def test_request_body_cannot_supply_identity_or_provider_authority(self):
        components = FakeComponents(
            FakeManagedSessions(),
            FakeCorrectionService(),
            FakeRetrievalGate(),
            FakeApplication(),
            FakeExecutor(),
        )
        forbidden = {
            "user_id": "attacker",
            "scope": "other-tenant",
            "sub": "attacker",
            "claims": {"sub": "attacker"},
            "project": "other-project",
            "agent_runtime_id": "999",
            "provider_coordinates": {"location": "elsewhere"},
        }
        for name, value in forbidden.items():
            with self.subTest(field=name):
                response = await self.request(
                    build_test_app(
                        FakeVerifier(),
                        components,
                        iap_verifier=FakeVerifier({"sub": "iap-subject-9"}),
                    ),
                    "POST",
                    "/v1/interactions",
                    headers={"X-Goog-IAP-JWT-Assertion": "signed-iap-assertion"},
                    json={"request": "hello", name: value},
                )
                self.assertEqual(422, response.status_code)

    async def test_missing_authorization_is_rejected_without_loading_components(self):
        components = FakeComponents(FakeManagedSessions(), FakeCorrectionService(), FakeRetrievalGate(), object(), FakeExecutor())
        response = await self.request(build_test_app(FakeVerifier(), components), "POST", "/v1/interactions", json={"request": "hello"})
        self.assertEqual(401, response.status_code)
        self.assertEqual({"detail": "authentication or authorization failed"}, response.json())

    async def test_malformed_bearer_header_is_rejected(self):
        components = FakeComponents(FakeManagedSessions(), FakeCorrectionService(), FakeRetrievalGate(), FakeApplication(), FakeExecutor())
        for header in ("Basic token", "Bearer", "Bearer one two", " bearer token"):
            with self.subTest(header=header):
                response = await self.request(
                    build_test_app(FakeVerifier(), components),
                    "POST",
                    "/v1/interactions",
                    headers={"Authorization": header},
                    json={"request": "hello"},
                )
                self.assertEqual(401, response.status_code)

    async def test_verified_subject_and_server_scope_form_identity(self):
        verifier = FakeVerifier({"sub": "subject-7"})
        sessions = FakeManagedSessions()
        components = FakeComponents(sessions, FakeCorrectionService(), FakeRetrievalGate(), FakeApplication(), FakeExecutor())
        response = await self.request(build_test_app(verifier, components), "POST", "/v1/interactions", headers={"Authorization": "Bearer signed-token"}, json={"request": "hello"})
        self.assertEqual(200, response.status_code)
        identity, ttl = sessions.created[0]
        self.assertEqual(AuthenticatedIdentity("subject-7", "tenant-a"), identity)
        self.assertEqual("86400s", ttl)
        self.assertEqual({"session_id": "aak1-session", "response": "deterministic response"}, response.json())

    async def test_verifier_rejection_is_generic_and_does_not_leak_token(self):
        verifier = FakeVerifier(error="signed-token-secret")
        components = FakeComponents(FakeManagedSessions(), FakeCorrectionService(), FakeRetrievalGate(), FakeApplication(), FakeExecutor())
        response = await self.request(build_test_app(verifier, components), "POST", "/v1/interactions", headers={"Authorization": "Bearer signed-token-secret"}, json={"request": "hello"})
        self.assertEqual(401, response.status_code)
        self.assertEqual({"detail": "authentication or authorization failed"}, response.json())
        self.assertNotIn("signed-token-secret", response.text)

    async def test_existing_session_and_typed_correction_use_authorized_identity(self):
        verifier = FakeVerifier({"sub": "subject-7"})
        sessions = FakeManagedSessions()
        corrections = FakeCorrectionService()
        executor = FakeExecutor()
        components = FakeComponents(sessions, corrections, FakeRetrievalGate(), FakeApplication(), executor)
        response = await self.request(build_test_app(verifier, components), "POST", "/v1/interactions", headers={"Authorization": "Bearer signed-token"}, json={"request": "hello", "session_id": "aak1-session", "correction": "Prefer Y."})
        self.assertEqual(200, response.status_code)
        identity, restored_id = sessions.restored[0]
        self.assertEqual(AuthenticatedIdentity("subject-7", "tenant-a"), identity)
        self.assertEqual("aak1-session", restored_id)
        self.assertEqual((identity, "aak1-session", ExplicitCorrection("Prefer Y.")), corrections.calls[0])
        self.assertEqual(identity, executor.calls[0][1])
        self.assertEqual("aak1-session", executor.calls[0][2])

    async def test_unknown_request_fields_are_rejected(self):
        components = FakeComponents(FakeManagedSessions(), FakeCorrectionService(), FakeRetrievalGate(), FakeApplication(), FakeExecutor())
        response = await self.request(build_test_app(FakeVerifier(), components), "POST", "/v1/interactions", headers={"Authorization": "Bearer token"}, json={"request": "hello", "provider_user": "bad"})
        self.assertEqual(422, response.status_code)

    async def test_request_validation_records_only_sanitized_boundary_evidence(self):
        components = FakeComponents(
            FakeManagedSessions(),
            FakeCorrectionService(),
            FakeRetrievalGate(),
            FakeApplication(),
            FakeExecutor(),
        )
        rejected_value = {"private_marker": "should-not-appear"}

        with self.assertLogs("aak.cloud_run", level="WARNING") as captured:
            response = await self.request(
                build_test_app(FakeVerifier(), components),
                "POST",
                "/v1/interactions",
                headers={"Authorization": "Bearer token"},
                json={"request": rejected_value},
            )

        self.assertEqual(422, response.status_code)
        self.assertEqual({"detail": "invalid request"}, response.json())
        evidence = "\n".join(captured.output)
        self.assertIn("boundary=request_validation", evidence)
        self.assertIn("fields=body.request", evidence)
        self.assertIn("types=string_type", evidence)
        self.assertNotIn("should-not-appear", evidence)
        self.assertNotIn("should-not-appear", response.text)

    async def test_user_authored_text_is_normalized_at_the_http_boundary(self):
        sessions = FakeManagedSessions()
        corrections = FakeCorrectionService()
        retrieval = FakeRetrievalGate()
        components = FakeComponents(
            sessions,
            corrections,
            retrieval,
            FakeApplication(),
            FakeExecutor(),
        )

        response = await self.request(
            build_test_app(FakeVerifier(), components),
            "POST",
            "/v1/interactions",
            headers={"Authorization": "Bearer token"},
            json={
                "request": "  Help me decide.\n",
                "correction": " Prefer secure delivery. ",
            },
        )

        self.assertEqual(200, response.status_code)
        identity = AuthenticatedIdentity("verified-subject", "tenant-a")
        self.assertEqual((identity, "Help me decide."), retrieval.calls[0])
        self.assertEqual(
            (
                identity,
                "aak1-session",
                ExplicitCorrection("Prefer secure delivery."),
            ),
            corrections.calls[0],
        )

    async def test_configuration_is_required_for_interactions(self):
        components = FakeComponents(FakeManagedSessions(), FakeCorrectionService(), FakeRetrievalGate(), FakeApplication(), FakeExecutor())
        response = await self.request(
            create_app(
                settings_loader=lambda: (_ for _ in ()).throw(ValueError("missing configuration")),
                token_verifier=FakeVerifier(),
                components_loader=lambda config: components,
            ),
            "POST",
            "/v1/interactions",
            headers={"Authorization": "Bearer token"},
            json={"request": "hello"},
        )
        self.assertEqual(422, response.status_code)

    async def test_retrieval_gate_receives_authenticated_identity_and_request(self):
        verifier = FakeVerifier({"sub": "subject-7"})
        sessions = FakeManagedSessions()
        retrieval = FakeRetrievalGate()
        components = FakeComponents(sessions, FakeCorrectionService(), retrieval, FakeApplication(), FakeExecutor())
        response = await self.request(
            build_test_app(verifier, components),
            "POST",
            "/v1/interactions",
            headers={"Authorization": "Bearer token"},
            json={"request": "Choose safely."},
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            (AuthenticatedIdentity("subject-7", "tenant-a"), "Choose safely."),
            retrieval.calls[0],
        )

    async def test_invalid_sub_is_rejected(self):
        components = FakeComponents(FakeManagedSessions(), FakeCorrectionService(), FakeRetrievalGate(), object(), FakeExecutor())
        for claims in ({}, {"sub": ""}, {"sub": " bad "}, {"sub": 7}, []):
            response = await self.request(build_test_app(FakeVerifier(claims), components), "POST", "/v1/interactions", headers={"Authorization": "Bearer token"}, json={"request": "hello"})
            self.assertEqual(401, response.status_code)


class ProviderRunnerTests(unittest.IsolatedAsyncioTestCase):
    async def test_provider_executor_uses_vertex_session_service_and_authorized_identity(self):
        provider_sessions = VertexAiSessionService(
            project="test-project", location="us", agent_engine_id="123"
        )
        class FakeRunner:
            def __init__(self):
                self.run_async_call = None

            async def run_async(self, **kwargs):
                self.run_async_call = kwargs
                yield SimpleNamespace(
                    content=SimpleNamespace(
                        parts=[SimpleNamespace(text="provider response")]
                    )
                )

            async def close(self):
                return None

        runner = FakeRunner()
        executor = ProviderBackedInteractionExecutor(
            session_service=provider_sessions,
            runner_factory=lambda **kwargs: runner,
        )
        application = object()
        identity = AuthenticatedIdentity("subject-7", "tenant-a")

        result = await executor.execute(
            application,
            identity=identity,
            session_id="aak1-session",
            prompt="payload",
        )

        self.assertEqual("subject-7", runner.run_async_call["user_id"])
        self.assertEqual("aak1-session", runner.run_async_call["session_id"])
        self.assertEqual("provider response", result)
        self.assertIsInstance(executor.session_service, VertexAiSessionService)


class GoogleIapVerifierTests(unittest.TestCase):
    def test_verifier_uses_iap_keys_exact_audience_and_requires_issuer(self):
        audience = "/projects/491899793855/locations/us-central1/services/aak-mvp"
        verifier = cloud_run.GoogleIapVerifier()

        with patch("aak.cloud_run.id_token.verify_token") as verify_token:
            verify_token.return_value = {
                "iss": "https://cloud.google.com/iap",
                "sub": "iap-subject-9",
            }
            claims = verifier.verify("signed-assertion", audience=audience)

        self.assertEqual("iap-subject-9", claims["sub"])
        verify_token.assert_called_once()
        _, request = verify_token.call_args.args
        self.assertIsNotNone(request)
        self.assertEqual("signed-assertion", verify_token.call_args.args[0])
        self.assertEqual(audience, verify_token.call_args.kwargs["audience"])
        self.assertEqual(cloud_run.IAP_CERTS_URL, verify_token.call_args.kwargs["certs_url"])

        with patch("aak.cloud_run.id_token.verify_token") as verify_token:
            verify_token.return_value = {"iss": "https://accounts.google.com", "sub": "x"}
            with self.assertRaisesRegex(ValueError, "issuer"):
                verifier.verify("signed-assertion", audience=audience)

        with patch("aak.cloud_run.id_token.verify_token") as verify_token:
            verify_token.side_effect = ValueError("wrong audience")
            with self.assertRaisesRegex(ValueError, "wrong audience"):
                verifier.verify("signed-assertion", audience=audience)


if __name__ == "__main__":
    unittest.main()
