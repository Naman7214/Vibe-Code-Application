import asyncio

from system.backend.agentic_workflow.app.utils.flutter_boilerplate_setup import (
    setup_flutter_boilerplate,
)


class FlutterCodeGenerationUsecase:
    def __init__(self):
        self.setup_flutter_boilerplate = setup_flutter_boilerplate

    async def execute(self, request):
        # Run Flutter boilerplate setup in background without blocking
        asyncio.create_task(
            self.setup_flutter_boilerplate.create_flutter_boilerplate()
        )
