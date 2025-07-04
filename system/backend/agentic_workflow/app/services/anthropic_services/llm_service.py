from typing import Any, Dict, List, Optional

import httpx
from anthropic import AsyncAnthropic
from fastapi import Depends

from system.backend.agentic_workflow.app.config.settings import settings
from system.backend.agentic_workflow.app.repositories.llm_usage_repo import (
    LLMUsageRepository,
)
from system.backend.agentic_workflow.app.utils.logger import loggers


class JsonResponseError(Exception):
    """Custom exception for API response errors"""

    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.detail)


class AnthropicService:
    def __init__(self, llm_usage_repo: LLMUsageRepository = Depends()):
        """
        Initialize the Anthropic service

        :param api_key: Your Anthropic API key
        :param base_url: Base URL for Anthropic API
        :param default_model: Default model to use
        :param default_max_tokens: Default maximum tokens for responses
        :param default_temperature: Default temperature for responses
        """
        self.anthropic_api_key = settings.ANTHROPIC_API_KEY
        self.openai_api_key = settings.OPENAI_API_KEY
        self.anthropic_base_url = "https://api.anthropic.com/v1/messages"
        self.openai_base_url = "https://api.openai.com/v1/chat/completions"
        self.default_model = settings.ANTHROPIC_DEFAULT_MODEL
        self.openai_model = settings.OPENAI_DEFAULT_MODEL
        self.default_max_tokens = 55555
        self.default_temperature = 0.5
        self.llm_usage_repo = llm_usage_repo

        self.timeout = httpx.Timeout(
            connect=60.0,
            read=300.0,
            write=150.0,
            pool=60.0,
        )

        self.http_client = httpx.AsyncClient(verify=False)

    def _get_anthropic_headers(self) -> Dict[str, str]:
        """Get default headers for Anthropic API requests"""
        return {
            "x-api-key": self.anthropic_api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
            "anthropic-beta": "extended-cache-ttl-2025-04-11",
        }

    def _get_openai_headers(self) -> Dict[str, str]:
        """Get default headers for OpenAI API requests"""
        return {
            "Authorization": f"Bearer {self.openai_api_key}",
            "content-type": "application/json",
        }

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        web_search: bool = False,
        provider: str = "anthropic",
    ) -> Dict[str, Any]:
        """
        Generate text response from Claude or OpenAI

        :param prompt: The user prompt
        :param system_prompt: Optional system prompt
        :param web_search: Whether to use web search (only for Anthropic)
        :param provider: The provider to use ("anthropic" or "openai")
        :return: Full API response including usage data
        """
        if provider.lower() == "openai":
            return await self._make_openai_request(prompt, system_prompt)
        else:
            return await self._make_anthropic_request(
                prompt, system_prompt, web_search
            )

    async def generate_text_with_tools(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Generate text response from Claude with tool calling support

        :param messages: List of messages in the conversation
        :param system_prompt: Optional system prompt
        :param tools: List of tool definitions in Anthropic format
        :return: Full API response including tool calls and usage data
        """
        try:
            client = AsyncAnthropic(
                api_key=self.anthropic_api_key, http_client=self.http_client
            )

            # Prepare the stream parameters
            stream_params = {
                "temperature": self.default_temperature,
                "model": self.default_model,
                "max_tokens": self.default_max_tokens,
                "messages": messages,
            }

            # Add system prompt with caching if provided
            if system_prompt:
                stream_params["system"] = [
                    {"type": "text", "text": system_prompt}
                ]

            # Add tools if provided
            if tools:
                stream_params["tools"] = tools

            # Print payload being sent
            print("🔍 ANTHROPIC API PAYLOAD:")
            for key, value in stream_params.items():
                if isinstance(value, list):
                    print(f"  {key.capitalize()} Count: {len(value)}")
                    if key == "messages":
                        for i, message in enumerate(value):
                            print(f"    Message {i+1}: {message}")
                    elif key == "tools":
                        for i, tool in enumerate(value):
                            print(f"    Tool {i+1}: {tool.get('name', 'Unknown')} ({tool.get('type', 'Unknown type')})")
                else:
                    print(f"  {key.capitalize()}: {value}")
            print("=" * 50)

            collected_text = ""
            tool_calls = []

            async with client.messages.stream(**stream_params) as stream:
                async for text in stream.text_stream:
                    collected_text += text

                final_message = await stream.get_final_message()

                # Extract tool calls if any
                for content_block in final_message.content:
                    if content_block.type == "tool_use":
                        tool_call_data = {
                            "id": content_block.id,
                            "name": content_block.name,
                            "input": content_block.input,
                        }
                        tool_calls.append(tool_call_data)
                        
                        # Print tool call details
                        print(f"🔧 TOOL CALL DETECTED:")
                        print(f"  ID: {content_block.id}")
                        print(f"  Name: {content_block.name}")
                        print(f"  Arguments: {content_block.input}")
                        print("-" * 30)

                # Print summary
                print(f"📊 RESPONSE SUMMARY:")
                print(f"  Content Length: {len(collected_text)} characters")
                print(f"  Tool Calls: {len(tool_calls)}")
                print(f"  Stop Reason: {final_message.stop_reason}")
                print(f"  Usage: Input={final_message.usage.input_tokens}, Output={final_message.usage.output_tokens}")
                print("=" * 50)

                loggers["anthropic"].info(
                    f"Anthropic usage: {final_message.usage}"
                )
                await self.llm_usage_repo.add_llm_usage(final_message.usage)

                return {
                    "content": collected_text,
                    "tool_calls": tool_calls,
                    "usage": final_message.usage,
                    "stop_reason": final_message.stop_reason,
                    "final_message": final_message,
                }

        except Exception as exc:
            error_msg = f"Error in tool calling: {str(exc)}"
            loggers["anthropic"].error(error_msg)
            raise JsonResponseError(status_code=500, detail=error_msg)

    async def _make_anthropic_request(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        web_search: bool = False,
    ) -> Dict[str, Any]:
        """Make request to Anthropic API"""
        payload = {
            "model": self.default_model,
            "max_tokens": self.default_max_tokens,
            "temperature": self.default_temperature,
            "messages": [{"role": "user", "content": prompt}],
        }

        if system_prompt:
            payload["system"] = [{"type": "text", "text": system_prompt}]

        if web_search:
            payload["tools"] = [
                {
                    "type": "web_search_20250305",
                    "name": "web_search",
                    "max_uses": 2,
                }
            ]

        return await self._make_request(payload, "anthropic")

    async def _make_openai_request(
        self, prompt: str, system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Make request to OpenAI API"""
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.openai_model,
            "max_completion_tokens": self.default_max_tokens,
            "reasoning_effort": "low",
            "messages": messages,
        }

        return await self._make_request(payload, "openai")

    async def _make_request(
        self, payload: Dict[str, Any], provider: str
    ) -> Dict[str, Any]:
        """
        Make a API request to the specified provider

        :param payload: Request payload
        :param provider: The provider ("anthropic" or "openai")
        :return: API response text
        """
        try:
            if provider == "openai":
                base_url = self.openai_base_url
                headers = self._get_openai_headers()
            else:
                base_url = self.anthropic_base_url
                headers = self._get_anthropic_headers()

            async with httpx.AsyncClient(
                timeout=self.timeout, verify=False
            ) as client:
                try:
                    response = await client.post(
                        base_url, headers=headers, json=payload
                    )
                except Exception as e:
                    print(f"{str(e)}")
                response.raise_for_status()

                response_data = response.json()

                collected_text = ""
                if provider == "openai":
                    # Extract text from OpenAI Chat Completions response format
                    collected_text = response_data["choices"][0]["message"][
                        "content"
                    ]
                    usage_data = response_data["usage"]
                    loggers["openai"].info(f"OpenAI usage: {usage_data}")
                else:
                    # Extract text from Anthropic response format
                    collected_text = response_data["content"][-1]["text"]
                    usage_data = response_data["usage"]
                    loggers["anthropic"].info(f"Anthropic usage: {usage_data}")

                try:
                    await self.llm_usage_repo.add_llm_usage(usage_data)
                    print(f"✅ Usage data saved to database successfully")
                except Exception as e:
                    print(f"❌ Failed to save usage data to database: {str(e)}")
                    loggers[provider].error(
                        f"Database insertion failed: {str(e)}"
                    )

                return collected_text

        except httpx.RequestError as exc:
            error_msg = (
                f"An error occurred while requesting {exc.request.url!r}."
            )
            raise JsonResponseError(status_code=500, detail=error_msg)
        except httpx.HTTPStatusError as exc:
            error_msg = f"Error response {exc.response.status_code} while requesting {exc.request.url!r}."
            raise JsonResponseError(
                status_code=exc.response.status_code, detail=error_msg
            )
        except Exception as exc:
            error_msg = f"Unexpected error: {str(exc)}"
            raise JsonResponseError(status_code=500, detail=error_msg)

    async def anthropic_client_request(
        self, prompt: str, system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Make a request to the Anthropic API using the client with optional system prompt caching

        :param prompt: The user message
        :param system_prompt: Optional system prompt (will be cached if provided)
        :return: The response text
        """
        collected_text = ""

        client = AsyncAnthropic(
            api_key=self.anthropic_api_key, http_client=self.http_client
        )

        # Prepare the stream parameters
        stream_params = {
            "temperature": 0.25,
            "model": self.default_model,
            "max_tokens": self.default_max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }

        # Add system prompt with caching if provided
        if system_prompt:
            stream_params["system"] = [{"type": "text", "text": system_prompt}]

        async with client.messages.stream(**stream_params) as stream:

            async for text in stream.text_stream:
                collected_text += text
                # print(text, end="", flush=True)

            final_message = await stream.get_final_message()

            usage_data = {
                "input_tokens": final_message.usage.input_tokens,
                "output_tokens": final_message.usage.output_tokens,
                "cache_creation_input_tokens": final_message.usage.cache_creation_input_tokens,
                "cache_read_input_tokens": final_message.usage.cache_read_input_tokens,
            }

            loggers["anthropic"].info(f"Anthropic usage: {usage_data}")

            await self.llm_usage_repo.add_llm_usage(usage_data)

        return collected_text
