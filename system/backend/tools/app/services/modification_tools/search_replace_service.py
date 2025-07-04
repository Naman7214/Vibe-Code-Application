import asyncio
import glob
import os
import re
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import Depends, HTTPException, status

from system.backend.tools.app.models.domain.error import Error
from system.backend.tools.app.repositories.error_repo import ErrorRepo
from system.backend.tools.app.utils.path_validator import (
    get_common_exclusion_patterns,
    is_safe_path,
)


class SearchReplaceService:
    def __init__(self, error_repo: ErrorRepo = Depends()):
        self.error_repo = error_repo

    async def search_and_replace(
        self,
        query: str,
        replacement: str,
        default_path: str,
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Search for text and replace it in files.

        Args:
            query: The text or regex pattern to search for
            replacement: The text to replace the matched content with
            options: Dictionary containing search options
            default_path: Default base path to search in

        Returns:
            Dictionary with results of the operation
        """

        if options is None:
            options = {}

        case_sensitive = options.get("case_sensitive", True)
        include_pattern = options.get("include_pattern", "*")
        exclude_pattern = options.get("exclude_pattern", "")
        search_paths = options.get("search_paths", [])

        # Use default_path if no search_paths specified
        if not search_paths and default_path:
            search_paths = [default_path]
        elif not search_paths:
            search_paths = [os.getcwd()]  # Fallback to current directory

        # Convert to absolute paths
        search_paths = [os.path.abspath(path) for path in search_paths]

        safe_search_paths = []
        for path in search_paths:
            is_safe, error_msg = is_safe_path(path)
            if not is_safe:
                await self.error_repo.insert_error(
                    Error(
                        tool_name="SearchReplaceService",
                        error_message=f"Access denied: {error_msg}",
                        timestamp=datetime.now().isoformat(),
                    )
                )
            else:
                safe_search_paths.append(path)

        flags = 0 if case_sensitive else re.IGNORECASE
        try:
            pattern = re.compile(query, flags)
        except re.error as e:
            await self.error_repo.insert_error(
                Error(
                    tool_name="SearchReplaceService",
                    error_message=f"Invalid regex pattern: {str(e)}",
                    timestamp=datetime.now().isoformat(),
                )
            )
            return {
                "success": False,
                "error": f"Invalid regex pattern: {str(e)}",
                "files_affected": 0,
                "matches": 0,
            }

        results = {
            "success": True,
            "files_affected": 0,
            "matches": 0,
            "changes": [],
        }

        try:
            # Process paths concurrently
            tasks = []
            for path in safe_search_paths:
                task = self._process_path(
                    path,
                    pattern,
                    replacement,
                    include_pattern,
                    exclude_pattern,
                    results,
                )
                tasks.append(task)

            await asyncio.gather(*tasks)

            return results

        except Exception as e:
            await self.error_repo.insert_error(
                Error(
                    tool_name="SearchReplaceService",
                    error_message=f"Error in search and replace: {str(e)}",
                    timestamp=datetime.now().isoformat(),
                )
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error in search and replace: {str(e)}",
            )

    async def _process_path(
        self,
        path: str,
        pattern: re.Pattern,
        replacement: str,
        include_pattern: str,
        exclude_pattern: str,
        results: Dict[str, Any],
    ) -> None:
        """Process a single search path asynchronously."""

        # Get default exclusion patterns and combine with user patterns
        default_exclusions = get_common_exclusion_patterns()
        combined_exclude_patterns = default_exclusions.copy()

        if exclude_pattern:
            # Add user-specified exclusion patterns
            user_patterns = [p.strip() for p in exclude_pattern.split(",")]
            combined_exclude_patterns.extend(user_patterns)

        if os.path.isdir(path):
            include_paths = []
            for root, dirs, files in os.walk(path):
                # Filter out excluded directories during walk to avoid traversing them
                dirs[:] = [
                    d
                    for d in dirs
                    if not self._should_exclude_directory(
                        os.path.join(root, d), combined_exclude_patterns
                    )
                ]

                for inc_pattern in include_pattern.split(","):
                    inc_pattern = inc_pattern.strip()
                    glob_pattern = os.path.join(root, inc_pattern)
                    matched_files = glob.glob(glob_pattern)

                    # Filter out excluded files
                    for file_path in matched_files:
                        if not self._should_exclude_file(
                            file_path, combined_exclude_patterns
                        ):
                            include_paths.append(file_path)
        else:
            # Single file: check if it matches include pattern and is not excluded
            if self._matches_pattern(
                path, include_pattern
            ) and not self._should_exclude_file(
                path, combined_exclude_patterns
            ):
                include_paths = [path]
            else:
                include_paths = []

        file_tasks = []
        for file_path in include_paths:
            if os.path.isfile(file_path):
                task = self._process_file(
                    file_path, pattern, replacement, results
                )
                file_tasks.append(task)

        await asyncio.gather(*file_tasks)

    def _should_exclude_directory(
        self, dir_path: str, exclude_patterns: list
    ) -> bool:
        """Check if a directory should be excluded based on patterns."""
        dir_name = os.path.basename(dir_path)
        dir_path_relative = os.path.relpath(dir_path)

        for pattern in exclude_patterns:
            # Check exact directory name match
            if dir_name == pattern or dir_name == pattern.rstrip("/"):
                return True
            # Check if pattern matches the relative path
            if self._matches_pattern(dir_path_relative, pattern):
                return True
            # Check if it's a dotfile/hidden directory and pattern matches hidden files
            if dir_name.startswith(".") and pattern.startswith("."):
                if self._matches_pattern(dir_name, pattern):
                    return True
        return False

    def _should_exclude_file(
        self, file_path: str, exclude_patterns: list
    ) -> bool:
        """Check if a file should be excluded based on patterns."""
        file_name = os.path.basename(file_path)
        file_path_relative = os.path.relpath(file_path)

        for pattern in exclude_patterns:
            # Check exact file name match
            if file_name == pattern:
                return True
            # Check if pattern matches the relative path
            if self._matches_pattern(file_path_relative, pattern):
                return True
            # Check if pattern matches the file name with glob
            if self._matches_pattern(file_name, pattern):
                return True
        return False

    def _matches_pattern(self, path: str, pattern: str) -> bool:
        """Check if a path matches a glob pattern."""
        for single_pattern in pattern.split(","):
            single_pattern = single_pattern.strip()
            if glob.fnmatch.fnmatch(os.path.basename(path), single_pattern):
                return True
            # Also check full path for patterns with slashes
            if "/" in single_pattern or "\\" in single_pattern:
                if glob.fnmatch.fnmatch(path, single_pattern):
                    return True
        return False

    async def _process_file(
        self,
        file_path: str,
        pattern: re.Pattern,
        replacement: str,
        results: Dict[str, Any],
    ) -> None:
        """Process a single file for search and replace asynchronously."""
        try:
            # Read file content using standard open
            with open(
                file_path, "r", encoding="utf-8", errors="ignore"
            ) as file:
                original_content = file.read()

            matches = list(pattern.finditer(original_content))
            if not matches:
                return

            new_content = pattern.sub(replacement, original_content)
            file_changes = []

            for match in matches:
                start, end = match.span()
                before_ctx = original_content[max(0, start - 20) : start]
                matched_text = original_content[start:end]
                after_ctx = original_content[
                    end : min(len(original_content), end + 20)
                ]

                replaced_text = pattern.sub(replacement, matched_text)

                file_changes.append(
                    {
                        "line_number": original_content[:start].count("\n") + 1,
                        "context": f"{before_ctx}[{matched_text}]{after_ctx}",
                        "replacement": replaced_text,
                    }
                )

            # Apply changes if not preview mode
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(new_content)

            # Update results with a lock to avoid race conditions
            async with asyncio.Lock():
                results["files_affected"] += 1
                results["matches"] += len(matches)
                results["changes"].append(
                    {
                        "file": file_path,
                        "matches": len(matches),
                        "changes": file_changes,
                    }
                )

        except Exception as e:
            async with asyncio.Lock():
                results["success"] = False
                results["error"] = (
                    f"Error processing file {file_path}: {str(e)}"
                )

            await self.error_repo.insert_error(
                Error(
                    tool_name="SearchReplaceService",
                    error_message=f"Error processing file {file_path}: {str(e)}",
                    timestamp=datetime.now().isoformat(),
                )
            )
