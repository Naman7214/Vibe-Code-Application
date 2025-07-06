from typing import Any, Dict
import os

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
from system.backend.agentic_workflow.app.utils.flutter_routes_generator import (
    generate_flutter_routes_for_project,
)

from .helper import FlutterStageIIIHelper


class FlutterStageIIIUsecase:
    def __init__(
        self,
        error_repo: ErrorRepo = Depends(),
    ):
        self.error_repo = error_repo
        self.helper = FlutterStageIIIHelper()

    async def execute(
        self, request: CodeGenerationRequest
    ) -> Dict[str, Any]:
        """
        Execute Flutter Stage III processing for code generation
        Generates routes/app_routes.dart file using heuristic analysis of the presentation structure

        Args:
            request: CodeGenerationRequest object containing screen dict and follow-up flag

        Returns:
            Dict with success status and message
        """
        try:
            # Extract data from request
            screen_dict = request.dict_of_screens
            is_follow_up = request.is_follow_up
            
            # Get session ID from context variable
            session_id = session_state.get()
            if not session_id:
                raise ValueError("Session ID not found in context")

            # Use heuristic Flutter routes generator
            codebase_path = f"artifacts/{session_id}/codebase"
            lib_path = f"{codebase_path}/lib"
            routes_dir = f"{lib_path}/routes"
            routes_file_path = f"{routes_dir}/app_routes.dart"

            # Ensure routes directory exists
            os.makedirs(routes_dir, exist_ok=True)

            # Generate routes using the heuristic generator
            routes_content, analysis = generate_flutter_routes_for_project(
                lib_path=lib_path,
                output_path=routes_file_path
            )

            # Create context registry content
            context_registry_content = self.helper.generate_context_registry(analysis)

            # Update file structure to reflect newly generated files
            await self.helper.update_file_structure(session_id, codebase_path)

            # Update scratchpad files with the generated content
            await self.helper.update_scratchpads_with_generated_content(
                session_id, routes_content, context_registry_content, codebase_path
            )

            return {
                "success": True,
                "message": "Flutter Stage III code generation completed successfully using heuristic routes generator",
                "error": None,
                "generated_files": ["lib/routes/app_routes.dart"],
                "analysis": analysis,
            }

        except HTTPException as e:
            await self.error_repo.insert_error(
                Error(
                    phase="flutter_code_generation_stage_iii",
                    error_message="Error in Flutter Stage III code generation usecase: "
                    + str(e.detail),
                    stack_trace=e.with_traceback(),
                )
            )
            return {
                "success": False,
                "message": "Error in Flutter Stage III code generation usecase: "
                + str(e.detail),
                "error": e.detail,
            }
        except Exception as e:
            await self.error_repo.insert_error(
                Error(
                    phase="flutter_code_generation_stage_iii",
                    error_message="Unexpected error in Flutter Stage III code generation usecase: "
                    + str(e),
                    stack_trace=str(e),
                )
            )
            return {
                "success": False,
                "message": "Unexpected error in Flutter Stage III code generation usecase: "
                + str(e),
                "error": str(e),
            }


