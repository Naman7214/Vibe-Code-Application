from fastapi import Depends, status
from fastapi.responses import JSONResponse

from system.backend.tools.app.models.schemas.context_generation_schema import (
    DesignThemeGenerationRequest,
)
from system.backend.tools.app.usecases.context_generation.design_theme_usecase import (
    DesignThemeUsecase,
)


class DesignThemeController:
    def __init__(
        self,
        design_theme_usecase: DesignThemeUsecase = Depends(),
    ):
        self.design_theme_usecase = design_theme_usecase

    async def execute(self, request: DesignThemeGenerationRequest):
        """Handle design theme generation request"""
        result = await self.design_theme_usecase.execute(request)

        return JSONResponse(
            content={
                "data": result,
                "message": "Design theme generation completed successfully",
                "error": "",
            },
            status_code=status.HTTP_200_OK,
        )
