from typing import List, Optional, Dict, Union, Any, Generator
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
        question: str,
        context: Optional[str] = None,
        insight_id: Optional[str] = None,
        param_dict: Optional[Dict] = None,
    ) -> List[Dict]:
        """
        Ask a question to a text-generation model hosted on the ai server.

        Args:
            question (`str`):
                The single string question you are asking a an LLM
            context (`str`):
                Set the given context string for an interaction with an LLM
            insight_id (`str`):
                Unique identifier for the temporal worksapce where actions are being isolated
            param_dict (`dict`):
                Additional inference params like temperature, max new tokens and top_k etc

                *NOTE* you can pass in
                param_dict = {"full_prompt":full_prompt, "temperature":temp, "max_new_tokens":max_token}
                where full_prompt is the an multi faceted prompt construct before sending the payload

                For OpenAI, this would be a list of dictionaris where the only keys within each dictionary are 'role' and 'content'
                For TextGen, this could be a list simialr to OpenAI or a complete string that has all the pieces pre constructed
        Response:
            `Union[Dict, Generator]`: A list that contains a dictioanry with the answer to the question, insight id and the message id
        """
        if insight_id is None:
            insight_id = self.insight_id

        optionalContext = (
            f',context=["<encode>{context}</encode>"]' if (context is not None) else ""
        )
        optionalParamDict = (
            f",paramValues=[{json.dumps(param_dict)}]"
            if (param_dict is not None)
            else ""
        )

        pixel = f'LLM(engine="{self.engine_id}", command="<encode>{question}</encode>"{optionalContext}{optionalParamDict});'

        output_payload_message = self.server.run_pixel(
            payload=pixel, insight_id=insight_id, full_response=True
        )

        if output_payload_message["pixelReturn"][0]["operationType"] == ["ERROR"]:
            raise RuntimeError(output_payload_message["pixelReturn"][0]["output"])

        return output_payload_message["pixelReturn"][0]["output"]

    def stream_ask(
        self,
        question: str,
        context: Optional[str] = None,
        insight_id: Optional[str] = None,
        param_dict: Optional[Dict] = None,
    ) -> Generator:
        """
        Stream responses from a question asked to a text-generation model hosted on the ai server.

        Args:
            question (`str`):
                The single string question you are asking a an LLM
            context (`str`):
                Set the given context string for an interaction with an LLM
            insight_id (`str`):
                Unique identifier for the temporal worksapce where actions are being isolated
            param_dict (`dict`):
                Additional inference params like temperature, max new tokens and top_k etc

                *NOTE* you can pass in
                param_dict = {"full_prompt":full_prompt, "temperature":temp, "max_new_tokens":max_token}
                where full_prompt is the an multi faceted prompt construct before sending the payload

                For OpenAI, this would be a list of dictionaris where the only keys within each dictionary are 'role' and 'content'
                For TextGen, this could be a list simialr to OpenAI or a complete string that has all the pieces pre constructed
        Response:
            `Generator`: A generator to iterate through to get the partial responses
        """
        if insight_id is None:
            insight_id = self.insight_id

        optionalContext = (
            f',context=["<encode>{context}</encode>"]' if (context is not None) else ""
        )
        optionalParamDict = (
            f",paramValues=[{json.dumps(param_dict)}]"
            if (param_dict is not None)
            else ""
        )

        pixel = f'LLM(engine="{self.engine_id}", command="<encode>{question}</encode>"{optionalContext}{optionalParamDict});'

        for message in self.server.get_partial_responses(
            self.server.run_pixel_separate_thread(
                payload=pixel, insight_id=insight_id, full_response=True
            )
        ):
            yield message

    def embeddings(
        self,
        strings_to_embed: List[str],
        insight_id: Optional[str] = None,
        param_dict: Optional[Dict] = None,
    ) -> Dict:
        """
        Pass in a list of strings to an embeddings model and get a list of vectors.

        Args:
            question (`str`):
                A user's access key is a unique identifier used for authentication and authorization. It will allow users or applications to access specific resources or perform designated actions within an ai-server instance.
            insight_id (`str`):
                Unique identifier for the temporal worksapce where actions are being isolated
            param_dict (`dict`):
                Optional

        Returns

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
            f",paramValues=[{json.dumps(param_dict)}]"
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

        insight_id = self.insight_id
        pixel = f'GetModelAPI(model="{self.engine_id}");'

        output_payload_message = self.server.run_pixel(
            payload=pixel, insight_id=insight_id, full_response=True
        )

        return output_payload_message["pixelReturn"][0]["output"]

    def to_langchain_embedder(self):
        """Transform the model engine into a langchain `Embeddings`object so that it can be used with langchain code"""

        from langchain_core.embeddings import Embeddings

        class CfgEmbeddingsEngine(Embeddings):
            def __init__(self, modelEngine):
                self.modelEngine = modelEngine

            def embed_documents(self, texts: List[str]) -> List[List[float]]:
                """Embed search docs."""
                return self.modelEngine.embeddings(strings_to_embed=texts)[0][
                    "response"
                ]

            def embed_query(self, text: str) -> List[float]:
                return self.modelEngine.embeddings(strings_to_embed=[text])[0][
                    "response"
                ][0]

        return CfgEmbeddingsEngine(modelEngine=self)

    def to_langchain_chat_model(self):
        """Transform the model engine into a langchain `BaseChatModel` object so that it can be used with langchain code"""
        from langchain_core.language_models.chat_models import BaseChatModel
        from langchain_core.outputs import (
            ChatGeneration,
            ChatResult,
        )
        from langchain_core.messages import (
            AIMessage,
            BaseMessage,
        )

        class ChatCfgAI(BaseChatModel):
            engine_id: str
            model_engine: ModelEngine
            model_type: str

            def __init__(self, model_engine):
                data = {
                    "engine_id": model_engine.get_model_engine_id(),
                    "model_engine": model_engine,
                    "model_type": model_engine.get_model_type(),
                }

                super().__init__(**data)

            class Config:
                """Configuration for this pydantic object."""

                allow_population_by_field_name = True

            def _generate(
                self,
                messages: List[BaseMessage],
                stop: Optional[List[str]] = None,
                **kwargs: Any,
            ) -> ChatResult:
                """Top Level call"""
                full_prompt = self.convert_messages_to_full_prompt(messages)
                response = self.model_engine.ask(
                    question="", param_dict={**kwargs, **{"full_prompt": full_prompt}}
                )

                return self._create_chat_result(response=response)

            def _create_chat_result(self, response: Dict[str, Any]) -> ChatResult:
                generations = []

                message = response.pop("response", "")
                generation_info = dict()
                if "logprobs" in response.keys():
                    generation_info["logprobs"] = response.pop("logprobs", {})
                gen = ChatGeneration(
                    message=AIMessage(content=message),
                    generation_info=generation_info,
                )

                generations.append(gen)

                return ChatResult(generations=generations, llm_output=response)

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

            @property
            def _llm_type(self) -> str:
                """Return type of chat model."""
                return "CFG AI"

        return ChatCfgAI(model_engine=self)
