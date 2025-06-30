from fastapi import APIRouter, HTTPException, Depends
from system.backend.agentic_workflow.app.models.schemas.stage_iv_schema import (
    StageIVRequest,
    StageIVResponse
)
from system.backend.agentic_workflow.app.controllers.stage_iv_controller import (
    StageIVController
)

# Create router instance
router = APIRouter(prefix="/api/v1/context-gathering", tags=["Context Gathering"])

# Create controller instance


@router.post("/stage-iv", response_model=StageIVResponse)
async def process_stage_iv(request: StageIVRequest, stage_iv_controller: StageIVController = Depends()) -> StageIVResponse:
    """
    Process Stage IV: Screen Detailed Planning
    
    This endpoint processes screen requirements, design system, and component strategies
    to generate detailed planning for each screen including layout structure, 
    component usage specifications, mock data, and content hierarchy.
    
    Args:
        request: StageIVRequest containing screen data with screen names as keys
                 and descriptions as values
    
    Returns:
        StageIVResponse with processing results and output file path
        
    Raises:
        HTTPException: If processing fails or session context is invalid
        
    Example:
        ```json
        {
            "screen_data": {
                "Homepage": "Landing page with hero section and featured products",
                "Menu": "Product catalog with filtering and search functionality",
                "Order": "Shopping cart and checkout process"
            }
        }
        ```
    """
    return await stage_iv_controller.process_stage_iv(request) 