import os
import tempfile
import unittest
import uuid

from ai_server.py_client.gaas.storage import StorageEngine
from test_base_connection import TestServerClient
from variables import STORAGE_ENGINE_ID

# every entry a listing hands back carries these, whether it is a file or a folder
LISTING_KEYS = {'Path', 'Name', 'Size', 'MimeType', 'ModTime', 'IsDir', 'Metadata'}

# what a sync reports when it finishes
SYNC_STATUS_KEYS = {'storagePath', 'status',
                    'uploadedFiles', 'skippedFiles', 'failedFiles'}


class StorageTests(TestServerClient):

    storage = None
    # each run works in its own folder so a failed run cannot leave anything
    # behind that the next one trips over
    test_folder = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.storage = StorageEngine(
            engine_id=STORAGE_ENGINE_ID,
        )
        cls.test_folder = f"sdk-tests/{uuid.uuid4()}"

    @classmethod
    def tearDownClass(cls):
        try:
            cls.storage.deleteFromStorage(storagePath=cls.test_folder)
        except RuntimeError as e:
            # not worth failing the run over, but say so rather than leaving
            # someone to wonder where the folder came from
            print(f"Could not clean up {cls.test_folder}: {e}")

    def _write_local_files(self, directory, names):
        """Writes a file per name and returns their full paths."""
        paths = []
        for name in names:
            path = os.path.join(directory, name)
            with open(path, 'w') as f:
                f.write(f"contents of {name}")
            paths.append(path)
        return paths

    def test_storage_list(self):
        storage_list = self.storage.list(storagePath="/")

        self.assertIsInstance(storage_list, list)

        if len(storage_list) > 0:
            self.assertIsInstance(storage_list[0], str)

    def test_storage_list_details(self):
        storage_list = self.storage.listDetails(storagePath="/")

        self.assertIsInstance(storage_list, list)

        if len(storage_list) > 0:
            self.assertIsInstance(storage_list[0], dict)
            self.assertCountEqual(storage_list[0].keys(), LISTING_KEYS)

    def test_storage_copy_round_trip(self):
        with tempfile.TemporaryDirectory() as local_dir:
            [local_file] = self._write_local_files(local_dir, ['round-trip.txt'])
            storage_path = f"{self.test_folder}/copy"

            self.storage.copyToStorage(
                storagePath=storage_path, localPath=local_file)

            details = self.storage.listDetails(storagePath=storage_path)
            names = [item['Name'] for item in details]
            self.assertIn('round-trip.txt', names)
            self.assertCountEqual(details[0].keys(), LISTING_KEYS)

        # pull it back into a fresh directory so we know it really came down
        with tempfile.TemporaryDirectory() as download_dir:
            self.storage.copyToLocal(
                storagePath=f"{storage_path}/round-trip.txt",
                localPath=download_dir,
            )
            self.assertIn('round-trip.txt', os.listdir(download_dir))

    def test_storage_sync_reports_status(self):
        storage_path = f"{self.test_folder}/sync"

        with tempfile.TemporaryDirectory() as local_dir:
            self._write_local_files(local_dir, ['a.txt', 'b.txt'])

            status = self.storage.syncLocalToStorage(
                storagePath=storage_path, localPath=local_dir)

            self.assertIsInstance(status, dict)
            self.assertCountEqual(status.keys(), SYNC_STATUS_KEYS)
            self.assertEqual(status['status'], 'SUCCESS')
            self.assertEqual(status['failedFiles'], [])
            self.assertEqual(len(status['uploadedFiles']), 2)
            self.assertEqual(status['skippedFiles'], [])

            # nothing changed locally, so a second sync should upload none of it
            second = self.storage.syncLocalToStorage(
                storagePath=storage_path, localPath=local_dir)

            self.assertEqual(second['status'], 'SUCCESS')
            self.assertEqual(second['uploadedFiles'], [])
            self.assertEqual(len(second['skippedFiles']), 2)

    def test_storage_sync_to_local(self):
        storage_path = f"{self.test_folder}/down"

        with tempfile.TemporaryDirectory() as local_dir:
            self._write_local_files(local_dir, ['c.txt', 'd.txt'])
            self.storage.syncLocalToStorage(
                storagePath=storage_path, localPath=local_dir)

        with tempfile.TemporaryDirectory() as download_dir:
            self.storage.syncStorageToLocal(
                storagePath=storage_path, localPath=download_dir)

            self.assertCountEqual(os.listdir(download_dir), ['c.txt', 'd.txt'])

    def test_storage_metadata(self):
        storage_path = f"{self.test_folder}/metadata"

        with tempfile.TemporaryDirectory() as local_dir:
            [local_file] = self._write_local_files(local_dir, ['tagged.txt'])
            self.storage.copyToStorage(
                storagePath=storage_path,
                localPath=local_file,
                metadata={'author': 'sdk-tests'},
            )

        details = self.storage.listDetails(storagePath=storage_path)
        tagged = next(item for item in details if item['Name'] == 'tagged.txt')

        # SMB/CIFS and SFTP have nowhere to keep metadata, so only assert on it
        # when the engine actually kept some
        if tagged['Metadata']:
            self.assertEqual(tagged['Metadata'].get('author'), 'sdk-tests')

            self.storage.updateFileMetadata(
                storagePath=f"{storage_path}/tagged.txt",
                metadata={'author': 'someone-else'},
            )

            updated = self.storage.listDetails(storagePath=storage_path)
            tagged = next(
                item for item in updated if item['Name'] == 'tagged.txt')
            # the update replaces the metadata rather than merging into it
            self.assertEqual(tagged['Metadata'].get('author'), 'someone-else')

    def test_storage_delete_does_not_reach_siblings(self):
        """A delete of "dir" must not take "dir-other" with it."""
        storage_path = f"{self.test_folder}/delete-me"
        sibling_path = f"{self.test_folder}/delete-me-not"

        with tempfile.TemporaryDirectory() as local_dir:
            [local_file] = self._write_local_files(local_dir, ['file.txt'])
            self.storage.copyToStorage(
                storagePath=storage_path, localPath=local_file)
            self.storage.copyToStorage(
                storagePath=sibling_path, localPath=local_file)

        self.storage.deleteFromStorage(storagePath=storage_path)

        survivors = [item['Name']
                     for item in self.storage.listDetails(storagePath=sibling_path)]
        self.assertIn('file.txt', survivors)


if __name__ == '__main__':
    unittest.main()
