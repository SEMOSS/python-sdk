from typing import Optional
import logging
from ai_server.server_resources.server_proxy import ServerProxy

logger: logging.Logger = logging.getLogger(__name__)


class DatabaseEngine(ServerProxy):
    def __init__(self, engine_id: str, insight_id: Optional[str] = None):
        super().__init__()

        self.engine_id = engine_id
        self.insight_id = insight_id

        logger.info("DatabaseEngine initialized with engine id " + engine_id)

    def execQuery(
        self,
        query: str,
        insight_id: Optional[str] = None,
        return_pandas: Optional[bool] = True,
        server_output_format: Optional[str] = "json",
    ):
        """
        Connect to a database an execute SQL against it to create a pandas frame

        Args:
            query (`str`):
                A user's access key is a unique identifier used for authentication and authorization. It will allow users or applications to access specific resources or perform designated actions within an ai-server instance.
            insight_id (`str`):
                Unique identifier for the temporal worksapce where actions are being isolated
            return_pandas (`bool`):
                true/false flag for creating a pandas frame
            server_output_format (`str`):
                Define wheter to write the query result to a file or json. *Note*, if file is selected then its only accessible via server UI
        """
        if insight_id is None:
            insight_id = self.insight_id

        fileLoc = super().call(
            engine_type="database",
            engine_id=self.engine_id,
            insight_id=insight_id,
            method_name="execQuery",
            method_args=[query, server_output_format],
            method_arg_types=["java.lang.String", "java.lang.String"],
        )

        if isinstance(fileLoc, list) and len(fileLoc) > 0:
            fileLoc = fileLoc[0]

        if return_pandas:
            logger.info(f"The output is {fileLoc}")
            import pandas as pd

            logger.info(fileLoc)
            if isinstance(fileLoc, dict) and len(fileLoc) > 0:
                rows = []
                # saftey check based on how java gson structure the response
                if "myArrayList" in fileLoc.keys() and {
                    rows.append(d[key]) if key == "map" else "notMap"
                    for d in fileLoc["myArrayList"]
                    for key in d.keys()
                } == {None}:
                    return pd.DataFrame.from_dict(rows)
            elif isinstance(fileLoc, str):
                return pd.read_json(fileLoc)
            else:
                return fileLoc
        else:
            if isinstance(fileLoc, dict) and len(fileLoc) > 0:
                return fileLoc
            else:
                return open(fileLoc, "r").read()

    def insertData(
        self, query: str, insight_id: Optional[str] = None, commit: bool = True
    ) -> None:
        """
        Connect to a database an execute SQL against it to insert data

        Args:
            query (`str`): A SQL statement to insert values into a table
            insight_id (`Optional[str]`): Unique identifier for the temporal worksapce where actions are being isolated
            commit (`bool`): commit to the database if autocommit is false. default is true
        """
        return self.runQuery(query, insight_id, commit)

    def updateData(
        self, query: str, insight_id: Optional[str] = None, commit: bool = True
    ) -> None:
        """
        Connect to a database an execute SQL against it to update data

        Args:
            query (`str`): A SQL statement to insert values into a table
            insight_id (`Optional[str]`): Unique identifier for the temporal worksapce where actions are being isolated
            commit (`bool`): commit to the database if autocommit is false. default is true
        """
        return self.runQuery(query, insight_id, commit)

    def removeData(
        self, query: str, insight_id: Optional[str] = None, commit: bool = True
    ) -> None:
        """
        Connect to a database an execute SQL against it to delete/remove data

        Args:
            query (`str`): A SQL statement like DELETE FROM diab WHERE age=19
            insight_id (`Optional[str]`): Unique identifier for the temporal worksapce where actions are being isolated
            commit (`bool`): commit to the database if autocommit is false. default is true
        """
        return self.runQuery(query, insight_id, commit)

    def runQuery(
        self, query: str, insight_id: Optional[str] = None, commit: bool = True
    ):
        """
        This will execute the ExecQuery() reactor for a database

        Args:
        query (`str`): A SQL statement like DELETE FROM diab WHERE age=19
        insight_id (`Optional[str]`): Unique identifier for the temporal worksapce where actions are being isolated
        """

        if insight_id is None:
            insight_id = self.insight_id

        commitStr = "true" if commit else "false"

        pixel = f'Database(database = "{self.engine_id}")|Query("<encode>{query}</encode>")|ExecQuery(commit={commitStr});'

        output_payload_message = self.server.run_pixel(
            payload=pixel, insight_id=insight_id, full_response=True
        )

        if output_payload_message["pixelReturn"][0]["operationType"] == ["ERROR"]:
            raise RuntimeError(output_payload_message["pixelReturn"][0]["output"])

        return output_payload_message["pixelReturn"][0]["output"]

    def to_langchain_database(self):
        """Transform the database engine into a langchain BaseRetriever object so that it can be used with langchain code"""
        from langchain_core.retrievers import BaseRetriever

        class SemossLangchainDatabase(BaseRetriever):
            engine_id: str
            database_engine: DatabaseEngine
            insight_id: Optional[str]

            def __init__(self, database_engine: DatabaseEngine):
                """Initialize with the provided database engine."""
                data = {
                    "engine_id": database_engine.engine_id,
                    "insight_id": database_engine.insight_id,
                    "database_engine": database_engine,
                }
                super().__init__(**data)

            class Config:
                """Configuration for this pydantic object."""

                validate_by_name = True

            def executeQuery(self, query: str) -> any:
                """Execute a query on the database."""
                return self.database_engine.execQuery(query=query)

            def insertQuery(self, query: str) -> any:
                """Insert data into the database."""
                return self.database_engine.insertData(query=query)

            def updateQuery(self, query: str) -> any:
                """Update data in the database."""
                return self.database_engine.updateData(query=query)

            def removeQuery(self, query: str) -> any:
                """Remove data from the database."""
                return self.database_engine.removeData(query=query)

            def _get_relevant_documents(self) -> str:
                """Retrieve relevant documents from the database."""
                return "SQL Operations"

        return SemossLangchainDatabase(database_engine=self)
