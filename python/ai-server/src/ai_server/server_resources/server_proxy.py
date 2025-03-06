from typing import List, Dict, Any, Optional, Generator

import logging
import threading

logger: logging.Logger = logging.getLogger(__name__)


class ServerProxy:
    """This class is used to transform model, database, storage and vector payloads into PayloadStructs before sending it to the RemoteEngineRunReactor via the runPixel endpoint"""

    def __init__(
        self,
    ):
        """
        Initialize the ServerProxy instance.
        """
        self.epoc = 0
        self.condition = threading.Condition()
        from ai_server.server_resources.server_client import ServerClient

        self.server = ServerClient.da_server
        assert (
            self.server is not None
        ), "Please authenticate using your access and secret keys"
        logger.info("Server is set")

    def get_next_epoc(self) -> str:
        """This method atomically increments the epoc count by one plus the current value."""
        self.epoc = self.epoc + 1
        return f"py_{self.epoc}"

    def comm(
        self,
        epoc: str,
        engine_type: str,
        engine_id: str,
        method_name: str,
        method_args: Optional[List[Any]] = [],
        method_arg_types: Optional[List[str]] = [],
        insight_id: Optional[str] = None,
    ) -> None:
        """
        This method in responsible for:
            - converting the args into a PayloadStruct
            - adds itself to the clients monitor block
            - forwards the PayloadStruct to the client to be sent to the Tomcat Server

        Args:
            epoc (`str`): The epoc ID for the payload struct
            engine_type (`str`): The engine type that will be called from the tomcat server. Options are model, storage, database or vector and are set in NativePyEngineWorker.java
            engine_id (`str`): The unique identifier of the engine being called. This passed so the tomcat server can call Utility.java to find the engine
            method_name (`str`): The IEngine method name that is available in the engine_type
            method_args (`Optional[List[Any]]`): A list of object to be sent to the IEngine method as inputs
            method_arg_types (`Optional[List[str]]`): A list of Java class names that represent the method args types
            insight_id (`Optional[str]`): The unique identifier for the insight

        Returns:
            `None`
        """

        # converts this into a PayloadStruct
        payload = {
            "epoc": epoc,
            "response": False,
            "engineType": engine_type,
            "interim": False,
            "objId": engine_id,  # all the method stuff will come here and below
            "methodName": method_name,
            "payload": method_args,
            "payloadClassNames": method_arg_types,
            "insightId": (
                insight_id if insight_id is not None else self.server.cur_insight
            ),
            "operation": "ENGINE",
        }

        # adds itself to the monitor block
        self.server.monitors.update({epoc: self.condition})
        logger.info("The server is ServerClient object")
        self.server.send_request(payload)

    def call(
        self,
        engine_type: str,
        engine_id: str,
        method_name: str = None,
        method_args: Optional[List[Any]] = [],
        method_arg_types: Optional[List[str]] = [],
        insight_id: Optional[str] = None,
    ) -> List[Dict]:
        """
        This method is responsible for initiating a synchronous communication with the server, which calls the `comm` method.

        Args:
            epoc (`str`): The epoc ID for the payload struct.
            engine_type (`str`): The engine type that will be called from the Tomcat server. Options are model, storage, database, or vector and are set in NativePyEngineWorker.java.
            engine_id (`str`): The unique identifier of the engine being called. This is passed so the Tomcat server can call Utility.java to find the engine.
            method_name (`str`): The IEngine method name that is available in the `engine_type`.
            method_args (`Optional[List[Any]]`): A list of objects to be sent to the IEngine method as inputs.
            method_arg_types (`Optional[List[str]]`): A list of Java class names that represent the method argument types.
            insight_id (`Optional[str]`): The unique identifier for the insight

        Returns:
            `List[Dict]`: A list that contains the response from the Tomcat server engine.
        """
        epoc = self.get_next_epoc()
        self.comm(
            epoc=epoc,
            engine_type=engine_type,
            engine_id=engine_id,
            method_name=method_name,
            method_args=method_args,
            method_arg_types=method_arg_types,
            insight_id=insight_id,
        )

        new_payload_struct = self.server.monitors.pop(epoc)
        logger.info(new_payload_struct)

        if "ex" in new_payload_struct:
            # if exception, convert it to an Exception and raise it
            raise Exception(new_payload_struct["ex"])
        else:
            logger.info(f"answer is .. {new_payload_struct['payload']}")
            return new_payload_struct["payload"]

    def process_payload(self, payload_struct):
        # try to see if the types are pickle
        # if so unpickle it
        import jsonpickle as jp

        payload_data = None
        if "payload" in payload_struct:
            payload_data = payload_struct["payload"]
        if payload_data is not None and isinstance(payload_data, List):
            for data in payload_data:
                index = payload_data.index(data)
                try:
                    orig_obj = data
                    obj = jp.loads(orig_obj)
                    payload_struct["payload"][index] = obj
                except Exception as e:
                    pass

        return payload_struct
