from fastapi import Depends, status
from fastapi.responses import JSONResponse

from system.backend.agentic_workflow.app.models.schemas.code_generation_schema import (
    CodeGenerationRequest,
)
from system.backend.agentic_workflow.app.usecases.code_generation_usecases.code_generation_usecase import (
    CodeGenerationUsecase,
)


class CodeGenerationController:
    def __init__(
        self,
        code_generation_usecase: CodeGenerationUsecase = Depends(),
    ):
        self.code_generation_usecase = code_generation_usecase

    async def execute(self, request: CodeGenerationRequest) -> JSONResponse:
        """
        Generate code for the given screens

        :param request: CodeGenerationRequest containing user query and options
        :return: JSONResponse with generated code data and individual file paths
        """

        await self.code_generation_usecase.execute(
            request
        )

        return JSONResponse(
            content={
                "data": "None",
                "message": "Code generation completed successfully",
                "error": None,
            },
            status_code=status.HTTP_200_OK,
        )
