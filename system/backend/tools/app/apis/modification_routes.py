from fastapi import APIRouter, Depends

from system.backend.tools.app.controllers.modification_tools.edit_file_controller import (
    EditFileController,
)
from system.backend.tools.app.controllers.modification_tools.reapply_controller import (
    ReapplyController,
)
from system.backend.tools.app.controllers.modification_tools.search_replace_controller import (
    SearchReplaceController,
)
from system.backend.tools.app.models.schemas.modification_schemas import (
    EditFileRequest,
    ReapplyRequest,
    SearchReplaceRequest,
)
from system.backend.tools.app.utils.error_handler import handle_exceptions

router = APIRouter(tags=["modification"])


@router.post("/search-replace")
@handle_exceptions
async def search_replace(
    request: SearchReplaceRequest,
    search_replace_controller: SearchReplaceController = Depends(),
):
    return await search_replace_controller.execute(request)


@router.post("/edit-file")
@handle_exceptions
async def edit_file(
    request: EditFileRequest,
    edit_file_controller: EditFileController = Depends(),
):
    return await edit_file_controller.execute(request)


@router.post("/reapply")
@handle_exceptions
async def reapply(
    request: ReapplyRequest,
    reapply_controller: ReapplyController = Depends(),
):
    return await reapply_controller.execute(request)
