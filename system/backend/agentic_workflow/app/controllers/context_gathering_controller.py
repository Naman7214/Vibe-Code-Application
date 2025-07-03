from fastapi import Depends, status
from fastapi.responses import JSONResponse

from system.backend.agentic_workflow.app.models.schemas.context_gathering_schema import (
    ContextGatheringRequest,
)
from system.backend.agentic_workflow.app.usecases.context_gathering_usecases.context_gathering_usecase import (
    ContextGatheringUsecase,
)
from system.backend.agentic_workflow.app.usecases.flutter_context_gathering_usecases.flutter_context_gathering_usecase import (
    FlutterContextGatheringUsecase,
)


class ContextGatheringController:
    def __init__(
        self,
        context_gathering_usecase: ContextGatheringUsecase = Depends(),
        flutter_context_gathering_usecase: FlutterContextGatheringUsecase = Depends(),
    ):
        self.context_gathering_usecase = context_gathering_usecase
        self.flutter_context_gathering_usecase = flutter_context_gathering_usecase

    async def execute(self, request: ContextGatheringRequest) -> JSONResponse:
        """
        Generate screens based on user query and save each screen individually.
        Handles both web and mobile platforms based on platform_type.

        :param request: ContextGatheringRequest containing user query, platform_type, and options
        :return: JSONResponse with generated screens data and individual file paths
        """

        # Route to appropriate usecase based on platform type
        if request.platform_type == "web":
            await self.context_gathering_usecase.execute(request)
        else:
            # For mobile platforms (Flutter), use the Flutter-specific usecase
            await self.flutter_context_gathering_usecase.execute(request)

        return JSONResponse(
            content={
                "data": "None",
                "message": f"Context gathering completed successfully for {request.platform_type} platform",
                "error": None,
            },
            status_code=status.HTTP_200_OK,
        )
