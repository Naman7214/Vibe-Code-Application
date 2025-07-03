import json
import os
from typing import Any, Dict

from fastapi import Depends

from system.backend.agentic_workflow.app.models.schemas.context_gathering_schema import (
    ContextGatheringRequest,
)
from system.backend.agentic_workflow.app.prompts.context_gathering_prompts.stage_ii_prompt import (
    FLUTTER_SYSTEM_PROMPT,
    FLUTTER_USER_PROMPT,
)
from system.backend.agentic_workflow.app.services.anthropic_services.llm_service import (
    AnthropicService,
)
from system.backend.agentic_workflow.app.utils.parser import parse_model_output


class FlutterHelper:
    def __init__(self, anthropic_service: AnthropicService = Depends()):
        self.anthropic_service = anthropic_service

    async def run_flutter_stage_2_pipeline(
        self, request: ContextGatheringRequest
    ):
        """
        Processes the input for Flutter Stage 2 to define mobile screen requirements.
        """

        with open(
            f"artifacts/{request.session_id}/project_context/stage_i.json", "r"
        ) as f:
            project_context = json.load(f)

        previous_output = {}
        if not os.path.exists(
            f"artifacts/{request.session_id}/project_context/stage_ii.json"
        ):
            previous_output = {}
        else:
            with open(
                f"artifacts/{request.session_id}/project_context/stage_ii.json",
                "r",
            ) as f:
                previous_output = json.load(f)

        if request.is_follow_up:
            project_context["screens"] = request.dict_of_screens

        # Use Flutter-specific prompts
        user_prompt = FLUTTER_USER_PROMPT.format(
            first_stage_output=json.dumps(project_context, indent=2),
            previous_output=json.dumps(previous_output, indent=2),
        )
        response = await self.anthropic_service.generate_text(
            system_prompt=FLUTTER_SYSTEM_PROMPT,
            prompt=user_prompt,
            provider="anthropic",
        )

        parsed_response = parse_model_output(response)

        await self._save_output(request.session_id, parsed_response)

    async def _save_output(self, session_id: str, output_data: Dict[str, Any]):
        """
        Saves the output data to a JSON file in the artifacts directory.
        """
        output_dir = f"artifacts/{session_id}/project_context"
        os.makedirs(output_dir, exist_ok=True)

        file_path = os.path.join(output_dir, "stage_ii.json")
        with open(file_path, "w") as f:
            json.dump(output_data, f, indent=2)
