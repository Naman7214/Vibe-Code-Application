import json
import logging
import os
from typing import Any, Dict

from fastapi import Depends, HTTPException

from system.backend.agentic_workflow.app.models.domain.error import Error
from system.backend.agentic_workflow.app.models.schemas.code_generation_schema import (
    CodeGenerationRequest,
)
from system.backend.agentic_workflow.app.prompts.code_generation_prompts.stage_iv_prompt import (
    SYSTEM_PROMPT,
    USER_PROMPT,
)
from system.backend.agentic_workflow.app.repositories.error_repo import (
    ErrorRepo,
)
from system.backend.agentic_workflow.app.services.anthropic_services.llm_service import (
    AnthropicService,
)
from system.backend.agentic_workflow.app.utils.routes_generator import (
    generate_routes_for_project,
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

from .helper import StageIVHelper


class StageIVUsecase:
    def __init__(
        self,
        anthropic_service: AnthropicService = Depends(),
        error_repo: ErrorRepo = Depends(),
    ):
        self.anthropic_service = anthropic_service
        self.error_repo = error_repo
        self.helper = StageIVHelper()

        # Set up logger for debugging
        self.logger = logging.getLogger("code_generation_stage_iv")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    async def execute(self, request: CodeGenerationRequest) -> Dict[str, Any]:
        """
        Execute Stage IV processing for code generation
        Generates Routes.jsx file based on screen scratchpads

        Args:
            request: CodeGenerationRequest object containing screen dict and follow-up flag

        Returns:
            Dict with success status and message
        """
        try:
            # Extract data from request
            screen_dict = request.dict_of_screens
            is_follow_up = request.is_follow_up

            # Debug: Log what we received
            self.logger.info(
                f"Stage IV received screen_dict type: {type(screen_dict)}"
            )
            self.logger.info(f"Stage IV received is_follow_up: {is_follow_up}")

            # Debug: Check each item in screen_dict
            for key, value in screen_dict.items():
                self.logger.info(
                    f"screen_dict['{key}'] = {type(value)}: {str(value)[:100]}..."
                )
                if hasattr(value, "__dict__"):
                    self.logger.error(
                        f"Non-serializable object found in screen_dict['{key}']: {type(value)}"
                    )

            # Get session ID from context variable
            session_id = session_state.get()
            if not session_id:
                raise ValueError("Session ID not found in context")

            # Use heuristic routes generator first
            codebase_path = f"artifacts/{session_id}/codebase"
            src_path = f"{codebase_path}/src"
            routes_file_path = f"{src_path}/Routes.jsx"

            # Ensure src directory exists
            os.makedirs(src_path, exist_ok=True)

            # Generate routes using the heuristic generator
            routes_content, analysis = generate_routes_for_project(
                src_path=src_path, output_path=routes_file_path
            )

            # Create context registry content
            context_registry_content = self.helper.generate_context_registry(
                analysis
            )

            # Update file structure to reflect newly generated files
            await self.helper.update_file_structure(session_id, codebase_path)

            # Update scratchpad files with the generated content
            await self.helper.update_scratchpads_with_routes_generation(
                session_id,
                routes_content,
                context_registry_content,
                codebase_path,
            )

            # Prepare input context using helper
            context_data = await self.helper.prepare_input_context(
                session_id, screen_dict, is_follow_up
            )

            # Debug: Try JSON serialization before using it in prompt
            try:
                screen_descriptions_json = json.dumps(screen_dict, indent=2)
                self.logger.info("JSON serialization of screen_dict successful")
            except TypeError as e:
                self.logger.error(f"JSON serialization failed: {e}")
                # Create a safe version for JSON serialization
                safe_screen_dict = {}
                for key, value in screen_dict.items():
                    if isinstance(
                        value, (str, int, float, bool, list, dict, type(None))
                    ):
                        safe_screen_dict[key] = value
                    else:
                        safe_screen_dict[key] = str(value)
                screen_descriptions_json = json.dumps(
                    safe_screen_dict, indent=2
                )
                self.logger.info(
                    "Using safe version of screen_dict for JSON serialization"
                )

            # Format user prompt with context
            user_prompt = USER_PROMPT.format(
                screen_scratchpads=context_data["screen_scratchpads"],
                global_scratchpad=context_data["global_scratchpad"],
                file_structure=context_data["file_structure"],
                existing_routes=context_data.get("existing_routes", ""),
                screen_descriptions=screen_descriptions_json,
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
                "message": "Stage IV code generation completed successfully using heuristic routes generator",
                "error": None,
                "generated_files": [item["file_path"] for item in actual_files]
                + ["src/Routes.jsx"],
                "analysis": analysis,
            }

        except HTTPException as e:
            await self.error_repo.insert_error(
                Error(
                    phase="code_generation_stage_iv",
                    error_message="Error in Stage IV code generation usecase: "
                    + str(e.detail),
                    stack_trace=e.with_traceback(),
                )
            )
            return {
                "success": False,
                "message": "Error in Stage IV code generation usecase: "
                + str(e.detail),
                "error": e.detail,
            }
        except Exception as e:
            await self.error_repo.insert_error(
                Error(
                    phase="code_generation_stage_iv",
                    error_message="Unexpected error in Stage IV code generation usecase: "
                    + str(e),
                    stack_trace=str(e),
                )
            )
            return {
                "success": False,
                "message": "Unexpected error in Stage IV code generation usecase: "
                + str(e),
                "error": str(e),
            }
