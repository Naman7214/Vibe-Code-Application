from fastapi import Depends, HTTPException
from fastapi.responses import JSONResponse

from system.backend.agentic_workflow.app.models.domain.error import Error
from system.backend.agentic_workflow.app.models.schemas.context_gathering_schema import (
    ContextGatheringRequest,
)
from system.backend.agentic_workflow.app.repositories.error_repo import (
    ErrorRepo,
)
from system.backend.agentic_workflow.app.usecases.flutter_context_gathering_usecases.stage_ii_usecase.flutter_helper import (
    FlutterHelper,
)


class FlutterStageIIUsecase:
    def __init__(
        self, helper: FlutterHelper = Depends(), error_repo: ErrorRepo = Depends()
    ):
        self.helper = helper
        self.error_repo = error_repo

    async def execute(self, request: ContextGatheringRequest) -> JSONResponse:
        try:

            await self.helper.run_flutter_stage_2_pipeline(request)

            return {
                "success": True,
                "message": "Flutter context gathering Stage II completed successfully",
                "error": None,
            }

        except HTTPException as e:
            await self.error_repo.insert_error(
                Error(
                    phase="flutter_stage_ii",
                    error_message="Error in the flutter stage ii of context gathering usecase: "
                    + str(e.detail),
                    stack_trace=e.with_traceback(),
                )
            )

            return {
                "success": False,
                "message": "Error in the flutter stage ii of context gathering usecase: "
                + str(e.detail),
                "error": e.detail,
            } 