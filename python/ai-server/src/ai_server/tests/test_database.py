import unittest
import pandas as pd
from ai_server.py_client.gaas.database import DatabaseEngine
from test_base_connection import TestServerClient
from variables import DATABASE_ENGINE_ID


class DatabaseTests(TestServerClient):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.db_engine = DatabaseEngine(
            engine_id=DATABASE_ENGINE_ID,
        )

    def test_db_query(self):
        db_pandas = self.db_engine.execQuery('select * from diabetes')

        # Assert that the response is a dictionary with specific keys
        self.assertIsInstance(db_pandas, pd.DataFrame)


if __name__ == '__main__':
    unittest.main()
