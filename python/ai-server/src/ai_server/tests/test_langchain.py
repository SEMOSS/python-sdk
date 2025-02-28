import unittest
from ai_server.py_client.gaas.model import ModelEngine
from ai_server.py_client.gaas.vector import VectorEngine
from test_base_connection import TestServerClient
from variables import LLM_CHAT_ENGINE_ID, VECTOR_ENGINE_ID
from langchain.schema import HumanMessage
from langchain_core.outputs import (
    ChatGeneration,
    ChatResult,
)
import os
from langchain_core.documents import Document


class LangChainTests(TestServerClient):

    def test_langchain_chat_model(self):
        model = ModelEngine(
            engine_id=LLM_CHAT_ENGINE_ID,
        )

        langchain_model = model.to_langchain_chat_model()

        messages = [HumanMessage(content='what is the capital of france ey?')]

        model_response = langchain_model._generate(messages=messages)

        # Check that we are returning a langchain ChatResult class object
        self.assertIsInstance(model_response, ChatResult)

        # Check the ChatResult object has the expected attributes
        self.assertTrue(hasattr(model_response, 'generations'))
        self.assertTrue(hasattr(model_response, 'llm_output'))

        # Check that the generations attribute contains a message
        for generation in model_response.generations:
            self.assertIsInstance(generation, ChatGeneration)
            self.assertTrue(hasattr(generation, 'message'))
            self.assertIsNotNone(generation.message)

    def test_langchain_vector_model(self):
        model = VectorEngine(
            engine_id=VECTOR_ENGINE_ID,
        )

        langchain_model = model.to_langchain_vector_store()

        CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
        TEST_FILE_DIR = os.path.join(CURRENT_DIR, "test_files")
        TEST_FILES = [os.path.join(TEST_FILE_DIR, file)
                      for file in os.listdir(TEST_FILE_DIR)]

        langchain_model.add_documents(
            file_paths=TEST_FILES
        )

        sim_search = langchain_model.similarity_search(
            query="checks and balances", limit=5)

        self.assertIsInstance(sim_search, list)

        top_match = sim_search[0]
        self.assertIsInstance(top_match, Document)


if __name__ == '__main__':

    unittest.main()
