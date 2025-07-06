import json
import os

from fastapi import Depends, HTTPException

from system.backend.agentic_workflow.app.models.domain.error import Error
from system.backend.agentic_workflow.app.models.schemas.context_gathering_schema import (
    ContextGatheringRequest,
)
from system.backend.agentic_workflow.app.prompts.context_gathering_prompts.stage_v_prompt import (
    FLUTTER_SYSTEM_PROMPT,
    FLUTTER_USER_PROMPT,
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


class FlutterStageVUsecase:
    def __init__(
        self,
        anthropic_service: AnthropicService = Depends(),
        error_repo: ErrorRepo = Depends(),
    ):
        self.anthropic_service = anthropic_service
        self.error_repo = error_repo

    async def execute(self, request: ContextGatheringRequest) -> dict:
        """
        Handle Flutter mobile navigation context gathering for Stage V

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

            # Handle Flutter mobile navigation generation
            return await self._handle_flutter_navigation_generation(
                request,
                context_dir,
                stage_iv_path,
                stage_v_path,
                session_id,
            )
        except HTTPException as e:
            await self.error_repo.insert_error(
                Error(
                    phase="flutter_stage_v",
                    error_message="Error in the flutter stage v of context gathering usecase: "
                    + str(e.detail),
                    stack_trace=e.with_traceback(),
                )
            )

            return {
                "success": False,
                "message": "Error in the flutter stage v of context gathering usecase: "
                + str(e.detail),
                "error": e.detail,
            }

    async def _handle_flutter_navigation_generation(
        self, request, context_dir, stage_iv_path, stage_v_path, session_id
    ) -> dict:
        """Handle Flutter mobile navigation generation"""

        # Check if stage_iv.json exists
        if not os.path.exists(stage_iv_path):
            raise FileNotFoundError(f"Stage IV file not found: {stage_iv_path}")

        # Read stage_iv.json content
        with open(stage_iv_path, "r") as f:
            stage_iv_data = json.load(f)

        # For follow-up requests, read existing stage_v.json and merge
        existing_stage_v = {}
        if request.is_follow_up and os.path.exists(stage_v_path):
            with open(stage_v_path, "r") as f:
                existing_stage_v = json.load(f)

        # Create user prompt with context and screens
        user_prompt = FLUTTER_USER_PROMPT.format(
            context=json.dumps(stage_iv_data, indent=None),
            screens=json.dumps(request.dict_of_screens, indent=None),
        )

        # Call LLM service with Flutter-specific prompts
        llm_response = await self.anthropic_service.generate_text(
            prompt=user_prompt,
            system_prompt=FLUTTER_SYSTEM_PROMPT,
            provider="anthropic",
        )

        # Parse the JSON output
        navigation_data = parse_model_output(llm_response)

        # For follow-up requests, merge with existing data
        if request.is_follow_up and existing_stage_v:
            # Merge screen navigation data
            existing_screen_nav = existing_stage_v.get("screen_navigation", {})
            new_screen_nav = navigation_data.get("screen_navigation", {})
            merged_screen_nav = {**existing_screen_nav, **new_screen_nav}

            navigation_data["screen_navigation"] = merged_screen_nav

        # Save to stage_v.json
        with open(stage_v_path, "w") as f:
            json.dump(navigation_data, f, indent=2)

        return {
            "success": True,
            "message": "Flutter Stage V completed successfully",
            "error": None,
        }
