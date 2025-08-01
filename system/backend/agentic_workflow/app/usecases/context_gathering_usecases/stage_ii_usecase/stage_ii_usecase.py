from fastapi import Depends, HTTPException
from fastapi.responses import JSONResponse

from system.backend.agentic_workflow.app.models.domain.error import Error
from system.backend.agentic_workflow.app.models.schemas.context_gathering_schema import (
    ContextGatheringRequest,
)
from system.backend.agentic_workflow.app.repositories.error_repo import (
    ErrorRepo,
)
from system.backend.agentic_workflow.app.usecases.context_gathering_usecases.stage_ii_usecase.helper import (
    Helper,
)


class StageIIUsecase:
    def __init__(
        self, helper: Helper = Depends(), error_repo: ErrorRepo = Depends()
    ):
        self.helper = helper
        self.error_repo = error_repo

    async def execute(self, request: ContextGatheringRequest) -> JSONResponse:
        try:

            await self.helper.run_stage_2_pipeline(request)

            return {
                "success": True,
                "message": "Context gathering completed successfully",
                "error": None,
            }

        except HTTPException as e:
            await self.error_repo.insert_error(
                Error(
                    phase="stage_ii",
                    error_message="Error in the stage ii of context gathering usecase: "
                    + str(e.detail),
                    stack_trace=e.with_traceback(),
                )
            )

            return {
                "success": False,
                "message": "Error in the stage ii of context gathering usecase: "
                + str(e.detail),
                "error": e.detail,
            }
