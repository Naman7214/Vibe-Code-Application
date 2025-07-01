from typing import Any, Dict

from pydantic import BaseModel, Field


class ContextGatheringRequest(BaseModel):
    user_query: str = Field(
        ..., description="The user query to generate the context"
    )
    platform_type: str = Field(
        ..., description="The platform type to generate the context"
    )
    session_id: str = (
        Field(..., description="The session id to generate the context"),
    )
    is_follow_up: bool = (
        Field(..., description="Whether the request is a follow-up request"),
    )
    dict_of_screens: Dict[str, Any] = Field(
        ..., description="The list of screens to generate the context"
    )
