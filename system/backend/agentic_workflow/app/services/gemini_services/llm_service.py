from typing import Any, Dict, List, Optional

import httpx
from fastapi import Depends
from google import genai

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


class GeminiService:
    def __init__(self, llm_usage_repo: LLMUsageRepository = Depends()):
        """
        Initialize the Gemini service

        :param llm_usage_repo: Repository for LLM usage tracking
        """
        self.gemini_api_key = settings.GEMINI_API_KEY
        self.default_model = settings.GEMINI_DEFAULT_MODEL
        self.default_temperature = 0.2
        self.llm_usage_repo = llm_usage_repo

        # Initialize Gemini client
        self.client = genai.Client(api_key=self.gemini_api_key)

        self.timeout = httpx.Timeout(
            connect=60.0,
            read=300.0,
            write=150.0,
            pool=60.0,
        )

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        thinking_budget: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Generate text response from Gemini

        :param prompt: The user prompt
        :param system_prompt: Optional system prompt
        :param temperature: Temperature for generation (0.0 to 1.0)
        :param max_tokens: Maximum tokens for response
        :param thinking_budget: Thinking budget for 2.5 models (0 to disable)
        :return: Full API response including usage data
        """
        try:
            # Prepare the contents (only user messages for Gemini)
            contents = [{"role": "user", "parts": [{"text": prompt}]}]

            # Prepare generation config with system instruction
            config_params = {
                "temperature": self.default_temperature,
                "max_output_tokens": 55555,
                "thinking_config": genai.types.ThinkingConfig(
                    thinking_budget=thinking_budget if thinking_budget is not None else -1,
                ),
                "response_mime_type": "text/plain",
            }
            
            # Add system instruction if provided
            if system_prompt:
                config_params["system_instruction"] = [
                    genai.types.Part.from_text(text=system_prompt),
                ]
            
            config = genai.types.GenerateContentConfig(**config_params)

            # Make the request
            response = self.client.models.generate_content(
                model=self.default_model,
                contents=contents,
                config=config,
            )

            # Extract response text
            response_text = response.text if hasattr(response, 'text') else ""

            # Log usage if available
            if hasattr(response, 'usage_metadata'):
                usage_data = {
                    "input_tokens": response.usage_metadata.prompt_token_count,
                    "output_tokens": response.usage_metadata.candidates_token_count,
                    "total_tokens": response.usage_metadata.total_token_count,
                }
                loggers["gemini"].info(f"Gemini usage: {usage_data}")
                # Note: You might need to adapt this based on your LLM usage repo structure
                # await self.llm_usage_repo.add_gemini_usage(usage_data)

            return {
                "content": response_text,
                "usage": getattr(response, 'usage_metadata', None),
                "response": response,
            }

        except Exception as exc:
            error_msg = f"Error in Gemini text generation: {str(exc)}"
            loggers["gemini"].error(error_msg)
            raise JsonResponseError(status_code=500, detail=error_msg)

    async def generate_text_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        thinking_budget: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Generate streaming text response from Gemini

        :param prompt: The user prompt
        :param system_prompt: Optional system prompt
        :param temperature: Temperature for generation (0.0 to 1.0)
        :param max_tokens: Maximum tokens for response
        :param thinking_budget: Thinking budget for 2.5 models (0 to disable)
        :return: Full API response including usage data
        """
        try:
            # Prepare the contents (only user messages for Gemini)
            contents = [{"role": "user", "parts": [{"text": prompt}]}]

            # Prepare generation config with system instruction
            config_params = {
                "temperature": self.default_temperature,
                "max_output_tokens": 55555,
                "thinking_config": genai.types.ThinkingConfig(
                    thinking_budget=thinking_budget if thinking_budget is not None else -1,
                ),
                "response_mime_type": "text/plain",
            }
            
            # Add system instruction if provided
            if system_prompt:
                config_params["system_instruction"] = [
                    genai.types.Part.from_text(text=system_prompt),
                ]
            
            config = genai.types.GenerateContentConfig(**config_params)

            # Make the streaming request
            stream = self.client.models.generate_content_stream(
                model=self.default_model,
                contents=contents,
                config=config,
            )

            # Collect all chunks
            collected_text = ""
            final_response = None
            
            for chunk in stream:
                if hasattr(chunk, 'text') and chunk.text:
                    collected_text += chunk.text
                final_response = chunk

            # Log usage if available
            if final_response and hasattr(final_response, 'usage_metadata'):
                usage_data = {
                    "input_tokens": final_response.usage_metadata.prompt_token_count,
                    "output_tokens": final_response.usage_metadata.candidates_token_count,
                    "total_tokens": final_response.usage_metadata.total_token_count,
                }
                loggers["gemini"].info(f"Gemini streaming usage: {usage_data}")

            return {
                "content": collected_text,
                "usage": getattr(final_response, 'usage_metadata', None),
                "response": final_response,
            }

        except Exception as exc:
            error_msg = f"Error in Gemini streaming text generation: {str(exc)}"
            loggers["gemini"].error(error_msg)
            raise JsonResponseError(status_code=500, detail=error_msg)

    async def generate_chat_response(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        thinking_budget: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Generate chat response from Gemini with conversation history

        :param messages: List of messages in the conversation
        :param system_prompt: Optional system prompt
        :param temperature: Temperature for generation (0.0 to 1.0)
        :param max_tokens: Maximum tokens for response
        :param thinking_budget: Thinking budget for 2.5 models (0 to disable)
        :return: Full API response including usage data
        """
        try:
            # Create chat session
            chat = self.client.chats.create(
                model=self.default_model,
                history=messages,
            )

            # Prepare generation config with system instruction
            config_params = {
                "temperature": self.default_temperature,
                "max_output_tokens": 55555,
                "thinking_config": genai.types.ThinkingConfig(
                    thinking_budget=thinking_budget if thinking_budget is not None else -1,
                ),
                "response_mime_type": "text/plain",
            }
            
            # Add system instruction if provided
            if system_prompt:
                config_params["system_instruction"] = [
                    genai.types.Part.from_text(text=system_prompt),
                ]
            
            config = genai.types.GenerateContentConfig(**config_params)

            # Get the last message as the current prompt
            last_message = messages[-1] if messages else {"parts": [{"text": ""}]}
            current_prompt = last_message.get("parts", [{"text": ""}])[0].get("text", "")

            # Send message
            response = chat.send_message(current_prompt, config=config)

            # Extract response text
            response_text = response.text if hasattr(response, 'text') else ""

            # Log usage if available
            if hasattr(response, 'usage_metadata'):
                usage_data = {
                    "input_tokens": response.usage_metadata.prompt_token_count,
                    "output_tokens": response.usage_metadata.candidates_token_count,
                    "total_tokens": response.usage_metadata.total_token_count,
                }
                loggers["gemini"].info(f"Gemini chat usage: {usage_data}")

            return {
                "content": response_text,
                "usage": getattr(response, 'usage_metadata', None),
                "response": response,
                "chat": chat,
            }

        except Exception as exc:
            error_msg = f"Error in Gemini chat response: {str(exc)}"
            loggers["gemini"].error(error_msg)
            raise JsonResponseError(status_code=500, detail=error_msg)

    async def gemini_client_request(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        thinking_budget: Optional[int] = None,
    ) -> str:
        """
        Simple method to get text response from Gemini - compatible with existing code

        :param prompt: The user prompt
        :param system_prompt: Optional system prompt
        :param temperature: Temperature for generation (0.0 to 1.0)
        :param max_tokens: Maximum tokens for response
        :param thinking_budget: Thinking budget for 2.5 models (0 to disable)
        :return: Generated text content
        """
        response = await self.generate_text(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            thinking_budget=thinking_budget,
        )
        return response.get("content", "") 