import asyncio
import json
import os
from typing import Any, Dict

from fastapi import Depends

from system.backend.agentic_workflow.app.models.schemas.context_gathering_schema import (
    ContextGatheringRequest,
)
from system.backend.agentic_workflow.app.prompts.context_gathering_prompts.stage_iii_prompt import (
    FLUTTER_SYSTEM_PROMPT_A,
    FLUTTER_SYSTEM_PROMPT_B,
    FLUTTER_USER_PROMPT_A,
    FLUTTER_USER_PROMPT_B,
)
from system.backend.agentic_workflow.app.services.anthropic_services.llm_service import (
    AnthropicService,
)
from system.backend.agentic_workflow.app.utils.parser import parse_model_output


class FlutterHelper:
    def __init__(self, anthropic_service: AnthropicService = Depends()):
        self.anthropic_service = anthropic_service

    async def run_flutter_stage_3_pipeline(self, request: ContextGatheringRequest):
        """
        Processes the input for Flutter Stage 3 to define mobile theme and widget strategy.
        """
        if request.is_follow_up:
            result = await self._generate_flutter_widgets_details(request)

            if not result.get("success"):
                return result

        else:
            global_theme_task = self._flutter_global_theme_generation(request)
            widgets_task = self._generate_flutter_widgets_details(request)

            results = await asyncio.gather(global_theme_task, widgets_task)

            for result in results:
                if not result.get("success"):
                    return result

        return {
            "success": True,
            "message": "Flutter Stage 3 pipeline completed successfully",
        }

    async def _flutter_global_theme_generation(self, request: ContextGatheringRequest):
        """
        Generates the global mobile theme for the Flutter project.
        """

        print("entered flutter global theme generation")

        with open(
            f"artifacts/{request.session_id}/project_context/stage_i.json", "r"
        ) as f:
            first_stage_output = json.load(f)

        with open(
            f"artifacts/{request.session_id}/project_context/stage_ii.json", "r"
        ) as f:
            second_stage_output = json.load(f)

        user_prompt = FLUTTER_USER_PROMPT_A.format(
            first_stage_output=json.dumps(first_stage_output, indent=2),
            second_stage_output=json.dumps(second_stage_output, indent=2),
        )
        response = await self.anthropic_service.generate_text(
            system_prompt=FLUTTER_SYSTEM_PROMPT_A,
            prompt=user_prompt,
            provider="anthropic",
        )

        parsed_response = parse_model_output(response)

        await self._save_output(
            request.session_id, parsed_response, "stage_iii_a.json"
        )

        return {
            "success": True,
            "message": "Flutter global theme generation completed successfully",
        }

    async def _generate_flutter_widgets_details(self, request: ContextGatheringRequest):
        """
        Generates the Flutter widget architecture and screen-specific widget details.
        """

        with open(
            f"artifacts/{request.session_id}/project_context/stage_ii.json", "r"
        ) as f:
            second_stage_output = json.load(f)

        previous_output = {}
        if request.is_follow_up:
            filtered_output = {
                key: value
                for key, value in second_stage_output.items()
                if key in request.dict_of_screens
                or key == "global_data_requirements"
            }
            second_stage_output = filtered_output

            with open(
                f"artifacts/{request.session_id}/project_context/stage_iii_b.json",
                "r",
            ) as f:
                previous_output = json.load(f)

        user_prompt = FLUTTER_USER_PROMPT_B.format(
            second_stage_output=json.dumps(second_stage_output, indent=2),
            previous_output=previous_output,
        )
        response = await self.anthropic_service.generate_text(
            system_prompt=FLUTTER_SYSTEM_PROMPT_B,
            prompt=user_prompt,
            provider="anthropic",
        )

        parsed_response = parse_model_output(response)

        await self._save_output(
            request.session_id, parsed_response, "stage_iii_b.json"
        )

        return {
            "success": True,
            "message": "Flutter widget architecture generation completed successfully",
        }

    async def _save_output(
        self,
        session_id: str,
        output_data: Dict[str, Any],
        output_file_name: str,
    ):
        """
        Saves the output data to a JSON file in the artifacts directory.
        """
        output_dir = f"artifacts/{session_id}/project_context"
        os.makedirs(output_dir, exist_ok=True)

        file_path = os.path.join(output_dir, output_file_name)
        with open(file_path, "w") as f:
            json.dump(output_data, f, indent=2) 