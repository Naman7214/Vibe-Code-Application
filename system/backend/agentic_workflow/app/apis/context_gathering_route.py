from fastapi import APIRouter, Depends

from system.backend.agentic_workflow.app.controllers.context_gathering_controller import (
    ContextGatheringController,
)
from system.backend.agentic_workflow.app.models.schemas.context_gathering_schema import (
    ContextGatheringRequest,
)

router = APIRouter()


@router.post("/context-gathering")
async def context_gathering(
    request: ContextGatheringRequest,
    context_gathering_controller: ContextGatheringController = Depends(),
):
    return await context_gathering_controller.execute(request)
