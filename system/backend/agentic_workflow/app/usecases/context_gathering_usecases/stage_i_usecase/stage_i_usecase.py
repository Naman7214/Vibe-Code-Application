import json
import os

from fastapi import Depends, HTTPException

from system.backend.agentic_workflow.app.models.domain.error import Error
from system.backend.agentic_workflow.app.models.schemas.context_gathering_schema import (
    ContextGatheringRequest,
)
from system.backend.agentic_workflow.app.repositories.error_repo import (
    ErrorRepo,
)
from system.backend.agentic_workflow.app.utils.session_context import (
    session_state,
)


class StageIUsecase:
    def __init__(self, error_repo: ErrorRepo = Depends()):
        self.error_repo = error_repo

    async def execute(self, request: ContextGatheringRequest) -> dict:
        """
        Handle context gathering for Stage I - updating screens based on user selection

        :param request: ContextGatheringRequest containing user selections
        :return: Dict with updated context data and metadata
        """
        try:
            # Get session_id from context (set by middleware)
            session_id = session_state.get()
            if not session_id:
                raise ValueError("No session_id available in context")

            # Path to stage_i.json file
            stage_file_path = (
                f"artifacts/{session_id}/project_context/stage_i.json"
            )

            # Check if stage_i.json exists
            if not os.path.exists(stage_file_path):
                raise FileNotFoundError(
                    f"Stage I file not found: {stage_file_path}"
                )

            # Read existing stage_i.json data
            with open(stage_file_path, "r") as f:
                stage_data = json.load(f)

            # Update screens based on is_follow_up flag
            if not request.is_follow_up:
                # Replace screens field with dict_of_screens
                stage_data["screens"] = request.dict_of_screens
            else:
                # Append dict_of_screens to existing screens field
                if "screens" not in stage_data:
                    stage_data["screens"] = {}
                stage_data["screens"].update(request.dict_of_screens)

            # Save updated data back to file
            with open(stage_file_path, "w") as f:
                json.dump(stage_data, f, indent=2)

            # Return result with metadata
            return {
                "success": True,
                "message": "Stage I completed successfully",
                "error": None,
            }
        except HTTPException as e:
            await self.error_repo.insert_error(
                Error(
                    phase="stage_i",
                    error_message="Error in the stage i of context gathering usecase: "
                    + str(e.detail),
                    stack_trace=e.with_traceback(),
                )
            )

            return {
                "success": False,
                "message": "Error in the stage i of context gathering usecase: "
                + str(e.detail),
                "error": e.detail,
            }
