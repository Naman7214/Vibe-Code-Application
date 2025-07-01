from pydantic import BaseModel, Field


class InitialProcessingRequest(BaseModel):
    user_query: str = Field(
        ..., description="The user query to generate the context"
    )
    platform_type: str = Field(
        ..., description="The platform type to generate the context"
    )
