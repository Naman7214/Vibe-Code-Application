from fastapi import Depends, status
from fastapi.responses import JSONResponse

from system.backend.agentic_workflow.app.models.schemas.context_gathering_schema import (
    ContextGatheringRequest,
)
from system.backend.agentic_workflow.app.usecases.context_gathering_usecases.stage_i_usecase.stage_i_usecase import (
    StageIUsecase,
)


class ContextGatheringController:
    def __init__(self, stage_i_usecase: StageIUsecase = Depends()):
        self.stage_i_usecase = stage_i_usecase

    async def execute(self, request: ContextGatheringRequest) -> JSONResponse:
        """
        Handle context gathering - updating screens based on user selections

        :param request: ContextGatheringRequest containing user selections
        :return: JSONResponse with updated context data
        """
        try:
            result = await self.stage_i_usecase.execute(request)

            return JSONResponse(
                content={
                    "data": result["data"],
                    "message": "Context gathering completed successfully",
                    "error": None,
                    "session_id": result["session_id"],
                    "updated_file": result["updated_file"],
                    "is_follow_up": result["is_follow_up"],
                    "screens_updated": result["screens_updated"],
                },
                status_code=status.HTTP_200_OK,
            )

        except Exception as e:
            return JSONResponse(
                content={
                    "data": {},
                    "message": "Context gathering failed",
                    "error": str(e),
                },
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
