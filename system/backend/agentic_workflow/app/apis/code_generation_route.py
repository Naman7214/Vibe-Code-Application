from fastapi import APIRouter, Depends

from system.backend.agentic_workflow.app.controllers.code_generation_controller import (
    CodeGenerationController,
)
from system.backend.agentic_workflow.app.models.schemas.code_generation_schema import (
    CodeGenerationRequest,
)

router = APIRouter()


@router.post("/generate-code")
async def generate_code(
    request: CodeGenerationRequest,
    controller: CodeGenerationController = Depends(),
):
    return await controller.execute(request)
