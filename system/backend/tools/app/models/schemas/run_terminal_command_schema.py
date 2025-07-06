from pydantic import BaseModel, Field


class RunTerminalCommandRequest(BaseModel):
    cmd: str = Field(..., description="The command to run")
    is_background: bool = Field(
        default=False,
        description="Whether to run the command in the background default is false",
    )
    default_path: str = Field(
        ...,
        description="The default working directory for the command",
    )
