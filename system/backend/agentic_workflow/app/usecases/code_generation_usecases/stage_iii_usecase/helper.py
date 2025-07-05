import asyncio
import json
import logging

from fastapi import Depends

from system.backend.agentic_workflow.app.models.schemas.code_generation_schema import (
    CodeGenerationRequest,
)
from system.backend.agentic_workflow.app.prompts.code_generation_prompts.stage_iii_prompt import (
    SYSTEM_PROMPT,
    USER_PROMPT,
)
from system.backend.agentic_workflow.app.services.anthropic_services.llm_service import (
    AnthropicService,
)
from system.backend.agentic_workflow.app.utils.file_structure import (
    generate_directory_structure,
    get_project_root,
)
from system.backend.agentic_workflow.app.utils.file_writer import (
    write_code_files,
)
from system.backend.agentic_workflow.app.utils.logger import loggers
from system.backend.agentic_workflow.app.utils.session_context import (
    session_state,
)
from system.backend.agentic_workflow.app.utils.xml_parser import (
    parse_xml_to_dict,
)


class Helper:
    def __init__(
        self, anthropic_service: AnthropicService = Depends(AnthropicService)
    ):
        self.anthropic_service = anthropic_service
        self.logger = logging.getLogger("code_generation_stage_iii")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def read_context_files(self, request: CodeGenerationRequest):
        """
        Read stage_iv.json and stage_v.json files for the given session.
        Returns stage_iv data and screen_navigation from stage_v.
        """
        base_path = f"artifacts/{session_state.get()}/project_context"

        with open(f"{base_path}/stage_iv.json", "r") as f:
            stage_iv_data = json.load(f)

        with open(f"{base_path}/stage_v.json", "r") as f:
            stage_v_data = json.load(f)
            screen_navigation = stage_v_data.get(
                "navigation_structure", {}
            ).get("screen_navigation", {})

        scratchpad_path = f"artifacts/{session_state.get()}/scratchpads"
        with open(f"{scratchpad_path}/global_scratchpad.txt", "r") as f:
            global_scratchpad = f.read()

        with open(f"{scratchpad_path}/file_structure.txt", "r") as f:
            file_structure = f.read()

        if request.is_follow_up:
            screen_names = list(request.dict_of_screens.keys())
            stage_iv_data = {
                screen: data
                for screen, data in stage_iv_data.items()
                if screen in screen_names
            }
            screen_navigation = {
                screen: data
                for screen, data in screen_navigation.items()
                if screen in screen_names
            }

        return (
            stage_iv_data,
            screen_navigation,
            global_scratchpad,
            file_structure,
        )

    async def run_stage_3_pipeline(self, request: CodeGenerationRequest):
        """
        Processes the input for Stage 3 to generate the code for the screens.
        """
        self.logger.info(
            "Starting stage 3 pipeline to generate code for screens"
        )

        stage_iv_data, screen_navigation, global_scratchpad, file_structure = (
            self.read_context_files(request)
        )

        self.logger.info(f"successfully read the context files...")

        screen_names = list(stage_iv_data.keys())
        batch_size = 5
        total_screens = len(screen_names)
        total_batches = (total_screens + batch_size - 1) // batch_size

        self.logger.info(
            f"Processing {total_screens} screens in {total_batches} batches (batch size: {batch_size})"
        )

        for i in range(0, len(screen_names), batch_size):
            batch_number = (i // batch_size) + 1
            batch_screens = screen_names[i : i + batch_size]

            self.logger.info(
                f"Starting batch {batch_number}/{total_batches} with screens: {batch_screens}"
            )

            loggers["screen_generation"].info(
                f"Processing batch of screens: {batch_screens}"
            )

            batch_stage_iv = {
                screen: stage_iv_data[screen] for screen in batch_screens
            }
            batch_navigation = {
                screen: screen_navigation.get(screen, {})
                for screen in batch_screens
            }

            await self.process_screen_batch(
                batch_stage_iv,
                batch_navigation,
                global_scratchpad,
                file_structure,
            )

            self.logger.info(
                f"Completed batch {batch_number}/{total_batches}"
            )

        self.logger.info("All batches completed.")
        
        self.logger.info("Generating updated directory structure")
        structure = generate_directory_structure(
            directory_path=f"{get_project_root()}/artifacts/{session_state.get()}/codebase",
            max_depth=10,
        )

        structure_file_path = f"{get_project_root()}/artifacts/{session_state.get()}/scratchpads/file_structure.txt"
        self.logger.info(
            f"Writing directory structure to {structure_file_path}"
        )
        with open(structure_file_path, "w") as f:
            f.write(structure)

        self.logger.info("Stage 3 pipeline completed successfully")

    async def process_screen_batch(
        self,
        batch_stage_iv,
        batch_navigation,
        global_scratchpad,
        file_structure,
    ):
        """
        Process a batch of screens (up to 5) in parallel using asyncio.
        """
        batch_screens = list(batch_stage_iv.keys())
        self.logger.info(
            f"Starting parallel processing of {len(batch_screens)} screens: {batch_screens}"
        )

        loggers["screen_generation"].info(
            f"Processing batch of screens: {batch_stage_iv.keys()}"
        )
        tasks = []
        for screen_name in batch_stage_iv.keys():
            self.logger.info(f"Creating task for screen: {screen_name}")
            task = self.process_single_screen(
                screen_name,
                batch_stage_iv[screen_name],
                batch_navigation.get(screen_name, {}),
                global_scratchpad,
                file_structure,
            )
            tasks.append(task)

        self.logger.info(
            f"Executing {len(tasks)} screen processing tasks in parallel"
        )
        await asyncio.gather(*tasks)

        self.logger.info("Batch processing completed.")

    async def process_single_screen(
        self,
        screen_name,
        screen_data,
        screen_navigation_data,
        global_scratchpad,
        file_structure,
    ):
        """
        Process a single screen and save its code files immediately.
        """
        loggers["screen_generation"].info(
            f"Processing single screen: {screen_name}"
        )

        system_prompt = SYSTEM_PROMPT.format(
            base_path=f"{get_project_root()}/artifacts/{session_state.get()}",
        )

        single_screen_data = {screen_name: screen_data}
        single_navigation_data = {screen_name: screen_navigation_data}

        user_prompt = USER_PROMPT.format(
            screen=json.dumps(single_screen_data),
            screen_navigation_data=json.dumps(single_navigation_data),
            global_scratchpad=global_scratchpad,
            file_structure=file_structure,
        )

        response = await self.anthropic_service.anthropic_client_request(
            system_prompt=system_prompt, prompt=user_prompt
        )

        self.logger.info(f"screen generated successfully... {screen_name}")

        code_files = parse_xml_to_dict(response)

        self.logger.info(f"Writing {len(code_files)} code files for screen: {screen_name}")
        write_code_files(code_files, base_dir="")
        self.logger.info(f"Successfully saved code files for screen: {screen_name}")
