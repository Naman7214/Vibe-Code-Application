from fastapi import APIRouter, Depends

from system.backend.tools.app.controllers.modification_tools.edit_file_controller import (
    EditFileController,
)
from system.backend.tools.app.controllers.modification_tools.search_replace_controller import (
    SearchReplaceController,
)
from system.backend.tools.app.models.schemas.modification_schemas import (
    EditFileRequest,
    SearchReplaceRequest,
)
from system.backend.tools.app.utils.error_handler import handle_exceptions

router = APIRouter()


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
