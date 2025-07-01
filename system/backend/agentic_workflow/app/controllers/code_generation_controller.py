from fastapi import Depends
from fastapi.responses import JSONResponse

from system.backend.agentic_workflow.app.models.schemas.code_generation_schema import (
    CodeGenerationRequest,
)
from system.backend.agentic_workflow.app.usecases.code_generation_usecases.stage_ii_usecase.stage_ii_usecase import (
    StageIIUsecase,
)


class CodeGenerationController:
    def __init__(
        self,
        stage_ii_usecase: StageIIUsecase = Depends(),
    ):
        self.stage_ii_usecase = stage_ii_usecase

    async def execute(self, request: CodeGenerationRequest) -> JSONResponse:
        """
        Generate code for the given screens

        :param request: CodeGenerationRequest containing user query and options
        :return: JSONResponse with generated code data and individual file paths
        """
        return await self.stage_ii_usecase.execute(request)
