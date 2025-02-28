import unittest
from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion
from openai.types.completion import Completion
from openai.types.create_embedding_response import CreateEmbeddingResponse
from ai_server.tests.test_base_connection import TestServerClient
from variables import LLM_EMBEDDING_ENGINE_ID, LLM_CHAT_ENGINE_ID


class OpenAiEndpointsTests(TestServerClient):

    openai_client = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        if cls.openai_client is None:
            cls.openai_client = OpenAI(
                api_key="EMPTY",
                base_url=cls.server_client.get_openai_endpoint(),
                default_headers=cls.server_client.get_auth_headers()
            )

    def test_chat_completions_endpoint(self):
        response = self.openai_client.chat.completions.create(
            model=LLM_CHAT_ENGINE_ID,  # change the model name to a Model Engine ID
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Who won the world series in 2020?"},
                {"role": "assistant",
                    "content": "The Los Angeles Dodgers won the World Series in 2020."},
                {"role": "user", "content": "Where was it played?"}
            ]
        )

        self.assertIsInstance(response, ChatCompletion)
        self.assertIsNotNone(response.choices[0].message.content)
        self.assertIsInstance(response.choices[0].message.content, str)

    def test_completions_endpoints(self):
        response = self.openai_client.completions.create(
            model=LLM_CHAT_ENGINE_ID,
            prompt="Write a tagline for an ice cream shop."
        )

        self.assertIsInstance(response, Completion)
        self.assertIsNotNone(response.choices[0].text)
        self.assertIsInstance(response.choices[0].text, str)

    def test_embeddings_endpoints(self):
        response = self.openai_client.embeddings.create(
            model=LLM_EMBEDDING_ENGINE_ID,
            input=["Your text string goes here"]
        )

        self.assertIsInstance(response, CreateEmbeddingResponse)
        self.assertIsNotNone(response.data[0].embedding)
        self.assertGreater(len(response.data[0].embedding), 0)


if __name__ == '__main__':
    unittest.main()
