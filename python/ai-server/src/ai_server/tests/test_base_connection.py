import unittest
from ai_server.server_resources.server_client import ServerClient
from variables import ACCESS_KEY, SECRET_KEY, ENDPOINT


class TestServerClient(unittest.TestCase):

    server_client = None

    @classmethod
    def setUpClass(cls):
        # Create an instance of ServerClient for testing
        if cls.server_client is None:
            cls.server_client = TestServerClient.login_with_access_keys()

    @staticmethod
    def login_with_access_keys():
        return ServerClient(
            base=ENDPOINT,
            access_key=ACCESS_KEY,
            secret_key=SECRET_KEY
        )


if __name__ == '__main__':
    unittest.main()
