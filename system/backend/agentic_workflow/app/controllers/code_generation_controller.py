from fastapi import Depends, status
from fastapi.responses import JSONResponse

from system.backend.agentic_workflow.app.models.schemas.code_generation_schema import (
    CodeGenerationRequest,
)
from system.backend.agentic_workflow.app.usecases.code_generation_usecases.code_generation_usecase import (
    CodeGenerationUsecase,
)
from system.backend.agentic_workflow.app.usecases.flutter_code_generation_usecases.flutter_code_generation_usecase import (
    FlutterCodeGenerationUsecase,
)


class CodeGenerationController:
    def __init__(
        self,
        code_generation_usecase: CodeGenerationUsecase = Depends(),
        flutter_code_generation_usecase: FlutterCodeGenerationUsecase = Depends(),
    ):
        self.code_generation_usecase = code_generation_usecase
        self.flutter_code_generation_usecase = flutter_code_generation_usecase

    async def execute(self, request: CodeGenerationRequest) -> JSONResponse:
        """
        Generate code for the given screens

        :param request: CodeGenerationRequest containing user query and options
        :return: JSONResponse with generated code data and individual file paths
        """
        if request.platform_type == "web":
            return await self.code_generation_usecase.execute(request)
        elif request.platform_type == "mobile":
            print("flutter code generation usecase")
            return await self.flutter_code_generation_usecase.execute(request)
        else:
            return JSONResponse(
                content={
                    "success": False,
                    "message": f"Unsupported platform type: {request.platform_type}",
                    "error": "Invalid platform type specified",
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            )
