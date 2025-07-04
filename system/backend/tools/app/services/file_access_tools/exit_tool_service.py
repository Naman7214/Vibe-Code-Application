import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from fastapi import Depends, HTTPException, status

from system.backend.tools.app.models.domain.error import Error
from system.backend.tools.app.repositories.error_repo import ErrorRepo
from system.backend.tools.app.utils.path_validator import is_safe_path


class ExitToolService:
    def __init__(self, error_repo: ErrorRepo = Depends()):
        self.error_repo = error_repo

    async def append_summary_to_file(
        self, file_path: str, summary: str, explanation: str
    ) -> Dict[str, Any]:
        """
        Append AI agent summary content to a text file.
        Creates the file and parent directories if they don't exist.

        Args:
            file_path: Absolute path to the target .txt file
            summary: The summary content to append
            explanation: Explanation of why this operation is needed

        Returns:
            Dictionary with success status and operation details
        """
        try:
            # Ensure the file has .txt extension
            if not file_path.lower().endswith(".txt"):
                file_path += ".txt"

            # Convert to absolute path
            abs_file_path = os.path.abspath(file_path)

            # Check if path is safe
            is_safe, error_msg = is_safe_path(abs_file_path)
            if not is_safe:
                await self.error_repo.insert_error(
                    Error(
                        tool_name="ExitToolService",
                        error_message=f"Access denied: {error_msg}",
                        timestamp=datetime.now().isoformat(),
                    )
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied: {error_msg}",
                )

            # Create parent directories if they don't exist
            parent_dir = os.path.dirname(abs_file_path)
            directories_created = False

            if parent_dir and not os.path.exists(parent_dir):
                try:
                    Path(parent_dir).mkdir(parents=True, exist_ok=True)
                    directories_created = True
                    print(f"Created parent directories: {parent_dir}")
                except Exception as e:
                    await self.error_repo.insert_error(
                        Error(
                            tool_name="ExitToolService",
                            error_message=f"Failed to create parent directories: {str(e)}",
                            timestamp=datetime.now().isoformat(),
                        )
                    )
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Failed to create parent directories: {str(e)}",
                    )

            # Check if file exists
            file_existed = os.path.exists(abs_file_path)
            original_size = 0

            if file_existed:
                try:
                    original_size = os.path.getsize(abs_file_path)
                except Exception as e:
                    await self.error_repo.insert_error(
                        Error(
                            tool_name="ExitToolService",
                            error_message=f"Failed to get file size: {str(e)}",
                            timestamp=datetime.now().isoformat(),
                        )
                    )
                    # Continue anyway, just set original size to 0
                    original_size = 0

            # Prepare the content to append
            timestamp = datetime.now().isoformat()
            separator = "\n" + "=" * 80 + "\n"
            content_to_append = (
                f"{separator}AI Agent Exit Summary - {timestamp}\n{separator}\n"
            )
            content_to_append += f"Explanation: {explanation}\n\n"
            content_to_append += f"Summary:\n{summary}\n"
            content_to_append += separator + "\n"

            # Append content to file
            try:
                with open(abs_file_path, "a", encoding="utf-8") as file:
                    # Add a newline if file exists and doesn't end with newline
                    if file_existed and original_size > 0:
                        # Check if file ends with newline
                        with open(abs_file_path, "rb") as check_file:
                            check_file.seek(-1, os.SEEK_END)
                            last_char = check_file.read(1)
                            if last_char != b"\n":
                                file.write("\n")

                    file.write(content_to_append)

                print(f"Successfully appended summary to file: {abs_file_path}")

            except Exception as e:
                await self.error_repo.insert_error(
                    Error(
                        tool_name="ExitToolService",
                        error_message=f"Failed to append to file: {str(e)}",
                        timestamp=datetime.now().isoformat(),
                    )
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to append to file: {str(e)}",
                )

            # Get final file size
            try:
                final_size = os.path.getsize(abs_file_path)
            except Exception:
                final_size = 0

            return {
                "success": True,
                "details": {
                    "file_path": abs_file_path,
                    "file_existed": file_existed,
                    "original_size": original_size,
                    "final_size": final_size,
                    "content_appended_size": len(content_to_append),
                    "directories_created": directories_created,
                    "parent_directory": (
                        parent_dir if directories_created else None
                    ),
                    "timestamp": timestamp,
                },
            }

        except HTTPException:
            # Re-raise HTTP exceptions to preserve their status codes
            raise
        except Exception as e:
            await self.error_repo.insert_error(
                Error(
                    tool_name="ExitToolService",
                    error_message=f"Unexpected error: {str(e)}",
                    timestamp=datetime.now().isoformat(),
                )
            )
            return {
                "success": False,
                "error": str(e),
                "details": {
                    "file_path": file_path,
                    "timestamp": datetime.now().isoformat(),
                },
            }
