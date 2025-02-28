import unittest
from test_base_connection import TestServerClient


class TestRunPixel(TestServerClient):

    def test_server_connection(self):
        # Mock response from the server
        expected_response = 2

        # Test the server connection
        # Replace some_method with the actual method you're testing
        response = self.server_client.run_pixel('1+1')
        self.assertEqual(response, expected_response)


if __name__ == '__main__':
    unittest.main()
