import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import requests

from ai_server.py_client.gaas.vector import VectorEngine
from ai_server.server_resources.server_client import ServerClient


class FakeResponse:
    def __init__(self, payload, error=None):
        self.payload = payload
        self.error = error

    def raise_for_status(self):
        if self.error is not None:
            raise self.error

    def json(self):
        return self.payload


class UploadBatchingTests(unittest.TestCase):
    def setUp(self):
        self.client = object.__new__(ServerClient)
        self.client.main_url = "https://example.test/Monolith/api"
        self.client.cur_insight = "insight-current"
        self.client.cookies = {}
        self.client.required_headers = {"X-Test": "true"}
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)

    def files(self, count):
        paths = []
        for index in range(count):
            path = Path(self.temporary_directory.name) / f"file-{index}.txt"
            path.write_text(f"file {index}", encoding="utf-8")
            paths.append(str(path))
        return paths

    def test_upload_files_batches_four_and_preserves_response_order(self):
        paths = self.files(9)
        request_groups = []
        opened_handles = []

        def post(url, *, cookies, files, headers):
            self.assertIn("insightId=insight-current", url)
            self.assertEqual(cookies, {})
            self.assertEqual(headers, {"X-Test": "true"})
            self.assertTrue(all(field == "file" for field, _handle in files))
            handles = [handle for _field, handle in files]
            self.assertTrue(all(not handle.closed for handle in handles))
            request_groups.append([Path(handle.name).name for handle in handles])
            opened_handles.extend(handles)
            return FakeResponse([{"fileName": f"remote/{Path(handle.name).name}"} for handle in handles])

        with patch("ai_server.server_resources.server_client.requests.post", side_effect=post):
            uploaded = self.client.upload_files(paths, batch_size=4)

        self.assertEqual([len(group) for group in request_groups], [4, 4, 1])
        self.assertEqual(uploaded, [f"remote/file-{index}.txt" for index in range(9)])
        self.assertTrue(all(handle.closed for handle in opened_handles))

    def test_upload_files_keeps_one_file_requests_by_default(self):
        paths = self.files(3)
        group_sizes = []

        def post(url, *, cookies, files, headers):
            del url, cookies, headers
            group_sizes.append(len(files))
            return FakeResponse([{"fileName": Path(files[0][1].name).name}])

        with patch("ai_server.server_resources.server_client.requests.post", side_effect=post):
            uploaded = self.client.upload_files(paths)

        self.assertEqual(group_sizes, [1, 1, 1])
        self.assertEqual(uploaded, ["file-0.txt", "file-1.txt", "file-2.txt"])

    def test_upload_files_validates_all_inputs_before_first_request(self):
        existing = self.files(1)[0]
        missing = str(Path(self.temporary_directory.name) / "missing.txt")
        post = Mock()

        with patch("ai_server.server_resources.server_client.requests.post", post):
            with self.assertRaises(FileNotFoundError):
                self.client.upload_files([existing, missing], batch_size=4)
            with self.assertRaises(ValueError):
                self.client.upload_files([existing], batch_size=0)
            with self.assertRaises(ValueError):
                self.client.upload_files([existing], batch_size=True)

        post.assert_not_called()

    def test_upload_files_raises_for_http_failure_and_closes_handles(self):
        paths = self.files(4)
        opened_handles = []

        def post(url, *, cookies, files, headers):
            del url, cookies, headers
            opened_handles.extend(handle for _field, handle in files)
            return FakeResponse([], requests.HTTPError("upload failed"))

        with patch("ai_server.server_resources.server_client.requests.post", side_effect=post):
            with self.assertRaises(requests.HTTPError):
                self.client.upload_files(paths, batch_size=4)

        self.assertTrue(all(handle.closed for handle in opened_handles))

    def test_upload_files_rejects_malformed_responses_and_closes_handles(self):
        paths = self.files(2)
        malformed_payloads = ([{"fileName": "only-one"}], [{"fileName": "one"}, {}])
        for payload in malformed_payloads:
            with self.subTest(payload=payload):
                opened_handles = []

                def post(url, *, cookies, files, headers):
                    del url, cookies, headers
                    opened_handles.extend(handle for _field, handle in files)
                    return FakeResponse(payload)

                with patch("ai_server.server_resources.server_client.requests.post", side_effect=post):
                    with self.assertRaises(ValueError):
                        self.client.upload_files(paths, batch_size=2)
                self.assertTrue(all(handle.closed for handle in opened_handles))

    def test_vector_add_document_forwards_upload_batch_size(self):
        class FakeServer:
            cur_insight = "insight-current"

            def __init__(self):
                self.upload_arguments = None

            def upload_files(self, **kwargs):
                self.upload_arguments = kwargs
                return ["remote/one.txt", "remote/two.txt"]

            def run_pixel(self, **kwargs):
                return {"pixelReturn": [{"operationType": ["OPERATION"], "output": True}]}

        fake_server = FakeServer()
        original = ServerClient.da_server
        ServerClient.da_server = fake_server
        self.addCleanup(setattr, ServerClient, "da_server", original)
        engine = VectorEngine("vector-1", insight_id="insight-current")

        result = engine.addDocument(
            ["one.txt", "two.txt"],
            insight_id="insight-current",
            upload_batch_size=4,
        )

        self.assertTrue(result)
        self.assertEqual(
            fake_server.upload_arguments,
            {
                "files": ["one.txt", "two.txt"],
                "insight_id": "insight-current",
                "batch_size": 4,
            },
        )


if __name__ == "__main__":
    unittest.main()
