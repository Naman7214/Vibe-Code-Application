from typing import Dict
from pydantic import BaseModel, Field


class StageIVRequest(BaseModel):
    """Request schema for Stage IV processing"""
    
    screen_data: Dict[str, str] = Field(
        ...,
        description="Dictionary with screen names as keys and descriptions as values",
        example={
            "Homepage": "Landing page with hero section and featured products",
            "Menu": "Product catalog with filtering and search functionality",
            "Order": "Shopping cart and checkout process"
        }
    )


class StageIVResponse(BaseModel):
    """Response schema for Stage IV processing"""
    
    message: str = Field(
        ...,
        description="Status message indicating successful processing"
    )
    
    screen_data: Dict[str, str] = Field(
        ...,
        description="The original screen data that was processed"
    )
    
    session_id: str = Field(
        ...,
        description="Session ID used for processing"
    )
    
    output_file: str = Field(
        ...,
        description="Path to the generated stage_iv.json file"
    ) 