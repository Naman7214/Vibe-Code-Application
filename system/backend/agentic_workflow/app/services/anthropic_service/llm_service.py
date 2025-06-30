from typing import Any, Dict, Optional

import httpx
from anthropic import Anthropic
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
        self.api_key = settings.ANTHROPIC_API_KEY
        self.base_url = "https://api.anthropic.com/v1/messages"
        self.default_model = settings.ANTHROPIC_DEFAULT_MODEL
        self.default_max_tokens = 32768
        self.default_temperature = 0.2
        self.llm_usage_repo = llm_usage_repo

        self.timeout = httpx.Timeout(
            connect=60.0,
            read=300.0,
            write=150.0,
            pool=60.0,
        )

    def _get_headers(self) -> Dict[str, str]:
        """Get default headers for API requests"""
        return {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
            "anthropic-beta":"extended-cache-ttl-2025-04-11"
        }

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        web_search: bool = False,
    ) -> Dict[str, Any]:
        """
        Generate text response from Claude

        :param prompt: The user prompt
        :param system_prompt: Optional system prompt
        :return: Full API response including usage data
        """
        payload = {
            "model": self.default_model,
            "max_tokens": self.default_max_tokens,
            "temperature": self.default_temperature,
            "messages": [{"role": "user", "content": prompt}],
        }

        if system_prompt:
            payload["system"] = [
                {
                    "type": "text",
                    "text": system_prompt,
                    "cache_control": {"type": "ephemeral", "ttl": "1h"},
                }
            ]

        if web_search:
            payload["tools"] = [
                {
                    "type": "web_search_20250305",
                    "name": "web_search",
                    "max_uses": 2,
                }
            ]

        return await self._make_request(payload)

    async def _make_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a streaming API request and parse Server-Sent Events

        :param payload: Request payload
        :return: API response in the same format as non-streaming
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.base_url, headers=self._get_headers(), json=payload
                )
                response.raise_for_status()

                collected_text = response.json()["content"][-1]["text"]
                usage_data = response.json()["usage"]

                loggers["anthropic"].info(f"Anthropic usage: {usage_data}")
                print(collected_text)

                await self.llm_usage_repo.add_llm_usage(usage_data)

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

    async def anthropic_client_request(self, prompt: str) -> Dict[str, Any]:
        """
        Make a request to the Anthropic API using the client
        """
        collected_text = ""

        client = Anthropic(api_key=self.api_key)
        with client.messages.stream(
            model=self.default_model,
            max_tokens=self.default_max_tokens,
            temperature=self.default_temperature,
            messages=[{"role": "user", "content": prompt}],
            tools=[
                {
                    "type": "web_search_20250305",
                    "name": "web_search",
                    "max_uses": 2,
                }
            ],
        ) as stream:

            for text in stream.text_stream:
                collected_text += text
                print(text, end="", flush=True)

            final_message = stream.get_final_message()

            loggers["anthropic"].info(f"Anthropic usage: {final_message.usage}")

            await self.llm_usage_repo.add_llm_usage(final_message.usage)

        return collected_text