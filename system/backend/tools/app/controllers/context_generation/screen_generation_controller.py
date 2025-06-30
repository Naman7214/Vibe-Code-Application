from fastapi import Depends, status
from fastapi.responses import JSONResponse

from system.backend.tools.app.models.schemas.context_generation_schema import (
    ScreenGenerationRequest,
)
from system.backend.tools.app.usecases.context_generation.screen_generation_usecase import (
    ScreenGenerationUsecase,
)


class ScreenGenerationController:
    def __init__(
        self, 
        screen_generation_usecase: ScreenGenerationUsecase = Depends()
    ):
        self.screen_generation_usecase = screen_generation_usecase

    async def execute(self, request: ScreenGenerationRequest) -> JSONResponse:
        """
        Generate screens based on user query and save each screen individually
        
        :param request: ScreenGenerationRequest containing user query and options
        :return: JSONResponse with generated screens data and individual file paths
        """
        result = await self.screen_generation_usecase.execute(request)
            
        return JSONResponse(
            content={
                "data": result,
                "message": "Screen generation completed successfully",
                "error": None,
            },
            status_code=status.HTTP_200_OK,
        )