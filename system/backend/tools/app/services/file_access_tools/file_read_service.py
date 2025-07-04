import os
from datetime import datetime


from fastapi import Depends, HTTPException, status

from system.backend.tools.app.models.domain.error import Error
from system.backend.tools.app.repositories.error_repo import ErrorRepo
from system.backend.tools.app.utils.path_validator import is_safe_path


class FileReadService:
    def __init__(self, error_repo: ErrorRepo = Depends()):
        self.error_repo = error_repo
        self.MAX_LINES = 1500  # Maximum number of lines to return (matches default end_line)

    async def read_file(
        self,
        file_path: str,
        start_line: int = 0,
        end_line: int = 1500,
    ):
        try:
            # Check if path is safe
            is_safe, error_msg = is_safe_path(file_path)
            if not is_safe:
                await self.error_repo.insert_error(
                    Error(
                        tool_name="FileReadService",
                        error_message=f"Access denied: {error_msg}",
                        timestamp=datetime.now().isoformat(),
                    )
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied: {error_msg}",
                )

            # Use the absolute file path directly
            if not os.path.exists(file_path):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"File not found: {file_path}",
                )

            stats = os.stat(file_path)
            file_extension = os.path.splitext(file_path)[1].lower()

            # Basic check for binary files
            if self._is_likely_binary(file_path):
                return {
                    "content": "[This appears to be a binary file that cannot be displayed]",
                    "size_bytes": stats.st_size,
                    "last_modified": datetime.fromtimestamp(
                        stats.st_mtime
                    ).isoformat(),
                    "is_binary": True,
                }

            with open(file_path, "r", encoding="utf-8") as file:
                try:
                    lines = file.readlines()
                except UnicodeDecodeError:
                    return {
                        "content": "[This file contains characters that cannot be decoded as UTF-8]",
                        "size_bytes": stats.st_size,
                        "last_modified": datetime.fromtimestamp(
                            stats.st_mtime
                        ).isoformat(),
                        "is_binary": True,
                    }

                total_lines = len(lines)

                # Handle line range specification
                # Now that we have explicit defaults (0, 1500), we always have values
                start = max(0, start_line)
                end = min(total_lines, end_line)

                # Check if we need to truncate
                is_truncated = total_lines > end
                remaining_lines = total_lines - end if is_truncated else 0

                # Get the slice of lines we need
                selected_lines = lines[start:end]
                content = "".join(selected_lines)

                # Generate LLM-friendly summary for context
                file_info = self._generate_file_info(
                    file_path,
                    total_lines,
                    start,
                    end,
                    remaining_lines,
                    is_truncated,
                )

            return {
                "content": content,
                "size_bytes": stats.st_size,
                "last_modified": datetime.fromtimestamp(
                    stats.st_mtime
                ).isoformat(),
                "total_lines": total_lines,
                "start_line": start,
                "end_line": end,
                "is_truncated": is_truncated,
                "remaining_lines": remaining_lines,
                "file_info": file_info,
            }

        except Exception as e:
            await self.error_repo.insert_error(
                Error(
                    tool_name="FileReadService",
                    error_message=f"Error reading file {file_path}: {str(e)}",
                    timestamp=datetime.now().isoformat(),
                )
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error reading file {file_path}: {str(e)}",
            )

    def _generate_file_info(
        self, file_path, total_lines, start, end, remaining_lines, is_truncated
    ):
        """Generate a human-readable summary about the file for LLM context"""
        file_name = os.path.basename(file_path)

        info = f"File: {file_name} ({total_lines} total lines)"

        if is_truncated:
            info += f"\n[Showing lines {start+1}-{end} out of {total_lines}. {remaining_lines} lines remaining after line {end}.]"

        # React-specific context for JSX/TSX files

        return info

    def _is_likely_binary(self, file_path):
        """Basic check if a file is likely binary"""
        # Common binary extensions
        binary_extensions = [
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".pdf",
            ".zip",
            ".tar",
            ".gz",
            ".exe",
            ".dll",
            ".bin",
            ".o",
        ]

        file_extension = os.path.splitext(file_path)[1].lower()
        if file_extension in binary_extensions:
            return True

        # Check first few bytes for common binary signatures
        try:
            with open(file_path, "rb") as f:
                chunk = f.read(1024)
                # High ratio of null bytes or control characters suggests binary
                text_chars = bytearray(
                    {7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7F}
                )
                return bool(chunk.translate(None, text_chars))
        except Exception:
            # If we can't read the file, we'll assume it's not binary
            return False
