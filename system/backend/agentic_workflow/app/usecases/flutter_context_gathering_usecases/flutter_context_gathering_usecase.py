from fastapi import Depends, status
from fastapi.responses import JSONResponse

from system.backend.agentic_workflow.app.models.schemas.context_gathering_schema import (
    ContextGatheringRequest,
)
# Stage I is directly reusable since it's platform-agnostic
from system.backend.agentic_workflow.app.usecases.context_gathering_usecases.stage_i_usecase.stage_i_usecase import (
    StageIUsecase,
)
from system.backend.agentic_workflow.app.usecases.flutter_context_gathering_usecases.stage_ii_usecase.flutter_stage_ii_usecase import (
    FlutterStageIIUsecase,
)
from system.backend.agentic_workflow.app.usecases.flutter_context_gathering_usecases.stage_iii_usecase.flutter_stage_iii_usecase import (
    FlutterStageIIIUsecase,
)
from system.backend.agentic_workflow.app.usecases.flutter_context_gathering_usecases.stage_iv_usecase.flutter_stage_iv_usecase import (
    FlutterStageIVUsecase,
)
from system.backend.agentic_workflow.app.usecases.flutter_context_gathering_usecases.stage_v_usecase.flutter_stage_v_usecase import (
    FlutterStageVUsecase,
)


class FlutterContextGatheringUsecase:
    def __init__(
        self,
        stage_i_usecase: StageIUsecase = Depends(),  # Reusing original Stage I
        stage_ii_usecase: FlutterStageIIUsecase = Depends(),
        stage_iii_usecase: FlutterStageIIIUsecase = Depends(),
        stage_iv_usecase: FlutterStageIVUsecase = Depends(),
        stage_v_usecase: FlutterStageVUsecase = Depends(),
    ):
        self.stage_i_usecase = stage_i_usecase
        self.stage_ii_usecase = stage_ii_usecase
        self.stage_iii_usecase = stage_iii_usecase
        self.stage_iv_usecase = stage_iv_usecase
        self.stage_v_usecase = stage_v_usecase

    async def execute(self, request: ContextGatheringRequest) -> JSONResponse:
        """
        Execute the complete Flutter context gathering pipeline
        """

        # Execute all stages sequentially with error handling
        
        stage_i_result = await self.stage_i_usecase.execute(request)
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

        # Stage IV: Screen Detailed Planning (Flutter-specific)
        stage_iv_result = await self.stage_iv_usecase.execute(
            request.dict_of_screens
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

        # Stage V: Navigation & State (Flutter-specific)
        stage_v_result = await self.stage_v_usecase.execute(request)
        if not stage_v_result["success"]:
            return JSONResponse(
                content={
                    "success": False,
                    "message": stage_v_result["message"],
                    "error": stage_v_result["error"],
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        return JSONResponse(
            content={
                "success": True,
                "message": "Flutter context gathering pipeline completed successfully",
                "error": None,
            },
            status_code=status.HTTP_200_OK,
        ) 