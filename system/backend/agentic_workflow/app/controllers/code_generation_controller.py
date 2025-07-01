from fastapi import Depends, status
from fastapi.responses import JSONResponse

from system.backend.agentic_workflow.app.models.schemas.code_generation_schema import (
    CodeGenerationStageIRequest,
)
from system.backend.agentic_workflow.app.usecases.code_generation_usecases.stage_i_usecase.stage_i_usecase import (
    StageIUsecase,
)
from system.backend.agentic_workflow.app.utils.session_context import (
    session_state,
)


class CodeGenerationController:
    def __init__(self, stage_i_usecase: StageIUsecase = Depends()):
        self.stage_i_usecase = stage_i_usecase

    async def execute_stage_i(self, request: CodeGenerationStageIRequest) -> JSONResponse:
        """
        Execute Stage I code generation to create Tailwind CSS configuration and styles
        Session ID is automatically extracted from X-Session-ID header by middleware.

        :param request: CodeGenerationStageIRequest (empty body)
        :return: JSONResponse with generated files information
        """
        try:
            # Session ID is automatically set by middleware from X-Session-ID header
            current_session_id = session_state.get()
            if not current_session_id:
                return JSONResponse(
                    content={
                        "data": {},
                        "message": "Session ID not found. Please provide X-Session-ID header.",
                        "error": "Missing session context",
                    },
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            # Execute Stage I usecase
            result = await self.stage_i_usecase.execute()

            if result["success"]:
                return JSONResponse(
                    content={
                        "data": {
                            "generated_files": result.get("generated_files", []),
                            "session_id": current_session_id,
                        },
                        "message": result["message"],
                        "error": None,
                    },
                    status_code=status.HTTP_200_OK,
                )
            else:
                return JSONResponse(
                    content={
                        "data": {},
                        "message": result["message"],
                        "error": result["error"],
                    },
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

        except Exception as e:
            return JSONResponse(
                content={
                    "data": {},
                    "message": "Code generation failed",
                    "error": str(e),
                },
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            ) 