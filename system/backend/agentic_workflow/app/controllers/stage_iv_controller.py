from fastapi import HTTPException, Depends
from typing import Dict

from system.backend.agentic_workflow.app.models.schemas.stage_iv_schema import (
    StageIVRequest, 
    StageIVResponse
)
from system.backend.agentic_workflow.app.usecases.context_gathering_usecases.stage_iv_usecase.stage_iv_usecase import (
    StageIVUsecase
)
from system.backend.agentic_workflow.app.utils.session_context import session_state
from system.backend.agentic_workflow.app.utils.logger import loggers


class StageIVController:
    def __init__(self, stage_iv_usecase: StageIVUsecase = Depends()):
        self.stage_iv_usecase = stage_iv_usecase

    async def process_stage_iv(self, request: StageIVRequest) -> StageIVResponse:
        """
        Process Stage IV request through the usecase
        
        Args:
            request: StageIVRequest containing screen data
            
        Returns:
            StageIVResponse with processing results
            
        Raises:
            HTTPException: If processing fails
        """
        try:
            # Get session ID from context
            session_id = session_state.get()
            if not session_id:
                raise HTTPException(
                    status_code=400, 
                    detail="Session ID not found in request context"
                )


            # Execute the usecase
            result = await self.stage_iv_usecase.execute(request.screen_data)

            # Construct output file path
            output_file = f"artifacts/{session_id}/project_context/stage_iv.json"


            return StageIVResponse(
                message="Stage IV processing completed successfully",
                screen_data=result,
                session_id=session_id,
                output_file=output_file
            )

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Stage IV processing failed: {str(e)}"
            ) 