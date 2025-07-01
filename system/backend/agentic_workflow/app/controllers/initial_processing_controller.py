from fastapi import Depends, status
from fastapi.responses import JSONResponse

from system.backend.agentic_workflow.app.models.schemas.initial_processing_schema import (
    InitialProcessingRequest,
)
from system.backend.agentic_workflow.app.usecases.initial_processing_usecases.initial_processing_usecase import (
    InitialProcessingUsecase,
)


class InitialProcessingController:
    def __init__(
        self, initial_processing_usecase: InitialProcessingUsecase = Depends()
    ):
        self.initial_processing_usecase = initial_processing_usecase

    async def execute(self, request: InitialProcessingRequest) -> JSONResponse:
        """
        Process initial user query to generate domain analysis, industry patterns,
        screens, and business context

        :param request: InitialProcessingRequest containing user query and platform type
        :return: JSONResponse with generated context data
        """
        try:
            result = await self.initial_processing_usecase.execute(request)

            return JSONResponse(
                content={
                    "data": result["data"],
                    "message": "Initial processing completed successfully",
                    "error": None,
                    "session_id": result["session_id"],
                    "saved_to": result["saved_to"],
                },
                status_code=status.HTTP_200_OK,
            )

        except Exception as e:
            return JSONResponse(
                content={
                    "data": {},
                    "message": "Initial processing failed",
                    "error": str(e),
                },
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
