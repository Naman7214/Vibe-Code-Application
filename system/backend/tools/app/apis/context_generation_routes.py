from fastapi import APIRouter, Depends

from system.backend.tools.app.controllers.context_generation.screen_generation_controller import (
    ScreenGenerationController,
)
from system.backend.tools.app.controllers.context_generation.design_theme_controller import (
    DesignThemeController,
)
from system.backend.tools.app.controllers.context_generation.navigation_context_controller import (
    NavigationContextController,
)
from system.backend.tools.app.models.schemas.context_generation_schema import (
    ScreenGenerationRequest,
    DesignThemeGenerationRequest,
    NavigationContextGenerationRequest,
)
from system.backend.tools.app.utils.error_handler import handle_exceptions

router = APIRouter()


@router.post("/screen-generation")
@handle_exceptions
async def screen_generation(
    request: ScreenGenerationRequest,
    screen_generation_controller: ScreenGenerationController = Depends(),
):
    return await screen_generation_controller.execute(request)


@router.post("/design-theme-generation")
@handle_exceptions
async def design_theme_generation(
    request: DesignThemeGenerationRequest,
    design_theme_controller: DesignThemeController = Depends(),
):
    return await design_theme_controller.execute(request)


@router.post("/navigation-context-generation")
@handle_exceptions
async def navigation_context_generation(
    request: NavigationContextGenerationRequest,
    navigation_context_controller: NavigationContextController = Depends(),
):
    return await navigation_context_controller.execute(request)


            



