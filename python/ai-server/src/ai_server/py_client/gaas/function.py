from typing import Optional
import logging
from ai_server.server_resources.server_proxy import ServerProxy

logger: logging.Logger = logging.getLogger(__name__)


class FunctionEngine(ServerProxy):
    def __init__(self, engine_id: str, insight_id: Optional[str] = None):
        super().__init__()

        self.engine_id = engine_id
        self.insight_id = insight_id

        logger.info("FunctionEngine initialized with engine id " + engine_id)

    def execute(self, parameterMap: dict, insight_id: Optional[str] = None) -> None:
        """
        Connect to a function and execute

        Args:
            parameterMap (`dict`): A dictionary with the payload for the function engine
        """
        if insight_id is None:
            insight_id = self.insight_id

        pixel = (
            f'ExecuteFunctionEngine(engine = "{self.engine_id}", map=[{parameterMap}]);'
        )

        output_payload_message = self.server.run_pixel(
            payload=pixel, insight_id=insight_id, full_response=True
        )

        if output_payload_message["pixelReturn"][0]["operationType"] == ["ERROR"]:
            raise RuntimeError(output_payload_message["pixelReturn"][0]["output"])

        return output_payload_message["pixelReturn"][0]["output"]
