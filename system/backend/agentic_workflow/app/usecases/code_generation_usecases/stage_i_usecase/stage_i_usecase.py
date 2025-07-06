import json
from typing import Dict

from fastapi import Depends, HTTPException

from system.backend.agentic_workflow.app.models.domain.error import Error
from system.backend.agentic_workflow.app.prompts.code_generation_prompts.stage_i_prompt import (
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

from .helper import StageIHelper


class StageIUsecase:
    def __init__(
        self,
        anthropic_service: AnthropicService = Depends(),
        error_repo: ErrorRepo = Depends(),
    ):
        self.anthropic_service = anthropic_service
        self.error_repo = error_repo
        self.helper = StageIHelper()

    async def execute(self) -> Dict[str, str]:
        """
        Execute Stage I processing for code generation
        Generates tailwind.css and tailwind.config.js files based on project context

        Returns:
            Dict with success status and message
        """
        try:
            # Get session ID from context variable
            session_id = session_state.get()
            if not session_id:
                raise ValueError("Session ID not found in context")

            # Prepare input context
            context_data = await self.helper.prepare_input_context(session_id)

            # Format user prompt with context
            user_prompt = USER_PROMPT.format(
                stage_iii_a_context=json.dumps(
                    context_data["stage_iii_a"], indent=None
                ),
                stage_iv_a_context=json.dumps(
                    context_data["stage_iv_a"], indent=None
                ),
                postcss_config=context_data["postcss_config"],
                package_json=json.dumps(
                    context_data["package_json"], indent=None
                ),
                codebase_path=context_data["codebase_path"],
            )

            # Make LLM call
            response = await self.anthropic_service.anthropic_client_request(
                prompt=user_prompt, system_prompt=SYSTEM_PROMPT
            )

            # Parse XML response to get file data
            file_data = parse_xml_to_dict(response)

            # Write generated files to codebase
            codebase_path = f"artifacts/{session_id}/codebase"
            write_code_files(file_data, codebase_path)

            # Update scratchpad files
            await self.helper.update_scratchpads(
                session_id, response, codebase_path
            )

            return {
                "success": True,
                "message": "Stage I code generation completed successfully",
                "error": None,
            }

        except HTTPException as e:
            await self.error_repo.insert_error(
                Error(
                    phase="code_generation_stage_i",
                    error_message="Error in Stage I code generation usecase: "
                    + str(e.detail),
                    stack_trace=e.with_traceback(),
                )
            )
            return {
                "success": False,
                "message": "Error in Stage I code generation usecase: "
                + str(e.detail),
                "error": e.detail,
            }
        except Exception as e:
            await self.error_repo.insert_error(
                Error(
                    phase="code_generation_stage_i",
                    error_message="Unexpected error in Stage I code generation usecase: "
                    + str(e),
                    stack_trace=str(e),
                )
            )
            return {
                "success": False,
                "message": "Unexpected error in Stage I code generation usecase: "
                + str(e),
                "error": str(e),
            }
