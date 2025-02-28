import unittest

from ai_server.server_resources.server_client import ServerClient

from test_base_connection import TestServerClient
from test_run_pixel import TestRunPixel
from test_model import ModelTests
from test_vector import VectorTests
from test_database import DatabaseTests
from test_openai_endpoints import OpenAiEndpointsTests
from test_langchain import LangChainTests
from test_storage import StorageTests
from variables import ACCESS_KEY, SECRET_KEY, ENDPOINT


if __name__ == '__main__':
    test_loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()

    TestServerClient.server_client = ServerClient(
        base=ENDPOINT,
        access_key=ACCESS_KEY,
        secret_key=SECRET_KEY
    )

    run_pixel_test = test_loader.loadTestsFromTestCase(TestRunPixel)
    test_suite.addTest(run_pixel_test)

    model_tests = test_loader.loadTestsFromTestCase(ModelTests)
    test_suite.addTest(model_tests)

    vector_tests = test_loader.loadTestsFromTestCase(VectorTests)
    test_suite.addTest(vector_tests)

    database_tests = test_loader.loadTestsFromTestCase(DatabaseTests)
    test_suite.addTest(database_tests)

    openai_endpoint_tests = test_loader.loadTestsFromTestCase(
        OpenAiEndpointsTests)
    test_suite.addTest(openai_endpoint_tests)

    langchain_tests = test_loader.loadTestsFromTestCase(LangChainTests)
    test_suite.addTest(langchain_tests)

    # No great way to run storage tests locally yet
    if ENDPOINT != "http://localhost:9090/Monolith_Dev/api":
        storage_tests = test_loader.loadTestsFromTestCase(StorageTests)
        test_suite.addTest(storage_tests)

    # run tests
    unittest.TextTestRunner(verbosity=2).run(test_suite)
