from typing import Any, Dict

from fastapi import Depends, HTTPException
from fastapi.responses import JSONResponse

from system.backend.agentic_workflow.app.models.domain.error import Error
from system.backend.agentic_workflow.app.models.schemas.context_gathering_schema import (
    ContextGatheringRequest,
)
from system.backend.agentic_workflow.app.repositories.error_repo import (
    ErrorRepo,
)
from system.backend.agentic_workflow.app.usecases.context_gathering_usecase.stage_iii_usecase.helper import (
    Helper,
)


class StageIIIUsecase:
    def __init__(
        self, helper: Helper = Depends(), error_repo: ErrorRepo = Depends()
    ):
        self.helper = helper
        self.error_repo = error_repo

    async def execute(
        self, request: ContextGatheringRequest, dict_of_screens: Dict[str, Any]
    ) -> JSONResponse:
        try:

            await self.helper.run_stage_3_pipeline(request, dict_of_screens)

            return {
                "success": True,
                "message": "Context gathering completed successfully",
            }
        except HTTPException as e:
            self.error_repo.insert_error(
                Error(
                    phase="stage_iii",
                    error_message="Error in the stage iii of context gathering usecase: "
                    + str(e.detail),
                    stack_trace=e.with_traceback(),
                )
            )

            raise HTTPException(
                status_code=500,
                detail="Error in the stage iii of context gathering usecase: "
                + str(e.detail),
            )
