from fastapi import Depends, status
from fastapi.responses import JSONResponse

from backend.app.models.schemas.context_generation_schema import NavigationContextGenerationRequest
from backend.app.usecases.context_generation.navigation_context_usecase import NavigationContextUsecase


class NavigationContextController:
    def __init__(
        self,
        navigation_context_usecase: NavigationContextUsecase = Depends(),
    ):
        self.navigation_context_usecase = navigation_context_usecase

    async def execute(self, request: NavigationContextGenerationRequest):
        """Handle navigation context generation request"""
        result = await self.navigation_context_usecase.execute(request)
        
        return JSONResponse(
            content={
                "data": result,
                "message": "Navigation context generation completed successfully",
                "error": None,
            },
            status_code=status.HTTP_200_OK,
        ) 