import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import Depends, HTTPException, status

from system.backend.tools.app.models.domain.error import Error
from system.backend.tools.app.repositories.error_repo import ErrorRepo
from system.backend.tools.app.utils.path_validator import (
    get_directory_exclusion_patterns,
    is_safe_path,
)


class DirectoryListService:
    def __init__(self, error_repo: ErrorRepo = Depends()):
        self.error_repo = error_repo

    async def list_directory(
        self,
        dir_path: str,
        recursive: bool,
        explanation: str,
        default_path: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        try:
            # Determine the actual directory path to list
            if dir_path in ["", ".", "./"]:
                # Use default_path if dir_path is empty or current directory
                if default_path:
                    actual_path = default_path
                else:
                    actual_path = os.getcwd()
            elif os.path.isabs(dir_path):
                # If dir_path is absolute, use it directly
                actual_path = dir_path
            else:
                # If dir_path is relative, combine with default_path or current directory
                base_path = default_path if default_path else os.getcwd()
                actual_path = os.path.join(base_path, dir_path)

            # Normalize the path
            actual_path = os.path.abspath(actual_path)

            # Check if path is safe
            is_safe, error_msg = is_safe_path(actual_path)
            if not is_safe:
                await self.error_repo.insert_error(
                    Error(
                        tool_name="DirectoryListService",
                        error_message=f"Access denied: {error_msg}",
                        timestamp=datetime.now().isoformat(),
                    )
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied: {error_msg}",
                )

            # Verify that the directory exists
            if not os.path.exists(actual_path):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Directory not found: {actual_path}",
                )

            if not os.path.isdir(actual_path):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Path is not a directory: {actual_path}",
                )

            # Get comprehensive list of directories to exclude from listing
            excluded_dirs = get_directory_exclusion_patterns()

            async def process_directory(
                current_path: str,
            ) -> List[Dict[str, Any]]:
                items = []

                try:
                    for item in os.listdir(current_path):
                        # Skip items that should be excluded
                        if self._should_exclude_item(item, excluded_dirs):
                            continue

                        full_path = os.path.join(current_path, item)

                        if os.path.isdir(full_path):
                            items.append(
                                {
                                    "path": full_path,
                                    "type": "directory",
                                    "size_bytes": None,
                                    "last_modified": None,
                                }
                            )

                            if recursive:
                                items.extend(await process_directory(full_path))

                        else:
                            stats = os.stat(full_path)
                            items.append(
                                {
                                    "path": full_path,
                                    "type": "file",
                                    "size_bytes": stats.st_size,
                                    "last_modified": datetime.fromtimestamp(
                                        stats.st_mtime
                                    ).isoformat(),
                                }
                            )

                except PermissionError:

                    await self.error_repo.insert_error(
                        Error(
                            tool_name="DirectoryListService",
                            error_message=f"Permission denied for directory: {current_path}",
                            timestamp=datetime.now().isoformat(),
                        )
                    )
                    return [
                        {
                            "path": current_path,
                            "type": "directory",
                            "size_bytes": 0,
                            "last_modified": datetime.now().isoformat(),
                            "error": "Permission denied",
                        }
                    ]

                return items

            return await process_directory(actual_path)

        except HTTPException:
            # Re-raise HTTP exceptions to preserve their status codes
            raise
        except Exception as e:
            await self.error_repo.insert_error(
                Error(
                    tool_name="DirectoryListService",
                    error_message=f"Error listing directory {actual_path}: {str(e)}",
                    timestamp=datetime.now().isoformat(),
                )
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error listing directory {actual_path}: {str(e)}",
            )

    def _should_exclude_item(
        self, item_name: str, excluded_patterns: List[str]
    ) -> bool:
        """
        Check if an item (file or directory) should be excluded.

        Args:
            item_name: The name of the file or directory
            excluded_patterns: List of patterns to exclude

        Returns:
            True if the item should be excluded, False otherwise
        """
        # Check if item name matches any exclusion pattern
        for pattern in excluded_patterns:
            # Exact match
            if item_name == pattern:
                return True
            # Remove trailing slash and check again
            if item_name == pattern.rstrip("/"):
                return True
            # Check if it's a hidden file starting with dot
            if item_name.startswith(".") and pattern.startswith("."):
                if item_name == pattern:
                    return True

        return False
