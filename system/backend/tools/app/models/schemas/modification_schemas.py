from typing import List, Optional

from pydantic import BaseModel, Field


class SearchReplaceOptions(BaseModel):
    case_sensitive: bool = Field(
        default=True, description="Whether the search should be case sensitive"
    )
    include_pattern: str = Field(
        default="*", description="Glob pattern for files to include"
    )
    exclude_pattern: str = Field(
        default="", description="Glob pattern for files to exclude"
    )
    search_paths: List[str] = Field(
        default=[], description="Paths to search in"
    )


class SearchReplaceRequest(BaseModel):
    query: str = Field(
        ..., description="The text or regex pattern to search for"
    )
    replacement: str = Field(
        ..., description="The text to replace the matched content with"
    )
    options: Optional[SearchReplaceOptions] = Field(
        default=None, description="Search options"
    )
    default_path: str = Field(
        ..., description="The default base path to search in"
    )


class EditFileRequest(BaseModel):
    target_file_path: str = Field(
        ..., description="The absolute path to the file to edit"
    )
    code_snippet: str = Field(..., description="The code snippet to edit")
