import os
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

from .helper import StageVHelper


class StageVUsecase:
    def __init__(
        self,
        error_repo: ErrorRepo = Depends(),
    ):
        self.error_repo = error_repo
        self.helper = StageVHelper()

    async def execute(self, request: CodeGenerationRequest) -> Dict[str, Any]:
        """
        Execute Stage V processing for code generation validation
        Runs multiple commands (build, lint, test, etc.) to detect syntax and logical errors

        Args:
            request: CodeGenerationRequest containing platform_type and other details

        Returns:
            Dict with success status, validation results, and error details if any
        """
        try:
            # Get session ID from context variable
            session_id = session_state.get()
            if not session_id:
                raise ValueError("Session ID not found in context")

            # Get platform type from request
            platform_type = request.platform_type

            # Prepare codebase path
            codebase_path = f"artifacts/{session_id}/codebase"

            # Check if codebase exists
            if not os.path.exists(codebase_path):
                raise FileNotFoundError(
                    f"Codebase not found at {codebase_path}"
                )

            # Get validation commands based on platform type
            validation_commands = await self.helper.get_validation_commands(
                platform_type
            )

            # Execute validation commands in chronological order
            validation_results = []
            has_errors = False

            for command_info in validation_commands:
                try:
                    result = await self.helper.execute_validation_command(
                        command_info, codebase_path
                    )
                    validation_results.append(result)

                    # Check if this command had errors
                    if result["status"] == "error" or result["has_errors"]:
                        has_errors = True

                except Exception as e:
                    # Command execution failed
                    error_result = {
                        "command": command_info["command"],
                        "description": command_info["description"],
                        "status": "failed",
                        "has_errors": True,
                        "error_details": {
                            "type": "execution_error",
                            "message": str(e),
                            "raw_output": "",
                            "parsed_errors": [],
                        },
                        "execution_time": 0,
                    }
                    validation_results.append(error_result)
                    has_errors = True

            # Create summary of results
            summary = await self.helper.create_validation_summary(
                validation_results, has_errors
            )

            # Update scratchpad with validation results
            await self.helper.update_scratchpads(
                session_id, validation_results, summary
            )

            if has_errors:
                return {
                    "success": False,
                    "message": "Code validation failed with errors",
                    "data": {
                        "validation_results": validation_results,
                        "summary": summary,
                        "codebase_path": codebase_path,
                        "platform_type": platform_type,
                    },
                    "error": "Validation errors detected in generated code",
                }
            else:
                return {
                    "success": True,
                    "message": "Code validation completed successfully - no errors found",
                    "data": {
                        "validation_results": validation_results,
                        "summary": summary,
                        "codebase_path": codebase_path,
                        "platform_type": platform_type,
                    },
                    "error": None,
                }

        except HTTPException as e:
            await self.error_repo.insert_error(
                Error(
                    phase="code_generation_stage_v",
                    error_message="Error in Stage V code validation usecase: "
                    + str(e.detail),
                    stack_trace=str(e),
                )
            )
            return {
                "success": False,
                "message": "Error in Stage V code validation usecase: "
                + str(e.detail),
                "error": e.detail,
            }
        except Exception as e:
            await self.error_repo.insert_error(
                Error(
                    phase="code_generation_stage_v",
                    error_message="Unexpected error in Stage V code validation usecase: "
                    + str(e),
                    stack_trace=str(e),
                )
            )
            return {
                "success": False,
                "message": "Unexpected error in Stage V code validation usecase: "
                + str(e),
                "error": str(e),
            }
