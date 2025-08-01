import asyncio
import json
from typing import Any, Dict

from fastapi import Depends, HTTPException

from system.backend.agentic_workflow.app.models.domain.error import Error
from system.backend.agentic_workflow.app.prompts.context_gathering_prompts.stage_iv_prompt import (
    SYSTEM_PROMPT,
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

    async def execute(self, input_data: Dict[str, str]) -> Dict[str, str]:
        """
        Execute Stage IV processing for screen detailed planning

        Args:
            input_data: Dict with screen names as keys (e.g., {"Login": "description", "Dashboard": "description"})

        Returns:
            The original input_data dict
        """
        try:
            # Get session ID from context variable
            session_id = session_state.get()
            if not session_id:
                raise ValueError("Session ID not found in context")

            # Extract screen names from input
            screen_names = list(input_data.keys())

            # Construct file paths
            base_path = f"artifacts/{session_id}/project_context"
            stage_ii_path = f"{base_path}/stage_ii.json"
            stage_iiia_path = f"{base_path}/stage_iiia.json"
            stage_iiib_path = f"{base_path}/stage_iiib.json"

            # Read context files
            stage_ii_data = await self.helper.read_json_file(stage_ii_path)
            stage_iiia_data = await self.helper.read_json_file(stage_iiia_path)
            stage_iiib_data = await self.helper.read_json_file(stage_iiib_path)

            # Extract relevant data
            screen_requirements = self.helper.extract_screen_requirements(
                stage_ii_data, screen_names
            )
            design_system = stage_iiia_data
            global_components = stage_iiib_data.get("global_components", {})
            screen_specific_components = (
                self.helper.extract_screen_specific_components(
                    stage_iiib_data, screen_names
                )
            )

            # Process screens in batches of 10
            batch_size = 10
            all_results = {}

            for i in range(0, len(screen_names), batch_size):
                batch_screens = screen_names[i : i + batch_size]

                # Create tasks for current batch
                tasks = []
                for screen_name in batch_screens:
                    task = self._process_single_screen(
                        screen_name=screen_name,
                        screen_requirements=screen_requirements.get(
                            screen_name, {}
                        ),
                        design_system=design_system,
                        global_components=global_components,
                        screen_specific_components=screen_specific_components.get(
                            screen_name, {}
                        ),
                    )
                    tasks.append(task)

                # Execute batch with asyncio.gather
                batch_results = await asyncio.gather(
                    *tasks, return_exceptions=True
                )

                # Process batch results
                for j, result in enumerate(batch_results):
                    screen_name = batch_screens[j]
                    if isinstance(result, Exception):
                        all_results[screen_name] = {"error": str(result)}
                    else:
                        all_results[screen_name] = result

            # Merge and save results to stage_iv.json (preserve existing screens)
            output_path = f"{base_path}/stage_iv.json"
            await self.helper.merge_and_save_json_file(output_path, all_results)

            # Return original input
            return {
                "success": True,
                "message": "Stage IV completed successfully",
                "error": None,
            }

        except HTTPException as e:
            await self.error_repo.insert_error(
                Error(
                    phase="stage_iv",
                    error_message="Error in the stage iv of context gathering usecase: "
                    + str(e.detail),
                    stack_trace=e.with_traceback(),
                )
            )
            return {
                "success": False,
                "message": "Error in the stage iv of context gathering usecase: "
                + str(e.detail),
                "error": e.detail,
            }

    async def _process_single_screen(
        self,
        screen_name: str,
        screen_requirements: Dict[str, Any],
        design_system: Dict[str, Any],
        global_components: Dict[str, Any],
        screen_specific_components: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Process a single screen with LLM
        """
        try:
            # Construct user message with all context
            user_message = {
                "screen_requirements": {screen_name: screen_requirements},
                "design_system": design_system,
                "global_components": global_components,
                "screen_specific_components": {
                    screen_name: screen_specific_components
                },
            }

            user_message_str = json.dumps(user_message, indent=None)
            # Make LLM call
            response = await self.anthropic_service.generate_text(
                prompt=user_message_str,
                system_prompt=SYSTEM_PROMPT,
                provider="anthropic",
            )
            # Extract text content
            content = response  # response is already the text content

            # Parse the response to extract JSON from <o> tags
            try:
                parsed_content = parse_model_output(content)
            except ValueError as e:
                parsed_content = {"raw_content": content, "parse_error": str(e)}

            return parsed_content

        except Exception as e:
            raise
