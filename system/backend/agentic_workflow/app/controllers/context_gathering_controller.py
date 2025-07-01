from fastapi import Depends, status
from fastapi.responses import JSONResponse

from system.backend.agentic_workflow.app.models.schemas.context_gathering_schema import (
    ContextGatheringRequest,
)
from system.backend.agentic_workflow.app.usecases.context_gathering_usecase.stage_ii_usecase.stage_ii_usecase import (
    StageIIUsecase,
)
from system.backend.agentic_workflow.app.usecases.context_gathering_usecase.stage_iii_usecase.stage_iii_usecase import (
    StageIIIUsecase,
)


class ContextGatheringController:
    def __init__(
        self,
        stage_ii_usecase: StageIIUsecase = Depends(),
        stage_iii_usecase: StageIIIUsecase = Depends(),
    ):
        self.stage_ii_usecase = stage_ii_usecase
        self.stage_iii_usecase = stage_iii_usecase

    async def execute(self, request: ContextGatheringRequest) -> JSONResponse:
        """
        Generate screens based on user query and save each screen individually

        :param request: ScreenGenerationRequest containing user query and options
        :return: JSONResponse with generated screens data and individual file paths
        """
        dict_of_screens = {
            "feedback_screen": "it'll be used to collect feedback from the user",
            "comparison_screen": "it'll be used to compare the products",
        }

        stage_ii_result = await self.stage_ii_usecase.execute(
            request, dict_of_screens
        )

        if stage_ii_result["success"]:
            stage_iii_result = await self.stage_iii_usecase.execute(
                request, dict_of_screens
            )

        return JSONResponse(
            content={
                "data": stage_iii_result,
                "message": "Context gathering completed successfully",
                "error": None,
            },
            status_code=status.HTTP_200_OK,
        )
