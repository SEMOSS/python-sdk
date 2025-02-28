import unittest
from ai_server.py_client.gaas.storage import StorageEngine
from test_base_connection import TestServerClient
from variables import STORAGE_ENGINE_ID


class StorageTests(TestServerClient):

    def test_storage_list(self):
        storage = StorageEngine(
            engine_id=STORAGE_ENGINE_ID,
        )

        storage_list = storage.list(storagePath='/my-new-test-folder/')

        self.assertIsInstance(storage_list, list)

        if len(storage_list) > 0:
            self.assertIsInstance(storage_list[0], str)

    def test_storage_list_details(self):
        storage = StorageEngine(
            engine_id=STORAGE_ENGINE_ID,
        )

        storage_list = storage.listDetails(storagePath='/my-new-test-folder/')

        self.assertIsInstance(storage_list, list)

        if len(storage_list) > 0:
            self.assertIsInstance(storage_list[0], dict)

            expected_keys = {'Path', 'Name', 'Size',
                             'MimeType', 'ModTime', 'IsDir', 'Tier'}

            self.assertCountEqual(storage_list[0].keys(), expected_keys)


if __name__ == '__main__':
    unittest.main()
