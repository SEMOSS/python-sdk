import unittest
from typing import Generator
from ai_server.py_client.gaas.model import ModelEngine
from test_base_connection import TestServerClient
from variables import LLM_EMBEDDING_ENGINE_ID, LLM_CHAT_ENGINE_ID


class ModelTests(TestServerClient):

    def test_model_ask(self):
        model = ModelEngine(
            engine_id=LLM_CHAT_ENGINE_ID,
        )

        model_response_list = model.ask(
            question='what is the capital of france ey?')

        # Assert that the response is a dictionary with specific keys
        self.assertIsInstance(model_response_list, list)

        model_response = model_response_list[0]

        self.assertIsInstance(model_response, dict)

        self.assertCountEqual(model_response.keys(), [
                              'response', 'numberOfTokensInPrompt', 'numberOfTokensInResponse', 'messageId', 'roomId'])

    def test_model_ask_with_stream(self):

        model = ModelEngine(
            engine_id=LLM_CHAT_ENGINE_ID,
        )

        model_response_stream = model.stream_ask(
            question='what is the capital of france ey?')

        self.assertIsInstance(model_response_stream, Generator)

    def test_model_embeddings(self):
        model = ModelEngine(
            engine_id=LLM_EMBEDDING_ENGINE_ID,
        )

        model_response_list = model.embeddings(
            strings_to_embed=['what is the capital of france ey?'])

        # Assert that the response is a dictionary with specific keys
        self.assertIsInstance(model_response_list, list)

        model_response = model_response_list[0]
        self.assertIsInstance(model_response, dict)

        self.assertCountEqual(model_response.keys(), [
                              'response', 'numberOfTokensInPrompt', 'numberOfTokensInResponse'])


if __name__ == '__main__':
    # python test_model.py -v -m "access_key=my_access_key secret_key=my_secret_key base=http://example.com/api"

    unittest.main()
