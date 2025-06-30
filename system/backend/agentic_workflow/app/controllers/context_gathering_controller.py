from fastapi import Depends, status
from fastapi.responses import JSONResponse
from system.backend.agentic_workflow.app.usecases.context_gathering_usecase.stage_ii_usecase.stage_ii_usecase import StageIIUsecase
from system.backend.agentic_workflow.app.models.schemas.context_gathering_schema import ContextGatheringRequest

class ContextGatheringController:
    def __init__(
        self, 
        stage_ii_usecase: StageIIUsecase = Depends()
    ):
        self.stage_ii_usecase = stage_ii_usecase

    async def execute(self, request: ContextGatheringRequest) -> JSONResponse:
        """
        Generate screens based on user query and save each screen individually
        
        :param request: ScreenGenerationRequest containing user query and options
        :return: JSONResponse with generated screens data and individual file paths
        """
        dict_of_screens = {}
        
        stage_ii_result = await self.stage_ii_usecase.execute(request, dict_of_screens)
        
        if stage_ii_result["success"]:
            pass
            
        return JSONResponse(
            content={
                "data": stage_ii_result,
                "message": "Context gathering completed successfully",
                "error": None,
            },
            status_code=status.HTTP_200_OK,
        )