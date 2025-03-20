import unittest
import os
from test_base_connection import TestServerClient
from ai_server.py_client.gaas.vector import VectorEngine

from ai_server.tests.variables import VECTOR_ENGINE_ID


class VectorTests(TestServerClient):

    vector_engine = None
    test_files = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.vector_engine = VectorEngine(
            engine_id=VECTOR_ENGINE_ID,
        )

        if cls.test_files is None:
            CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
            TEST_FILE_DIR = os.path.join(CURRENT_DIR, "test_files")
            # List files with full paths
            TEST_FILES = [os.path.join(TEST_FILE_DIR, file)
                          for file in os.listdir(TEST_FILE_DIR)]
            cls.test_files = TEST_FILES

    def test_vector_search(self):
        from pathlib import Path

        self.vector_engine.addDocument(
            file_paths=self.test_files
        )

        file_names = [Path(file).name for file in self.test_files]

        vector_search = self.vector_engine.nearestNeighbor(
            search_statement='How did the WHO improve access to oxygen supplies?',
            limit=5
        )

        # Assert that the response is a dictionary with specific keys
        self.assertIsInstance(vector_search, list)

        top_match = vector_search[0]
        self.assertIsInstance(top_match, dict)

        self.assertCountEqual(top_match.keys(), [
                              'Score', 'Source', 'Modality', 'Divider', 'Part', 'Tokens', 'Content'])

        self.vector_engine.removeDocument(file_names=file_names)

    def test_list_documents(self):

        document_info_list = self.vector_engine.listDocuments()

        self.assertIsInstance(document_info_list, list)

        if len(document_info_list) > 0:
            document_info = document_info_list[0]
            self.assertIsInstance(document_info, dict)
            self.assertIn('fileName', document_info)


if __name__ == '__main__':
    unittest.main()
