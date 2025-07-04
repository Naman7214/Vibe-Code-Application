from typing import Optional

from pydantic import BaseModel, Field


class RunTerminalCommandRequest(BaseModel):
    cmd: str = Field(..., description="The command to run")
    is_background: bool = Field(
        ..., description="Whether to run the command in the background"
    )
    explanation: str = Field(
        ..., description="The explanation for the terminal command request"
    )
    default_path: Optional[str] = Field(
        default=None,
        description="The default working directory for the command",
    )
