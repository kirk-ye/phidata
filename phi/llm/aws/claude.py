from typing import Optional, Dict, Any, List

from phi.llm.message import Message
from phi.llm.aws.bedrock import AwsBedrock
from phi.utils.log import logger


class Claude(AwsBedrock):
    name: str = "AwsBedrockAnthropicClaude"
    model: str = "anthropic.claude-3-sonnet-20240229-v1:0"
    # -*- Request parameters
    max_tokens: int = 8192
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    top_k: Optional[int] = None
    stop_sequences: Optional[List[str]] = None
    anthropic_version: str = "bedrock-2023-05-31"
    request_params: Optional[Dict[str, Any]] = None
    # -*- Client parameters
    client_params: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        _dict = super().to_dict()
        _dict["max_tokens"] = self.max_tokens
        _dict["temperature"] = self.temperature
        _dict["top_p"] = self.top_p
        _dict["top_k"] = self.top_k
        _dict["stop_sequences"] = self.stop_sequences
        return _dict

    @property
    def api_kwargs(self) -> Dict[str, Any]:
        _request_params: Dict[str, Any] = {
            "max_tokens": self.max_tokens,
            "anthropic_version": self.anthropic_version,
        }
        if self.temperature:
            _request_params["temperature"] = self.temperature
        if self.top_p:
            _request_params["top_p"] = self.top_p
        if self.top_k:
            _request_params["top_k"] = self.top_k
        if self.stop_sequences:
            _request_params["stop_sequences"] = self.stop_sequences
        if self.request_params:
            _request_params.update(self.request_params)
        return _request_params

    def get_request_body(self, messages: List[Message]) -> Dict[str, Any]:
        system_prompt = None
        messages_for_api = []
        for m in messages:
            if m.role == "system":
                system_prompt = m.content
            else:
                messages_for_api.append({"role": m.role, "content": m.content})

        # -*- Build request body
        request_body = {
            "messages": messages_for_api,
            **self.api_kwargs,
        }
        if system_prompt:
            request_body["system"] = system_prompt
        logger.info(f"Request body: {request_body}")
        return request_body

    def parse_response_message(self, response: Dict[str, Any]) -> Message:
        logger.debug(f"Response: {response}")
        logger.debug(f"Response type: {type(response)}")
        if response.get("type") == "message":
            response_message = Message(role=response.get("role"))
            if response.get("content"):
                response_message.content = response.get("content")

        return Message(
            role="assistant",
            content=response.get("completion"),
        )
