from pydantic import BaseModel, Field


class RunTerminalCommandRequest(BaseModel):
    cmd: str = Field(..., description="The command to run")
    is_background: bool = Field(
        ..., description="Whether to run the command in the background"
    )
    default_path: str = Field(
        ...,
        description="The default working directory for the command",
    )
