from pydantic import BaseModel, Field


class ScreenGenerationRequest(BaseModel):
    user_query: str = Field(
        ..., description="The user query to generate the screens"
    )
    dir_path: str = Field(
        default="context/screens",
        description="The directory path to save the screens",
    )
    base_file_name: str = Field(
        default="screen", description="The base file name to save the screens"
    )
    explanation: str = Field(
        ..., description="The explanation about calling the tool"
    )


class DesignThemeGenerationRequest(BaseModel):
    user_query: str = Field(
        ..., description="The user query to generate the design theme"
    )
    dir_path: str = Field(
        default="context",
        description="The directory path to save the design theme",
    )
    output_file: str = Field(
        default="designTheme.json",
        description="The file name to save the design theme",
    )
    explanation: str = Field(
        ..., description="The explanation about calling the tool"
    )


class NavigationContextGenerationRequest(BaseModel):
    user_query: str = Field(
        ..., description="The user query to generate the navigation context"
    )
    screens_dir: str = Field(
        default="context/screens",
        description="The directory path to the screens",
    )
    dir_path: str = Field(
        default="context",
        description="The directory path to save the navigation context",
    )
    output_file: str = Field(
        default="navigationContext.json",
        description="The file name to save the navigation context",
    )
    explanation: str = Field(
        ..., description="The explanation about calling the tool"
    )
