import os
import subprocess
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import Depends, HTTPException, status

from system.backend.tools.app.models.domain.error import Error
from system.backend.tools.app.repositories.error_repo import ErrorRepo
from system.backend.tools.app.utils.path_validator import (
    get_directory_exclusion_patterns,
    is_safe_path,
)


class FileSearchService:
    def __init__(self, error_repo: ErrorRepo = Depends()):
        self.error_repo = error_repo

    def _find_fzf_executable(self) -> str:
        """Find the fzf executable in common locations."""
        # Common locations for fzf
        common_paths = [
            "/usr/local/bin/fzf",
            "/opt/homebrew/bin/fzf",
            "/usr/bin/fzf",
            "/home/linuxbrew/.linuxbrew/bin/fzf",
            "fzf",  # Fallback to PATH lookup
        ]

        for path in common_paths:
            try:
                result = subprocess.run(
                    [path, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    return path
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue

        # Try which/where command as final fallback
        try:
            result = subprocess.run(
                ["which", "fzf"] if os.name != "nt" else ["where", "fzf"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip().split("\n")[0]
        except:
            pass

        raise FileNotFoundError("fzf executable not found")

    async def search_files(
        self, pattern: str, default_path: str
    ) -> List[Dict[str, Any]]:
        try:
            # Determine the search directory
            if default_path:
                search_dir = os.path.abspath(default_path)
            else:
                search_dir = os.getcwd()

            # Check if the search path is safe
            is_safe, error_msg = is_safe_path(search_dir)
            if not is_safe:
                await self.error_repo.insert_error(
                    Error(
                        tool_name="FileSearchService",
                        error_message=f"Access denied to search path: {error_msg}",
                        timestamp=datetime.now().isoformat(),
                    )
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied to search path: {error_msg}",
                )

            # Verify that the directory exists
            if not os.path.exists(search_dir):
                await self.error_repo.insert_error(
                    Error(
                        tool_name="FileSearchService",
                        error_message=f"Search directory not found: {search_dir}",
                        timestamp=datetime.now().isoformat(),
                    )
                )
                return [
                    {
                        "file_path": pattern,
                        "score": 0,
                        "error": f"Search directory not found: {search_dir}",
                    }
                ]

            if not os.path.isdir(search_dir):
                await self.error_repo.insert_error(
                    Error(
                        tool_name="FileSearchService",
                        error_message=f"Search path is not a directory: {search_dir}",
                        timestamp=datetime.now().isoformat(),
                    )
                )
                return [
                    {
                        "file_path": pattern,
                        "score": 0,
                        "error": f"Search path is not a directory: {search_dir}",
                    }
                ]

            # Get comprehensive list of directories to exclude from search
            exclude_dirs = get_directory_exclusion_patterns()

            # First, generate a list of files excluding the directories
            find_cmd = ["find", search_dir]

            # Add exclusion patterns
            for exclude_dir in exclude_dirs:
                find_cmd.extend(
                    [
                        "-not",
                        "-path",
                        f"*/{exclude_dir}/*",
                        "-not",
                        "-path",
                        f"*/{exclude_dir}",
                    ]
                )

            # Run find command to get filtered file list
            find_process = subprocess.run(
                find_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=search_dir,
            )

            if find_process.returncode != 0:
                error_msg = f"Find command failed: {find_process.stderr}"
                await self.error_repo.insert_error(
                    Error(
                        tool_name="FileSearchService",
                        error_message=error_msg,
                        timestamp=datetime.now().isoformat(),
                    )
                )
                return [{"file_path": pattern, "score": 0, "error": error_msg}]

            # Get the filtered file list
            file_list = find_process.stdout.strip().split("\n")

            # Filter out empty strings
            file_list = [f for f in file_list if f.strip()]

            if not file_list:
                return [
                    {
                        "file_path": pattern,
                        "score": 0,
                        "error": "No files found in search directory",
                    }
                ]

            # Find fzf executable
            try:
                fzf_path = self._find_fzf_executable()
            except FileNotFoundError:
                await self.error_repo.insert_error(
                    Error(
                        tool_name="FileSearchService",
                        error_message="fzf is not installed or not found in PATH. Please install fzf first.",
                        timestamp=datetime.now().isoformat(),
                    )
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="fzf is not installed or not found in PATH. Please install fzf first.",
                )

            # Use fzf to search through the filtered file list
            env = os.environ.copy()
            # Ensure common paths are in PATH
            if "PATH" in env:
                env["PATH"] = f"/usr/local/bin:/opt/homebrew/bin:{env['PATH']}"
            else:
                env["PATH"] = "/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin"

            with subprocess.Popen(
                [
                    fzf_path,
                    "-f",
                    pattern,
                    "-i",
                    "--print-query",
                    "--no-sort",
                    "--tac",
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
            ) as process:
                # Pass the filtered file list to fzf
                stdout, stderr = process.communicate(input="\n".join(file_list))

            if stderr and process.returncode != 0:
                await self.error_repo.insert_error(
                    Error(
                        tool_name="FileSearchService",
                        error_message=f"fzf search failed: {stderr}",
                        timestamp=datetime.now().isoformat(),
                    )
                )
                return [
                    {
                        "file_path": pattern,
                        "score": 0,
                        "error": f"fzf search failed: {stderr}",
                    }
                ]

            results = []
            lines = stdout.strip().split("\n")

            query = lines[0] if lines else pattern
            matches = lines[1:] if len(lines) > 1 else []

            if not matches:
                return [
                    {
                        "file_path": pattern,
                        "score": 0,
                        "error": "No matches found",
                    }
                ]

            for match in matches:
                if match:
                    score = 1.0
                    if query.lower() in match.lower():
                        score = 0.8
                    if match.lower().startswith(query.lower()):
                        score = 0.9

                    results.append({"file_path": match, "score": score})

            return results

        except HTTPException:
            # Re-raise HTTP exceptions to preserve their status codes
            raise
        except Exception as e:
            await self.error_repo.insert_error(
                Error(
                    tool_name="FileSearchService",
                    error_message=f"Error searching files: {str(e)}",
                    timestamp=datetime.now().isoformat(),
                )
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error searching files: {str(e)}",
            )
