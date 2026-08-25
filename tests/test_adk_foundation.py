import unittest

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import BaseLlm, LlmResponse
from google.adk.models.google_llm import Gemini
from google.genai import types

from aak.adk_app import (
    MODEL_ID,
    build_app,
    build_vertex_app,
    build_vertex_model,
    run_local_interaction,
)


class FakeLlm(BaseLlm):
    async def generate_content_async(self, llm_request, stream=False):
        del llm_request, stream
        yield LlmResponse(
            content=types.Content(
                role="model",
                parts=[types.Part(text="deterministic ADK response")],
            )
        )


class AdkFoundationTests(unittest.TestCase):
    def test_vertex_configuration_requires_explicit_project_and_location(self):
        invalid_configurations = (
            {"project": None, "location": "test-location"},
            {"project": "test-project", "location": None},
            {"project": "", "location": "test-location"},
            {"project": "test-project", "location": "   "},
        )

        for configuration in invalid_configurations:
            with self.subTest(configuration=configuration), self.assertRaises(
                ValueError
            ):
                build_vertex_model(**configuration)

    def test_builds_actual_adk_app_for_vertex_gemini_3_5_flash(self):
        application = build_vertex_app(
            project="test-project",
            location="test-location",
        )

        self.assertIsInstance(application, App)
        self.assertIsInstance(application.root_agent, Agent)
        self.assertIsInstance(application.root_agent.model, Gemini)
        self.assertEqual("gemini-3.5-flash", MODEL_ID)
        self.assertEqual(MODEL_ID, application.root_agent.model.model)
        self.assertEqual(
            {
                "vertexai": True,
                "project": "test-project",
                "location": "test-location",
            },
            application.root_agent.model.client_kwargs,
        )
        self.assertEqual([], application.root_agent.tools)


class AdkFoundationInteractionTests(unittest.IsolatedAsyncioTestCase):
    async def test_actual_app_and_in_memory_runner_reach_fake_llm_boundary(self):
        application = build_app(model=FakeLlm(model="fake-aak-model"))

        response = await run_local_interaction(
            application,
            prompt="Hello from the AAK deterministic test.",
        )

        self.assertIsInstance(application, App)
        self.assertIsInstance(application.root_agent, Agent)
        self.assertEqual("deterministic ADK response", response)


if __name__ == "__main__":
    unittest.main()
