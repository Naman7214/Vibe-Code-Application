from typing import Optional

from pydantic import BaseModel, Field


class GrepSearchQueryRequest(BaseModel):
    query: str = Field(..., description="The query to search for")
    case_sensitive: bool = Field(
        default=False, description="Whether to search case-sensitively"
    )
    include_pattern: str | None = Field(
        default=None, description="The pattern to include in the search"
    )
    exclude_pattern: str | None = Field(
        default=None, description="The pattern to exclude in the search"
    )
    explanation: str = Field(
        ..., description="The explanation for the grep search request"
    )
    default_path: Optional[str] = Field(
        default=None, description="The default base path to search in"
    )
