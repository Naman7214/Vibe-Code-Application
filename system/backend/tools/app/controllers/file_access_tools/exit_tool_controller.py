from fastapi import Depends, status
from fastapi.responses import JSONResponse

from system.backend.tools.app.models.schemas.file_access_schemas import (
    ExitToolRequest,
)
from system.backend.tools.app.usecases.file_access_tools.exit_tool_usecase import (
    ExitToolUseCase,
)


class ExitToolController:
    def __init__(self, exit_tool_usecase: ExitToolUseCase = Depends()):
        self.exit_tool_usecase = exit_tool_usecase

    async def execute(self, request: ExitToolRequest):
        """
        Execute the exit tool request to append AI agent summary to a text file.

        Args:
            request: ExitToolRequest containing file_path, summary, and explanation

        Returns:
            JSONResponse with operation results
        """
        response = await self.exit_tool_usecase.execute(
            request.file_path, request.summary, request.explanation
        )

        if response.get("success", False):
            return JSONResponse(
                content={
                    "data": response,
                    "message": "Summary appended to file successfully",
                    "error": None,
                },
                status_code=status.HTTP_200_OK,
            )
        else:
            return JSONResponse(
                content={
                    "data": response,
                    "message": "Failed to append summary to file",
                    "error": response.get("error", "Unknown error occurred"),
                },
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
