import os
from datetime import datetime
from pathlib import Path
from typing import Tuple

import httpx
from fastapi import Depends, HTTPException, status

from system.backend.tools.app.config.settings import settings
from system.backend.tools.app.models.domain.error import Error
from system.backend.tools.app.repositories.error_repo import ErrorRepo
from system.backend.tools.app.repositories.llm_usage_repo import (
    LLMUsageRepository,
)
from system.backend.tools.app.utils.path_validator import is_safe_path


class EditFileService:
    def __init__(
        self,
        error_repo: ErrorRepo = Depends(),
        llm_usage_repo: LLMUsageRepository = Depends(),
    ):
        self.error_repo = error_repo
        self.llm_usage_repo = llm_usage_repo
        self.relace_api_key = settings.RELACE_API_KEY
        self.relace_api_url = settings.RELACE_API_URL
        self.timeout = httpx.Timeout(
            connect=30.0,
            read=120.0,
            write=60.0,
            pool=30.0,
        )

    async def edit_file(self, target_file_path: str, code_snippet: str):
        """
        Edit a file by applying code changes using the Relace API.
        Creates the file and parent directories if they don't exist.

        Args:
            target_file_path: Absolute path to the target file
            code_snippet: The code changes to apply

        Returns:
            Dictionary with success status and operation details
        """
        try:
            # Check if path is safe
            is_safe, error_msg = is_safe_path(target_file_path)
            if not is_safe:
                await self.error_repo.insert_error(
                    Error(
                        tool_name="EditFileService",
                        error_message=f"Access denied: {error_msg}",
                        timestamp=datetime.now().isoformat(),
                    )
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied: {error_msg}",
                )

            # Create parent directories if they don't exist
            parent_dir = os.path.dirname(target_file_path)
            directories_created = False

            if parent_dir and not os.path.exists(parent_dir):
                try:
                    Path(parent_dir).mkdir(parents=True, exist_ok=True)
                    directories_created = True
                except Exception as e:
                    await self.error_repo.insert_error(
                        Error(
                            tool_name="EditFileService",
                            error_message=f"Failed to create parent directories: {str(e)}",
                            timestamp=datetime.now().isoformat(),
                        )
                    )
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Failed to create parent directories: {str(e)}",
                    )

            # Read existing content or use empty string for new files
            original_content = ""
            file_existed = os.path.exists(target_file_path)

            if file_existed:
                try:
                    with open(target_file_path, "r", encoding="utf-8") as file:
                        original_content = file.read()

                except Exception as e:
                    await self.error_repo.insert_error(
                        Error(
                            tool_name="EditFileService",
                            error_message=f"Failed to read existing file: {str(e)}",
                            timestamp=datetime.now().isoformat(),
                        )
                    )
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Failed to read existing file: {str(e)}",
                    )
            else:
                print(
                    f"File does not exist, will create new file: {target_file_path}"
                )

            # Apply code changes using Relace API
            try:
                merged_code, usage_data = await self._apply_code_changes_relace(
                    original_content, code_snippet
                )

                if merged_code is None:
                    raise ValueError(
                        "Failed to apply code changes - no merged code returned"
                    )

                # Log LLM usage
                await self._log_llm_usage(
                    tool_name="EditFileService",
                    file_path=target_file_path,
                    usage_data=usage_data,
                    file_existed=file_existed,
                    directories_created=directories_created,
                )

            except Exception as api_error:
                await self.error_repo.insert_error(
                    Error(
                        tool_name="EditFileService",
                        error_message=f"Relace API error: {str(api_error)}",
                        timestamp=datetime.now().isoformat(),
                    )
                )
                return {
                    "success": False,
                    "error": f"Relace API error: {str(api_error)}",
                    "details": {
                        "file_path": target_file_path,
                        "file_existed": file_existed,
                        "directories_created": directories_created,
                        "timestamp": datetime.now().isoformat(),
                    },
                }

            # Write the merged content to file
            try:
                with open(target_file_path, "w", encoding="utf-8") as file:
                    file.write(merged_code)
            except Exception as e:
                await self.error_repo.insert_error(
                    Error(
                        tool_name="EditFileService",
                        error_message=f"Failed to write file: {str(e)}",
                        timestamp=datetime.now().isoformat(),
                    )
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to write file: {str(e)}",
                )

            return {
                "success": True,
                "details": {
                    "file_path": target_file_path,
                    "file_existed": file_existed,
                    "original_size": len(original_content),
                    "new_size": len(merged_code),
                    "directories_created": directories_created,
                    "parent_directory": (
                        parent_dir if directories_created else None
                    ),
                    "timestamp": datetime.now().isoformat(),
                },
            }

        except HTTPException:
            # Re-raise HTTP exceptions to preserve their status codes
            raise
        except Exception as e:
            await self.error_repo.insert_error(
                Error(
                    tool_name="EditFileService",
                    error_message=f"Unexpected error: {str(e)}",
                    timestamp=datetime.now().isoformat(),
                )
            )
            return {
                "success": False,
                "error": str(e),
                "details": {
                    "file_path": target_file_path,
                    "timestamp": datetime.now().isoformat(),
                },
            }

    async def _apply_code_changes_relace(
        self, initial_code: str, edit_snippet: str
    ) -> Tuple[str, dict]:
        """
        Apply code changes using the Relace API.

        Args:
            initial_code (str): The original code content (empty string for new files)
            edit_snippet (str): The code snippet to apply

        Returns:
            Tuple[str, dict]: The merged code and usage data

        Raises:
            Exception: If the API call fails or returns invalid data
        """
        try:
            payload = {
                "initialCode": initial_code,
                "editSnippet": edit_snippet,
                "stream": False,
                "relace-metadata": {
                    "tool": "EditFileService",
                    "timestamp": datetime.now().isoformat(),
                    "initial_code_length": len(initial_code),
                    "edit_snippet_length": len(edit_snippet),
                },
            }

            headers = {
                "Authorization": f"Bearer {self.relace_api_key}",
                "Content-Type": "application/json",
            }

            async with httpx.AsyncClient(
                timeout=self.timeout, verify=False
            ) as client:
                response = await client.post(
                    self.relace_api_url, json=payload, headers=headers
                )
                response.raise_for_status()

                result = response.json()
                merged_code = result.get("mergedCode")
                usage_data = result.get("usage", {})

                if not merged_code:
                    raise ValueError("No merged code returned from Relace API")

                return merged_code, usage_data

        except httpx.RequestError as e:
            raise Exception(f"Request error calling Relace API: {str(e)}")
        except httpx.HTTPStatusError as e:
            error_detail = ""
            try:
                error_detail = e.response.text
            except:
                error_detail = f"Status code: {e.response.status_code}"
            raise Exception(f"HTTP error calling Relace API: {error_detail}")
        except Exception as e:
            raise Exception(f"Unexpected error calling Relace API: {str(e)}")

    async def _log_llm_usage(
        self,
        tool_name: str,
        file_path: str,
        usage_data: dict,
        file_existed: bool,
        directories_created: bool,
    ):
        """
        Log LLM usage data to the repository.

        Args:
            tool_name: Name of the tool making the request
            file_path: Path to the file being edited
            usage_data: Usage statistics from Relace API
            file_existed: Whether the file existed before editing
            directories_created: Whether parent directories were created
        """
        try:
            llm_usage_entry = {
                "tool_name": tool_name,
                "file_path": file_path,
                "timestamp": datetime.now().isoformat(),
                "api_provider": "relace",
                "endpoint": "instantapply",
                "operation_type": "file_edit",
                "file_existed": file_existed,
                "directories_created": directories_created,
                "usage": usage_data,
                "prompt_tokens": usage_data.get("prompt_tokens", 0),
                "completion_tokens": usage_data.get("completion_tokens", 0),
                "total_tokens": usage_data.get("total_tokens", 0),
                "api_url": self.relace_api_url,
            }

            await self.llm_usage_repo.add_llm_usage(llm_usage_entry)

        except Exception as e:
            # Log error but don't fail the main operation
            await self.error_repo.insert_error(
                Error(
                    tool_name="EditFileService",
                    error_message=f"Failed to log LLM usage: {str(e)}",
                    timestamp=datetime.now().isoformat(),
                )
            )
