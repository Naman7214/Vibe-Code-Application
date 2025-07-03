import json
from typing import Any, Dict

from fastapi import Depends, HTTPException

from system.backend.agentic_workflow.app.models.domain.error import Error
from system.backend.agentic_workflow.app.prompts.flutter_code_generation_prompts.stage_iii_prompt import (
    SYSTEM_PROMPT,
    USER_PROMPT,
)
from system.backend.agentic_workflow.app.repositories.error_repo import (
    ErrorRepo,
)
from system.backend.agentic_workflow.app.services.anthropic_services.llm_service import (
    AnthropicService,
)
from system.backend.agentic_workflow.app.utils.session_context import (
    session_state,
)
from system.backend.agentic_workflow.app.utils.write_file import (
    write_code_files,
)
from system.backend.agentic_workflow.app.utils.xml_parser import (
    parse_xml_to_dict,
)

from .helper import FlutterStageIIIHelper


class FlutterStageIIIUsecase:
    def __init__(
        self,
        anthropic_service: AnthropicService = Depends(),
        error_repo: ErrorRepo = Depends(),
    ):
        self.anthropic_service = anthropic_service
        self.error_repo = error_repo
        self.helper = FlutterStageIIIHelper()

    async def execute(
        self, screen_dict: Dict[str, str], is_follow_up: bool = False
    ) -> Dict[str, Any]:
        """
        Execute Flutter Stage III processing for code generation
        Generates routes/app_routes.dart file based on screen scratchpads

        Args:
            screen_dict: Dictionary with screen names as keys and descriptions as values
            is_follow_up: Flag indicating if this is a follow-up request

        Returns:
            Dict with success status and message
        """
        try:
            # Get session ID from context variable
            session_id = session_state.get()
            if not session_id:
                raise ValueError("Session ID not found in context")

            # Prepare input context using helper
            context_data = await self.helper.prepare_input_context(
                session_id, screen_dict, is_follow_up
            )

            # Format user prompt with context
            user_prompt = USER_PROMPT.format(
                screen_scratchpads=context_data["screen_scratchpads"],
                existing_routes=context_data.get("existing_routes", ""),
                screen_descriptions=json.dumps(screen_dict, indent=2),
                is_follow_up=str(is_follow_up).lower(),
                codebase_path=context_data["codebase_path"],
            )

            # Make LLM call
            response = await self.anthropic_service.anthropic_client_request(
                prompt=user_prompt, system_prompt=SYSTEM_PROMPT
            )

            # Parse XML response to get file data
            file_data = parse_xml_to_dict(response)

            # Filter out CONTEXT_REGISTRY from files to be written to codebase
            actual_files = [
                file_info
                for file_info in file_data
                if file_info["file_path"] != "CONTEXT_REGISTRY"
            ]

            # Write generated files to codebase (excluding CONTEXT_REGISTRY)
            codebase_path = f"artifacts/{session_id}/codebase"
            write_code_files(actual_files, codebase_path)

            # Update file structure to reflect newly generated files
            await self.helper.update_file_structure(session_id, codebase_path)

            # Update scratchpad files
            await self.helper.update_scratchpads(
                session_id, response, codebase_path
            )

            return {
                "success": True,
                "message": "Flutter Stage III code generation completed successfully",
                "error": None,
                "generated_files": [item["file_path"] for item in actual_files],
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
