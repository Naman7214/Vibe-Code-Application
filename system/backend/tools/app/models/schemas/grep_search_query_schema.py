from pydantic import BaseModel, Field


class GrepSearchQueryRequest(BaseModel):
    query: str = Field(..., description="The query to search for")
    case_sensitive: bool = Field(
        default=False, description="Whether to search case-sensitively"
    )
    include_pattern: str | None = Field(
        default="*", description="The pattern to include in the search"
    )
    exclude_pattern: str | None = Field(
        default="", description="The pattern to exclude in the search"
    )
    default_path: str = Field(
        ..., description="The default base path to search in"
    )
