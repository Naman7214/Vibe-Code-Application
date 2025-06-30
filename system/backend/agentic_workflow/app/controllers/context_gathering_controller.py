from fastapi import Depends, status
from fastapi.responses import JSONResponse

from system.backend.agentic_workflow.app.models.schemas.context_gathering_schema import (
    ContextGatheringRequest,
)
from system.backend.agentic_workflow.app.usecases.context_gathering_usecases.stage_i_usecase.stage_i_usecase import (
    StageIUsecase,
)
from system.backend.agentic_workflow.app.usecases.context_gathering_usecases.stage_v_usecase.stage_v_usecase import (
    StageVUsecase,
)
from system.backend.agentic_workflow.app.utils.session_context import (
    session_state,
)


class ContextGatheringController:
    def __init__(
        self,
        stage_i_usecase: StageIUsecase = Depends(),
        stage_v_usecase: StageVUsecase = Depends(),
    ):
        self.stage_i_usecase = stage_i_usecase
        self.stage_v_usecase = stage_v_usecase

    async def execute(self, request: ContextGatheringRequest) -> JSONResponse:
        """
        Handle context gathering - automatically determines stage based on completion status

        :param request: ContextGatheringRequest containing user selections
        :return: JSONResponse with context data
        """
        try:
            # Get session_id from context
            session_id = session_state.get()
            if not session_id:
                return JSONResponse(
                    content={
                        "data": {},
                        "message": "Session not found",
                        "error": "No session_id available",
                    },
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            # #execute Stage I (screen selection)
            # result = await self.stage_i_usecase.execute(request)
            # message = "Stage I context gathering completed successfully"
            # stage = "stage_i"
            # Stage I is complete, execute Stage V (navigation generation)
            result = await self.stage_v_usecase.execute(request)
            message = (
                "Stage V navigation context gathering completed successfully"
            )
            stage = "stage_v"

            return JSONResponse(
                content={
                    "data": result["data"],
                    "message": message,
                    "error": None,
                    "session_id": result["session_id"],
                    "stage": stage,
                    "metadata": {
                        key: value
                        for key, value in result.items()
                        if key not in ["data", "session_id"]
                    },
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
