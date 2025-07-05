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

    def _create_simple_error_message(self, validation_results):
        """
        Create a simple error message containing only the command and error
        
        Args:
            validation_results: List of validation command results
            
        Returns:
            Simple error string with command and error details
        """
        error_commands = []
        for result in validation_results:
            if result["has_errors"]:
                command = result["command"]
                error_message = result["error_details"]["message"]
                raw_output = result["error_details"].get("raw_output", "")
                
                # For Flutter builds, use the specialized error extraction if the original message is generic
                if ("flutter build" in command and 
                    (error_message in ["error during build:", "No specific error message found"] or 
                     len(error_message.strip()) < 20) and raw_output):
                    
                    # Use the helper's Flutter error extraction
                    if ("Target dart2js failed" in raw_output or "Error: Compilation failed" in raw_output):
                        error_message = self.helper._extract_flutter_compilation_errors(raw_output)
                    
                # For other commands, try to extract better details from raw output
                elif ((error_message in ["error during build:", "No specific error message found"] or 
                       len(error_message.strip()) < 20) and raw_output):
                    
                    # Look for more specific error information in raw output
                    lines = raw_output.split("\n")
                    better_error = None
                    
                    for i, line in enumerate(lines):
                        line = line.strip()
                        # Look for vite/webpack/build tool specific errors
                        if any(pattern in line for pattern in [
                            "Error: [vite]", "Error: [webpack]", "Failed to resolve", 
                            "Cannot resolve", "Module not found", "Rollup failed"
                        ]):
                            # Include this line and next few lines for context
                            error_lines = [line]
                            for j in range(i + 1, min(i + 3, len(lines))):
                                next_line = lines[j].strip()
                                if next_line and not next_line.startswith("at ") and len(next_line) > 5:
                                    error_lines.append(next_line)
                            better_error = "\n".join(error_lines)
                            break
                    
                    if better_error:
                        error_message = better_error
                
                error_commands.append(f"Command: {command}\nError: {error_message}")
        
        return "\n\n".join(error_commands) if error_commands else "Validation errors detected"

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
                # Return simplified error format
                simple_error = self._create_simple_error_message(validation_results)
                return {
                    "success": False,
                    "message": "Code validation failed with errors",
                    "error": simple_error,
                }
            else:
                return {
                    "success": True,
                    "message": "Code validation completed successfully - no errors found",
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
                "error": str(e.detail),
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
