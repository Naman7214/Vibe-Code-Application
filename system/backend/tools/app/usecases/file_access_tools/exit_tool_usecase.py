from typing import Any, Dict

from fastapi import Depends

from system.backend.tools.app.services.file_access_tools.exit_tool_service import (
    ExitToolService,
)


class ExitToolUseCase:
    def __init__(self, exit_tool_service: ExitToolService = Depends()):
        self.exit_tool_service = exit_tool_service

    async def execute(self, file_path: str, summary: str) -> Dict[str, Any]:
        """
        Execute the exit tool operation to append AI agent summary to a text file.

        Args:
            file_path: Path to the text file to append to
            summary: Summary content from the AI agent

        Returns:
            Dictionary with operation results
        """
        return await self.exit_tool_service.append_summary_to_file(
            file_path, summary
        )
