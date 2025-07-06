import json
import os

from fastapi import Depends, HTTPException

from system.backend.agentic_workflow.app.models.domain.error import Error
from system.backend.agentic_workflow.app.models.schemas.context_gathering_schema import (
    ContextGatheringRequest,
)
from system.backend.agentic_workflow.app.prompts.context_gathering_prompts.stage_v_prompt import (
    FOLLOWUP_SYSTEM_PROMPT,
    FOLLOWUP_USER_PROMPT,
    INITIAL_SYSTEM_PROMPT,
    INITIAL_USER_PROMPT,
)
from system.backend.agentic_workflow.app.repositories.error_repo import (
    ErrorRepo,
)
from system.backend.agentic_workflow.app.services.anthropic_services.llm_service import (
    AnthropicService,
)
from system.backend.agentic_workflow.app.utils.parser import parse_model_output
from system.backend.agentic_workflow.app.utils.session_context import (
    session_state,
)


class StageVUsecase:
    def __init__(
        self,
        anthropic_service: AnthropicService = Depends(),
        error_repo: ErrorRepo = Depends(),
    ):
        self.anthropic_service = anthropic_service
        self.error_repo = error_repo

    async def execute(self, request: ContextGatheringRequest) -> dict:
        """
        Handle navigation context gathering for Stage V

        :param request: ContextGatheringRequest containing screen selections
        :return: Dict with navigation context data and metadata
        """
        try:
            # Get session_id from context (set by middleware)
            session_id = session_state.get()
            if not session_id:
                raise ValueError("No session_id available in context")

            # Define file paths
            context_dir = f"artifacts/{session_id}/project_context"
            stage_iv_path = os.path.join(context_dir, "stage_iv.json")
            stage_v_path = os.path.join(context_dir, "stage_v.json")

            if not request.is_follow_up:
                # Scenario 1: Initial navigation generation
                return await self._handle_initial_generation(
                    request,
                    context_dir,
                    stage_iv_path,
                    stage_v_path,
                    session_id,
                )
            else:
                # Scenario 2: Follow-up navigation updates
                return await self._handle_followup_generation(
                    request, context_dir, stage_v_path, session_id
                )
        except HTTPException as e:
            await self.error_repo.insert_error(
                Error(
                    phase="stage_v",
                    error_message="Error in the stage v of context gathering usecase: "
                    + str(e.detail),
                    stack_trace=e.with_traceback(),
                )
            )

            return {
                "success": False,
                "message": "Error in the stage v of context gathering usecase: "
                + str(e.detail),
                "error": e.detail,
            }

    async def _handle_initial_generation(
        self, request, context_dir, stage_iv_path, stage_v_path, session_id
    ) -> dict:
        """Handle initial navigation generation scenario"""

        # Check if stage_iv.json exists
        if not os.path.exists(stage_iv_path):
            raise FileNotFoundError(f"Stage IV file not found: {stage_iv_path}")

        # Read stage_iv.json content
        with open(stage_iv_path, "r") as f:
            stage_iv_data = json.load(f)

        # Create user prompt with context and screens
        user_prompt = INITIAL_USER_PROMPT.format(
            context=json.dumps(stage_iv_data, indent=None),
            screens=json.dumps(request.dict_of_screens, indent=None),
        )

        # Call LLM service
        llm_response = await self.anthropic_service.generate_text(
            prompt=user_prompt,
            system_prompt=INITIAL_SYSTEM_PROMPT,
            provider="anthropic",
        )

        # Parse the JSON output
        navigation_data = parse_model_output(llm_response)
        # Save to stage_v.json
        with open(stage_v_path, "w") as f:
            json.dump(navigation_data, f, indent=2)

        return {
            "success": True,
            "message": "Stage V completed successfully",
            "error": None,
        }

    async def _handle_followup_generation(
        self, request, context_dir, stage_v_path, session_id
    ) -> dict:
        """Handle follow-up navigation updates scenario"""

        # Check if stage_v.json exists
        if not os.path.exists(stage_v_path):
            raise FileNotFoundError(f"Stage V file not found: {stage_v_path}")

        # Read existing stage_v.json
        with open(stage_v_path, "r") as f:
            existing_stage_v = json.load(f)

        # Extract existing global navigation
        existing_navigation_structure = existing_stage_v.get(
            "navigation_structure", {}
        )
        existing_global_nav = existing_navigation_structure.get(
            "global_navigation", {}
        )

        # Create user prompt for follow-up
        user_prompt = FOLLOWUP_USER_PROMPT.format(
            global_navigation=json.dumps(existing_global_nav, indent=None),
            new_screens=json.dumps(request.dict_of_screens, indent=None),
        )

        # Call LLM service
        llm_response = await self.anthropic_service.generate_text(
            prompt=user_prompt,
            system_prompt=FOLLOWUP_SYSTEM_PROMPT,
            provider="anthropic",
        )

        # Parse the JSON output
        updated_navigation = parse_model_output(llm_response)

        # Update existing stage_v.json
        # Replace global-navigation with updated version
        existing_stage_v["navigation_structure"]["global_navigation"] = (
            updated_navigation["navigation_structure"]["global_navigation"]
        )

        # Append new screen-specific navigation
        if "screen_navigation" not in existing_stage_v["navigation_structure"]:
            existing_stage_v["navigation_structure"]["screen_navigation"] = {}

        existing_stage_v["navigation_structure"]["screen_navigation"].update(
            updated_navigation["navigation_structure"]["screen_navigation"]
        )

        # Save updated data back to file
        with open(stage_v_path, "w") as f:
            json.dump(existing_stage_v, f, indent=2)

        return {
            "success": True,
            "message": "Stage V completed successfully",
            "error": None,
        }
