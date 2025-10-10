from typing import List, Optional, Dict, Union, Any, Generator
import warnings
import logging
import json
from ai_server.server_resources.server_proxy import ServerProxy

logger: logging.Logger = logging.getLogger(__name__)


class ModelEngine(ServerProxy):
    def __init__(self, engine_id: Optional[str], insight_id: Optional[str] = None):
        super().__init__()
        self.engine_id = engine_id
        self.insight_id = insight_id

        logger.info("ModelEngine initialized with engine id " + engine_id)

    def ask(
        self,
        command: Optional[str] = None,
        question: Optional[str] = None,  # Deprecated
        room_id: Optional[str] = None,
        context: Optional[str] = None,
        image: Optional[List] = None,
        url: Optional[List] = None,
        use_history: Optional[bool] = True,
        param_dict: Optional[Dict] = None,
        insight_id: Optional[str] = None,
    ) -> List[Dict]:
        """Sends a question to a text-generation model and returns the response.

        Args:
            - command (str): The command to send to the model.
            - question (str): **Deprecated**. Use `command` instead.
            - room_id (Optional[str]): Identifier for the room/conversation. If not provided, one will be created on the Java side.
            - context (Optional[str]): Context for the model (the system prompt).
            - image (Optional[List]): List of base64 image data to provide to the model.
            - url (Optional[List]): List of image URLs to provide to the model.
            - use_history (Optional[bool]): Whether to provide the conversation history to the model on an individual call.
            - param_dict (Optional[Dict]): A dictionary of additional parameters for the model,
                        such as temperature, max_new_tokens, etc.
                        *NOTE* you can pass in
                        param_dict = {"full_prompt":full_prompt, "temperature":temp, "max_new_tokens":max_token}
                        where full_prompt is the an multi faceted prompt construct before sending the payload
                        For OpenAI, this would be a list of dictionaris where the only keys within each dictionary are 'role' and 'content'
                        For TextGen, this could be a list simialr to OpenAI or a complete string that has all the pieces pre constructed
            - insight_id (Optional[str]): Identifier for insights.

        Returns:
            A list of dictionaries containing the model's response.

        Raises:
            RuntimeError: If the server returns an error.
        """
        if insight_id is None:
            insight_id = self.insight_id

        if question is not None:
            warnings.warn(
                "The 'question' parameter is deprecated and will be removed in a future version. "
                "Please use 'command' instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            if command is None:
                command = question

        command_param = (
            f', command="<encode>{command}</encode>"' if (command is not None) else ""
        )

        if (
            command_param == ""
            and param_dict is not None
            and not param_dict.get("full_prompt", None)
        ):
            raise ValueError("Either command or question must be provided")

        optional_room_id_param = (
            f', roomId="<encode>{room_id}</encode>"' if (room_id is not None) else ""
        )
        optional_context = (
            f', context=["<encode>{context}</encode>"]' if (context is not None) else ""
        )
        optional_param_dict = (
            f", paramValues=[{json.dumps(param_dict, ensure_ascii=False)}]"
            if (param_dict is not None)
            else ""
        )
        optional_image_param = f",image={image}" if (image is not None) else ""
        optional_url_param = f",url={url}" if (url is not None) else ""
        optional_use_history_param = (
            f", useHistory={str(use_history).lower()}"
            if (use_history is not None)
            else ""
        )

        pixel = f'LLM(engine="{self.engine_id}"{command_param}{optional_context}{optional_use_history_param}{optional_param_dict}{optional_room_id_param}{optional_image_param}{optional_url_param});'

        output_payload_message = self.server.run_pixel(
            payload=pixel, insight_id=insight_id, full_response=True
        )

        if output_payload_message["pixelReturn"][0]["operationType"] == ["ERROR"]:
            raise RuntimeError(output_payload_message["pixelReturn"][0]["output"])

        return output_payload_message["pixelReturn"][0]["output"]

    def stream_ask(
        self,
        command: Optional[str] = None,
        question: Optional[str] = None,  # Deprecated
        room_id: Optional[str] = None,
        context: Optional[str] = None,
        image: Optional[List] = None,
        url: Optional[List] = None,
        use_history: Optional[bool] = True,
        param_dict: Optional[Dict] = None,
        insight_id: Optional[str] = None,
    ) -> Generator:
        """Streams the response from a text-generation model.

        Args:
            - command (str): The command to send to the model.
            - question (str): **Deprecated**. Use `command` instead.
            - room_id (Optional[str]): Identifier for the room/conversation. If not provided, one will be created on the Java side.
            - context (Optional[str]): Context for the model (the system prompt).
            - image (Optional[List]): List of base64 image data to provide to the model.
            - url (Optional[List]): List of image URLs to provide to the model.
            - use_history (Optional[bool]): Whether to provide the conversation history to the model on an individual call.
            - param_dict (Optional[Dict]): A dictionary of additional parameters for the model,
                        such as temperature, max_new_tokens, etc.
                        *NOTE* you can pass in
                        param_dict = {"full_prompt":full_prompt, "temperature":temp, "max_new_tokens":max_token}
                        where full_prompt is the an multi faceted prompt construct before sending the payload
                        For OpenAI, this would be a list of dictionaris where the only keys within each dictionary are 'role' and 'content'
                        For TextGen, this could be a list simialr to OpenAI or a complete string that has all the pieces pre constructed
            - insight_id (Optional[str]): Identifier for insights.

        Yields:
            A generator that yields the model's response in chunks.

        Raises:
            RuntimeError: If the server returns an error.
        """
        if insight_id is None:
            insight_id = self.insight_id

        if question is not None:
            warnings.warn(
                "The 'question' parameter is deprecated and will be removed in a future version. "
                "Please use 'command' instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            if command is None:
                command = question

        command_param = (
            f', command="<encode>{command}</encode>"' if (command is not None) else ""
        )

        if (
            command_param == ""
            and param_dict is not None
            and not param_dict.get("full_prompt", None)
        ):
            raise ValueError("Either command or question must be provided")

        optional_room_id_param = (
            f', roomId="<encode>{room_id}</encode>"' if (room_id is not None) else ""
        )
        optional_context = (
            f', context=["<encode>{context}</encode>"]' if (context is not None) else ""
        )
        if param_dict is not None:
            param_dict["stream"] = True
        else:
            param_dict = {"stream": True}

        optional_param_dict = (
            f", paramValues=[{json.dumps(param_dict, ensure_ascii=False)}]"
        )

        optional_image_param = f",image={image}" if (image is not None) else ""
        optional_url_param = f",url={url}" if (url is not None) else ""
        optional_use_history_param = (
            f", useHistory={str(use_history).lower()}"
            if (use_history is not None)
            else ""
        )

        pixel = f'LLM(engine="{self.engine_id}"{command_param}{optional_context}{optional_use_history_param}{optional_param_dict}{optional_room_id_param}{optional_image_param}{optional_url_param});'

        for message in self.server.get_partial_responses(
            self.server.run_pixel_async(payload=pixel, insight_id=insight_id)
        ):
            if message and message.strip():
                yield message

    def embeddings(
        self,
        strings_to_embed: List[str],
        insight_id: Optional[str] = None,
        param_dict: Optional[Dict] = None,
    ) -> Dict:
        """Generates embeddings for a list of strings.

        Args:
            strings_to_embed: A list of strings to embed.
            insight_id: Optional; The unique identifier for the temporal workspace.
                        If None, the session's default insight_id is used.
            param_dict: Optional; A dictionary of additional parameters for the model.

        Returns:
            A dictionary containing the embeddings.

        Raises:
            RuntimeError: If the server returns an error.
        """
        if isinstance(strings_to_embed, str):
            strings_to_embed = [strings_to_embed]
        assert isinstance(strings_to_embed, list)

        if insight_id is None:
            if self.insight_id is None:
                insight_id = self.insight_id
            else:
                insight_id = self.server.cur_insight

        assert self.server is not None

        optionalParamDict = (
            f",paramValues=[{json.dumps(param_dict, ensure_ascii=False)}]"
            if (param_dict is not None)
            else ""
        )

        pixel = f'Embeddings(engine="{self.engine_id}", values={strings_to_embed}{optionalParamDict});'

        output_payload_message = self.server.run_pixel(
            payload=pixel, insight_id=insight_id, full_response=True
        )

        if output_payload_message["pixelReturn"][0]["operationType"] == ["ERROR"]:
            raise RuntimeError(output_payload_message["pixelReturn"][0]["output"])

        return output_payload_message["pixelReturn"][0]["output"]

    def get_model_engine_id(self) -> str:
        return self.engine_id

    def get_model_type(self) -> str:
        """Gets the model's API type.

        Returns:
            The model's API type (e.g., "OPEN_AI", "VERTEX").

        Raises:
            RuntimeError: If the server returns an error.
        """
        insight_id = self.insight_id
        pixel = f'GetModelAPI(model="{self.engine_id}");'

        output_payload_message = self.server.run_pixel(
            payload=pixel, insight_id=insight_id, full_response=True
        )

        if output_payload_message["pixelReturn"][0]["operationType"] == ["ERROR"]:
            raise RuntimeError(output_payload_message["pixelReturn"][0]["output"])

        return output_payload_message["pixelReturn"][0]["output"]

    def get_conversation_history(self, insight_id: Optional[str] = None) -> List[Dict]:
        """Gets the conversation history for a given insight.

        Args:
            insight_id: Optional; The unique identifier for the temporal workspace.
                        If None, the session's default insight_id is used.

        Returns:
            A list of dictionaries representing the conversation history.

        Raises:
            RuntimeError: If the server returns an error.
        """

        if insight_id is None:
            insight_id = self.insight_id

        pixel = f'GetRoomMessages(roomId="{insight_id}");'

        output_payload_message = self.server.run_pixel(
            payload=pixel, insight_id=insight_id, full_response=True
        )

        if output_payload_message["pixelReturn"][0]["operationType"] == ["ERROR"]:
            raise RuntimeError(output_payload_message["pixelReturn"][0]["output"])

        return output_payload_message["pixelReturn"][0]["output"]

    def to_langchain_embedder(self):
        """Transform the model engine into a langchain `Embeddings`object so that it can be used with langchain code"""

        from langchain_core.embeddings import Embeddings

        class SemossLangchainEmbeddingsModel(Embeddings):

            def __init__(self, modelEngine: ModelEngine):
                self.modelEngine = modelEngine

            def embed_documents(self, texts: List[str]) -> List[List[float]]:
                """Embed search docs."""
                return self.modelEngine.embeddings(strings_to_embed=texts)["response"]

            def embed_query(self, text: str) -> List[float]:
                return self.modelEngine.embeddings(strings_to_embed=[text])["response"][
                    0
                ]

        return SemossLangchainEmbeddingsModel(modelEngine=self)

    def to_langchain_chat_model(self):
        """Transform the model engine into a langchain `BaseChatModel` object so that it can be used with langchain code"""
        from langchain_core.language_models.chat_models import BaseChatModel
        from langchain_core.outputs import (
            ChatGeneration,
            ChatResult,
            ChatGenerationChunk,
        )
        from langchain_core.messages import (
            AIMessage,
            BaseMessage,
            HumanMessage,
            AIMessageChunk,
        )
        from collections.abc import Iterator
        from collections.abc import Sequence
        from langchain_core.tools import BaseTool
        from typing import Callable
        from langchain_core.runnables import Runnable
        from langchain_core.language_models.base import LanguageModelInput

        class SemossLangchainChatModel(BaseChatModel):
            engine_id: str
            model_engine: ModelEngine
            model_type: str

            # define the tools json
            tools: Sequence[
                Union[Dict[str, Any], type, Callable, BaseTool]  # noqa: UP006
            ]

            def __init__(self, model_engine: ModelEngine):
                data = {
                    "engine_id": model_engine.get_model_engine_id(),
                    "model_engine": model_engine,
                    "model_type": model_engine.get_model_type(),
                    "tools": [],
                }
                super().__init__(**data)

            def get_chat_history(
                self, insight_id: Optional[str] = None
            ) -> List[BaseMessage]:
                """Retrieve past conversation history and format it for Langchain."""

                # Fetch chat history from ModelEngine
                history = self.model_engine.get_conversation_history()
                messages = []
                for msg in sorted(history, key=lambda x: x["DATE_CREATED"]):
                    if msg["MESSAGE_TYPE"] == "INPUT":
                        messages.append(HumanMessage(content=msg["MESSAGE_DATA"]))
                    elif msg["MESSAGE_TYPE"] == "RESPONSE":
                        messages.append(AIMessage(content=msg["MESSAGE_DATA"]))
                return messages

            class Config:
                """Configuration for this pydantic object."""

                validate_by_name = True

            def _generate(
                self,
                messages: List[BaseMessage],
                stop: Optional[List[str]] = None,
                **kwargs: Any,
            ) -> ChatResult:
                """Top Level call"""
                history = self.get_chat_history()

                # Combine history with new messages (if history exists)
                full_messages = history + messages if history else messages

                # Convert to appropriate prompt format
                full_prompt = self.convert_messages_to_full_prompt(full_messages)

                param_dict = {**kwargs, **{"full_prompt": full_prompt}}
                if kwargs.get("tools") is not None:
                    # Convert tools to json string
                    processed_tools = self.convert_tools_to_list_dict(
                        kwargs.pop("tools")
                    )
                    param_dict["tools"] = processed_tools

                # Send the combined prompt to the model
                response = self.model_engine.ask(question="", param_dict=param_dict)

                return self._create_chat_result(response=response)

            def _create_chat_result(self, response: Dict[str, Any]) -> ChatResult:
                generations = []

                message = response.pop("response", "")
                generation_info = dict()
                if "logprobs" in response.keys():
                    generation_info["logprobs"] = response.pop("logprobs", {})

                # if this is a tool
                # need to do a different return

                if response["messageType"] == "TOOL":
                    tool_response = []
                    for m in message:
                        tool_response.append(
                            {
                                "id": m["id"],
                                "type": "function",
                                "function": {
                                    "arguments": m["arguments"],
                                    "name": m["name"],
                                },
                            }
                        )

                    gen = ChatGeneration(
                        message=AIMessage(
                            content="", additional_kwargs={"tool_calls": tool_response}
                        ),
                        generation_info=generation_info,
                    )
                else:
                    # if this is a normal message, just return the message
                    gen = ChatGeneration(
                        message=AIMessage(content=message),
                        generation_info=generation_info,
                    )

                generations.append(gen)

                return ChatResult(generations=generations, llm_output=response)

            def _stream(
                self, messages, stop=None, run_manager=None, **kwargs
            ) -> Iterator[ChatGenerationChunk]:
                """Top Level call"""
                history = self.get_chat_history()

                # Combine history with new messages (if history exists)
                full_messages = history + messages if history else messages

                # Convert to appropriate prompt format
                full_prompt = self.convert_messages_to_full_prompt(full_messages)

                # Remove non-serializable LangChain runtime keys
                filtered_kwargs = {
                    k: v
                    for k, v in kwargs.items()
                    if k not in {"callbacks", "run_manager"}
                }
                param_dict = {**filtered_kwargs, "full_prompt": full_prompt}
                if kwargs.get("tools") is not None:
                    # Convert tools to json string
                    processed_tools = self.convert_tools_to_list_dict(
                        kwargs.pop("tools")
                    )
                    param_dict["tools"] = processed_tools

                # Send the combined prompt to the model
                response = self.model_engine.stream_ask(
                    question="", param_dict=param_dict
                )

                for stream_message in response:
                    yield ChatGenerationChunk(
                        message=AIMessageChunk(content=stream_message)
                    )

            def convert_messages_to_full_prompt(
                self,
                messages: List[BaseMessage],
            ) -> Union[Dict[str, Any], str]:
                """Convert a LangChain message to a the correct response for a model.

                Args:
                    message: The LangChain message.

                Returns:
                    The `Dict` or `str` containing the message payload.
                """

                if self.model_type in ["OPEN_AI", "VERTEX"]:
                    # assume this is a chat based openai model, otherwise why would you call this
                    # class
                    full_prompt: List[Dict[str, Any]]
                    from langchain_community.adapters.openai import (
                        convert_message_to_dict,
                    )

                    full_prompt = [convert_message_to_dict(m) for m in messages]
                    return full_prompt
                else:
                    full_prompt: str
                    full_prompt = "\n".join([m.content for m in messages])
                    return full_prompt

            def convert_tools_to_list_dict(
                self, tools: Sequence[BaseTool]
            ) -> List[Dict]:
                """Convert a list of tools to a list of dicts

                Args:
                    tools: The list of tools to convert.

                Returns:
                    The dict containing the tools details
                """
                processed_tools_list = []
                for tool in tools:
                    tool_dict = {}
                    tool_dict["name"] = tool.name
                    tool_dict["description"] = tool.description
                    tool_params = {}
                    for args_name in tool.args.keys():
                        arg_map = {}
                        arg_map["description"] = tool.args[args_name]["title"]
                        arg_map["type"] = tool.args[args_name]["type"]
                        tool_params[args_name] = arg_map
                    tool_dict["parameters"] = {
                        "type": "object",
                        "properties": tool_params,
                        "required": list(tool.args.keys()),
                    }
                    tool_dict["type"] = "function"
                    processed_tools_list.append(
                        {"type": "function", "function": tool_dict}
                    )

                return processed_tools_list

            def bind_tools(
                self,
                tools: Sequence[
                    Union[Dict[str, Any], type, Callable, BaseTool]  # noqa: UP006
                ],
                *,
                tool_choice: Optional[Union[str]] = None,
                **kwargs: Any,
            ) -> Runnable[LanguageModelInput, BaseMessage]:
                """Bind tools to the model.

                Args:
                    tools: Sequence of tools to bind to the model.
                    tool_choice: The tool to use. If "any" then any tool can be used.

                Returns:
                    A Runnable that returns a message.
                """
                from langchain_core.runnables import RunnableBinding

                runnable_binding = RunnableBinding(
                    bound=self,
                    kwargs={"tools": tools},  # <-- Note the additional kwargs
                )
                return runnable_binding

            @property
            def _llm_type(self) -> str:
                """Return type of chat model."""
                return "SEMOSS"

        return SemossLangchainChatModel(model_engine=self)
