import asyncio

from fastapi import Depends, status
from fastapi.responses import JSONResponse

from system.backend.agentic_workflow.app.models.schemas.code_generation_schema import (
    CodeGenerationRequest,
)
from system.backend.agentic_workflow.app.usecases.flutter_code_generation_usecases.stage_i_usecase.stage_i_usecase import (
    FlutterStageIUsecase,
)
from system.backend.agentic_workflow.app.usecases.flutter_code_generation_usecases.stage_ii_usecase.stage_ii_usecase import (
    StageIIUsecase,
)
from system.backend.agentic_workflow.app.usecases.flutter_code_generation_usecases.stage_iii_usecase.stage_iii_usecase import (
    FlutterStageIIIUsecase,
)
from system.backend.agentic_workflow.app.utils.flutter_boilerplate_setup import (
    setup_flutter_boilerplate,
)


class FlutterCodeGenerationUsecase:
    def __init__(
        self,
        stage_i_usecase: FlutterStageIUsecase = Depends(),
        stage_ii_usecase: StageIIUsecase = Depends(),
        stage_iii_usecase: FlutterStageIIIUsecase = Depends(),
    ):
        self.stage_i_usecase = stage_i_usecase
        self.stage_ii_usecase = stage_ii_usecase
        self.stage_iii_usecase = stage_iii_usecase

    async def execute(self, request: CodeGenerationRequest) -> JSONResponse:
        # Wait for Flutter boilerplate setup to complete before proceeding
        await setup_flutter_boilerplate.create_flutter_boilerplate()

        stage_i_result = await self.stage_i_usecase.execute()
        if not stage_i_result["success"]:
            return JSONResponse(
                content={
                    "success": False,
                    "message": stage_i_result["message"],
                    "error": stage_i_result["error"],
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        stage_ii_result = await self.stage_ii_usecase.execute(request)
        if not stage_ii_result["success"]:
            return JSONResponse(
                content={
                    "success": False,
                    "message": stage_ii_result["message"],
                    "error": stage_ii_result["error"],
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        stage_iii_result = await self.stage_iii_usecase.execute(
            request.dict_of_screens, request.is_follow_up
        )
        if not stage_iii_result["success"]:
            return JSONResponse(
                content={
                    "success": False,
                    "message": stage_iii_result["message"],
                    "error": stage_iii_result["error"],
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        return JSONResponse(
            content={
                "success": True,
                "message": "Flutter code generation completed successfully across all stages",
                "data": {
                    "stage_i": stage_i_result,
                    "stage_ii": stage_ii_result,
                    "stage_iii": stage_iii_result,
                },
                "error": None,
            },
            status_code=status.HTTP_200_OK,
        )