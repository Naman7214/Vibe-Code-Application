from fastapi import APIRouter, Depends

from system.backend.agentic_workflow.app.controllers.context_gathering_controller import (
    ContextGatheringController,
)
from system.backend.agentic_workflow.app.models.schemas.context_gathering_schema import (
    ContextGatheringRequest,
)

router = APIRouter()


@router.post("/context-gathering")
async def context_gathering(
    request: ContextGatheringRequest,
    context_gathering_controller: ContextGatheringController = Depends(),
):
    """
    Context Gathering Endpoint
    
    This endpoint handles context gathering for both web and mobile platforms:
    - If platform_type is "web": Uses React-specific context gathering pipeline
    - If platform_type is anything else (e.g., "mobile", "flutter"): Uses Flutter-specific context gathering pipeline
    
    The endpoint executes a 5-stage context gathering process:
    Stage 1: Domain Intelligence - Analyzes user query for domain patterns and screen suggestions
    Stage 2: Screen Requirements - Defines detailed requirements for each selected screen
    Stage 3A: Theme Strategy - Generates design system and visual themes
    Stage 3B: Component/Widget Strategy - Defines reusable components (React) or widgets (Flutter)
    Stage 4: Screen Detailed Planning - Creates comprehensive screen specifications
    Stage 5: Navigation & State - Designs navigation structure and state management
    
    Args:
        request: ContextGatheringRequest containing:
            - user_query: Description of the application to build
            - session_id: Unique identifier for the session
            - platform_type: Target platform ("web" for React, "mobile"/"flutter" for Flutter)
            - dict_of_screens: Screen selection (for follow-up requests)
            - is_follow_up: Whether this is a follow-up request
    
    Returns:
        JSONResponse with completion status and platform-specific message
    """
    return await context_gathering_controller.execute(request)
