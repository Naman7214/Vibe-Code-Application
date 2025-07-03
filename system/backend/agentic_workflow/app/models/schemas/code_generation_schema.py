from typing import Any, Dict

from pydantic import BaseModel, Field


class CodeGenerationRequest(BaseModel):
    is_follow_up: bool = Field(
        ..., description="Whether the request is a follow-up request"
    )
    dict_of_screens: Dict[str, Any] = Field(
        ..., description="The list of screens to generate the code"
    )
    platform_type: str = Field(
        default="web", description="The platform type to generate the code"
    )
