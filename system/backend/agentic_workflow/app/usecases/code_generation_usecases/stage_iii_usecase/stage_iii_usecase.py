from fastapi import Depends, HTTPException
from fastapi.responses import JSONResponse

from system.backend.agentic_workflow.app.models.domain.error import Error
from system.backend.agentic_workflow.app.models.schemas.code_generation_schema import (
    CodeGenerationRequest,
)
from system.backend.agentic_workflow.app.repositories.error_repo import (
    ErrorRepo,
)
from system.backend.agentic_workflow.app.usecases.code_generation_usecases.stage_iii_usecase.helper import (
    Helper,
)

class StageIIIUsecase:
    def __init__(
        self, helper: Helper = Depends(), error_repo: ErrorRepo = Depends()
    ):
        self.helper = helper
        self.error_repo = error_repo    

    async def execute(self, request: CodeGenerationRequest) -> JSONResponse:
        try:

            await self.helper.run_stage_3_pipeline(request)

            return {
                "success": True,
                "message": "Code generation for the screens completed successfully",
                "error": None,
            }
        except HTTPException as e:
            await self.error_repo.insert_error(
                Error(
                    phase="stage_iii",
                    error_message="Error in the stage iii of code generation usecase: "
                    + str(e.detail),
                    stack_trace=e.with_traceback(),
                )
            )

            return {
                "success": False,
                "message": "Error in the stage iii of code generation usecase: "
                + str(e.detail),
                "error": e.detail,
            }
    