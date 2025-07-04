import asyncio

from fastapi import Depends, status
from fastapi.responses import JSONResponse

from system.backend.agentic_workflow.app.models.schemas.code_generation_schema import (
    CodeGenerationRequest,
)
from system.backend.agentic_workflow.app.usecases.code_generation_usecases.stage_i_usecase.stage_i_usecase import (
    StageIUsecase,
)
from system.backend.agentic_workflow.app.usecases.code_generation_usecases.stage_ii_usecase.stage_ii_usecase import (
    StageIIUsecase,
)
from system.backend.agentic_workflow.app.usecases.code_generation_usecases.stage_iii_usecase.stage_iii_usecase import (
    StageIIIUsecase,
)
from system.backend.agentic_workflow.app.usecases.code_generation_usecases.stage_iv_usecase.stage_iv_usecase import (
    StageIVUsecase,
)
from system.backend.agentic_workflow.app.usecases.code_generation_usecases.stage_v_usecase.stage_v_usecase import (
    StageVUsecase,
)
from system.backend.agentic_workflow.app.utils.react_boilerplate_setup import (
    setup_react_boilerplate,
)


class CodeGenerationUsecase:
    def __init__(
        self,
        stage_i_usecase: StageIUsecase = Depends(),
        stage_ii_usecase: StageIIUsecase = Depends(),
        stage_iii_usecase: StageIIIUsecase = Depends(),
        stage_iv_usecase: StageIVUsecase = Depends(),
        stage_v_usecase: StageVUsecase = Depends(),
    ):
        self.stage_i_usecase = stage_i_usecase
        self.stage_ii_usecase = stage_ii_usecase
        self.stage_iii_usecase = stage_iii_usecase
        self.stage_iv_usecase = stage_iv_usecase
        self.stage_v_usecase = stage_v_usecase

    async def execute(self, request: CodeGenerationRequest) -> JSONResponse:

        # Run React boilerplate setup in background without blocking
        asyncio.create_task(setup_react_boilerplate.create_react_boilerplate())

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

        stage_iii_result = await self.stage_iii_usecase.execute(request)
        if not stage_iii_result["success"]:
            return JSONResponse(
                content={
                    "success": False,
                    "message": stage_iii_result["message"],
                    "error": stage_iii_result["error"],
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        stage_iv_result = await self.stage_iv_usecase.execute(
            request.dict_of_screens, request.is_follow_up
        )
        if not stage_iv_result["success"]:
            return JSONResponse(
                content={
                    "success": False,
                    "message": stage_iv_result["message"],
                    "error": stage_iv_result["error"],
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        stage_v_result = await self.stage_v_usecase.execute(request)

        if not stage_v_result["success"]:
            return JSONResponse(
                content={
                    "success": False,
                    "message": stage_v_result["message"],
                    "error": stage_v_result["error"],
                    "validation_details": stage_v_result.get("data", {}),
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        return JSONResponse(
            content={
                "success": True,
                "message": "Code generation and validation completed successfully across all stages",
                "data": {
                    "stage_i": stage_i_result,
                    "stage_ii": stage_ii_result,
                    "stage_iii": stage_iii_result,
                    "stage_iv": stage_iv_result,
                    "stage_v": stage_v_result,
                },
                "error": None,
            },
            status_code=status.HTTP_200_OK,
        )
