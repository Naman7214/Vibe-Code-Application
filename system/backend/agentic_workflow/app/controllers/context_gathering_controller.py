from fastapi import Depends, status
from fastapi.responses import JSONResponse

from system.backend.agentic_workflow.app.models.schemas.context_gathering_schema import (
    ContextGatheringRequest,
)
from system.backend.agentic_workflow.app.usecases.context_gathering_usecases.context_gathering_usecase import (
    ContextGatheringUsecase,
)


class ContextGatheringController:
    def __init__(
        self,
        context_gathering_usecase: ContextGatheringUsecase = Depends(),
    ):
        self.context_gathering_usecase = context_gathering_usecase

    async def execute(self, request: ContextGatheringRequest) -> JSONResponse:
        """
        Generate screens based on user query and save each screen individually

        :param request: ScreenGenerationRequest containing user query and options
        :return: JSONResponse with generated screens data and individual file paths
        """

        await self.context_gathering_usecase.execute(request)

        return JSONResponse(
            content={
                "data": "None",
                "message": "Context gathering completed successfully",
                "error": None,
            },
            status_code=status.HTTP_200_OK,
        )
