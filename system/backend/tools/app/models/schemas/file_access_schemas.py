from typing import Optional

from pydantic import BaseModel, Field


class FileReadRequest(BaseModel):
    file_path: str = Field(
        ..., description="The absolute path to the file to read"
    )
    start_line: int = Field(
        default=0, description="The line number to start reading from"
    )
    end_line: int = Field(
        default=1500, description="The line number to stop reading at"
    )


class FilesDeleteRequest(BaseModel):
    path: str = Field(
        ..., description="The absolute path to the file to delete"
    )


class DirectoryListRequest(BaseModel):
    dir_path: str = Field(
        default="",
        description="The path to the directory to list, relative to default_path if provided",
    )
    recursive: bool = Field(
        default=True, description="Whether to list subdirectories recursively"
    )
    default_path: Optional[str] = Field(
        default=None,
        description="The default base path to use if dir_path is relative",
    )


class FileSearchRequest(BaseModel):
    pattern: str = Field(
        ..., description="The pattern to search for in file names"
    )
    default_path: str = Field(
        ..., description="The default base path to search in"
    )


class ExitToolRequest(BaseModel):
    file_path: str = Field(
        ...,
        description="The absolute path to the .txt file to append content to",
    )
    summary: str = Field(
        ..., description="The summary of what was done by the AI agent"
    )
    explanation: str = Field(
        ..., description="The explanation for the exit tool request"
    )
