from typing import Any, Dict

from fastapi import Depends, HTTPException

from system.backend.agentic_workflow.app.models.domain.error import Error
from system.backend.agentic_workflow.app.models.schemas.code_generation_schema import (
    CodeGenerationRequest,
)
from system.backend.agentic_workflow.app.repositories.error_repo import (
    ErrorRepo,
)
from system.backend.agentic_workflow.app.utils.session_context import (
    session_state,
)

from .helper import StageIIHelper


class StageIIUsecase:
    def __init__(
        self,
        helper: StageIIHelper = Depends(),
        error_repo: ErrorRepo = Depends(),
    ):
        self.helper = helper
        self.error_repo = error_repo

    async def execute(self, request: CodeGenerationRequest) -> Dict[str, Any]:
        """
        Execute Stage II code generation usecase for global components builder

        :param request: CodeGenerationRequest containing is_follow_up flag and screens data
        :return: Dict with success status, message, and error information
        """
        try:
            # Get session_id from context (set by middleware)
            session_id = session_state.get()
            if not session_id:
                raise ValueError("No session_id available in context")

            # Case 2: Skip processing if this is a follow-up request
            if request.is_follow_up:
                return {
                    "success": True,
                    "message": "Stage II skipped for follow-up request",
                    "error": None,
                }

            # Case 1: Process global components generation for initial request
            result = await self.helper.execute_stage_ii_pipeline(session_id)

            if not result["success"]:
                # Log error but don't raise exception, return the error result
                await self.error_repo.insert_error(
                    Error(
                        phase="stage_ii_code_generation",
                        error_message=f"Stage II pipeline failed: {result['message']}",
                        stack_trace=None,
                    )
                )
                return result

            return {
                "success": True,
                "message": "Stage II global components generation completed successfully",
                "error": None,
            }

        except ValueError as e:
            error_message = (
                f"Validation error in stage II code generation: {str(e)}"
            )
            await self.error_repo.insert_error(
                Error(
                    phase="stage_ii_code_generation",
                    error_message=error_message,
                    stack_trace=None,
                )
            )
            return {
                "success": False,
                "message": error_message,
                "error": str(e),
            }

        except HTTPException as e:
            error_message = (
                f"HTTP error in stage II code generation: {str(e.detail)}"
            )
            await self.error_repo.insert_error(
                Error(
                    phase="stage_ii_code_generation",
                    error_message=error_message,
                    stack_trace=e.with_traceback(),
                )
            )
            return {
                "success": False,
                "message": error_message,
                "error": e.detail,
            }

        except Exception as e:
            error_message = (
                f"Unexpected error in stage II code generation: {str(e)}"
            )
            await self.error_repo.insert_error(
                Error(
                    phase="stage_ii_code_generation",
                    error_message=error_message,
                    stack_trace=None,
                )
            )
            return {
                "success": False,
                "message": error_message,
                "error": str(e),
            }
