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

from .helper import (
    get_stage_file_path,
    read_stage_data,
    update_screens_data,
    write_stage_data,
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

            # Get the file path for stage_i.json
            stage_file_path = get_stage_file_path(session_id)

            # Read existing stage_i.json data
            stage_data = read_stage_data(stage_file_path)

            # Update screens based on is_follow_up flag
            updated_stage_data = update_screens_data(
                stage_data, request.dict_of_screens, request.is_follow_up
            )

            # Save updated data back to file
            write_stage_data(stage_file_path, updated_stage_data)

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
        except Exception as e:
            await self.error_repo.insert_error(
                Error(
                    phase="stage_i",
                    error_message="Error in the stage i of context gathering usecase: "
                    + str(e),
                    stack_trace=str(e),
                )
            )

            return {
                "success": False,
                "message": "Error in the stage i of context gathering usecase: "
                + str(e),
                "error": str(e),
            }
