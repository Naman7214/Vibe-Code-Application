from typing import Any, Dict
from pydantic import BaseModel, Field

class CodeGenerationRequest(BaseModel):
    user_query: str = Field(
        ..., description="The user query to generate the code"
    )
    platform_type: str = Field(
        ..., description="The platform type to generate the code"
    )
    dict_of_screens: Dict[str, Any] = Field(
        ..., description="The list of screens to generate the code"
    )

class CodeGenerationStageIRequest(BaseModel):
    """
    Request for Stage I code generation.
    Session ID should be sent in X-Session-ID header.
    """
    pass
    
    class Config:
        json_schema_extra = {
            "example": {}
        }