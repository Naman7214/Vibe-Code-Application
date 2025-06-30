from fastapi import APIRouter, Depends

from system.backend.agentic_workflow.app.controllers.initial_processing_controller import (
    InitialProcessingController,
)
from system.backend.agentic_workflow.app.models.schemas.initial_processing_schema import (
    InitialProcessingRequest,
)

router = APIRouter()


@router.post("/initial-processing")
async def initial_processing(
    request: InitialProcessingRequest,
    initial_processing_controller: InitialProcessingController = Depends(),
):
    return await initial_processing_controller.execute(request)
