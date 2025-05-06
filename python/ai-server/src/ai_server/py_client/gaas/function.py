from typing import Optional, Any
import logging
import json
from ai_server.server_resources.server_proxy import ServerProxy

logger: logging.Logger = logging.getLogger(__name__)


class FunctionEngine(ServerProxy):

    def __init__(self, engine_id: str, insight_id: Optional[str] = None):
        super().__init__()

        self.engine_id = engine_id
        self.insight_id = insight_id

        logger.info("FunctionEngine initialized with engine id " + engine_id)

    def get_function_engine_id(self) -> str:
        return self.engine_id

    def execute(self, parameterMap: dict, insight_id: Optional[str] = None) -> None:
        """
        Connect to a function and execute

        Args:
            parameterMap (`dict`): A dictionary with the payload for the function engine
        """
        if insight_id is None:
            insight_id = self.insight_id

        pixel = f'ExecuteFunctionEngine(engine = "{self.engine_id}", map=[{json.dumps(parameterMap)}]);'

        output_payload_message = self.server.run_pixel(
            payload=pixel, insight_id=insight_id, full_response=True
        )

        if output_payload_message["pixelReturn"][0]["operationType"] == ["ERROR"]:
            raise RuntimeError(output_payload_message["pixelReturn"][0]["output"])

        return output_payload_message["pixelReturn"][0]["output"]

    # def to_langchain_tool(self):
    #     """Transform the function engine itno a langchain `BaseTool` object"""

    #     from langchain_core.tools import BaseTool

    #     class SemossFunctionTool(BaseTool):
    #         function_engine: FunctionEngine

    #         def __init__(self, function_engine: FunctionEngine):
    #             self.function_engine = function_engine

    #         def _run(self, parameterMap: dict, *args: Any, **kwargs: Any) -> Any:
    #             """Use the tool.

    #             Add run_manager: Optional[CallbackManagerForToolRun] = None
    #             to child implementations to enable tracing.
    #             """
    #             return self.function_engine.execute(parameterMap)

    #     return SemossFunctionTool()
