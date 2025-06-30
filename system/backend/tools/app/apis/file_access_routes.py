from fastapi import APIRouter, Depends

from system.backend.tools.app.controllers.file_access_tools.directory_list_controller import (
    DirectoryListController,
)
from system.backend.tools.app.controllers.file_access_tools.file_deletion_controller import (
    FileDeletionController,
)
from system.backend.tools.app.controllers.file_access_tools.file_read_controller import (
    FileReadController,
)
from system.backend.tools.app.controllers.file_access_tools.file_search_controller import (
    FileSearchController,
)
from system.backend.tools.app.models.schemas.file_access_schemas import (
    DirectoryListRequest,
    FileReadRequest,
    FilesDeleteRequest,
    FileSearchRequest,
)
from system.backend.tools.app.utils.error_handler import handle_exceptions

router = APIRouter()


@router.post("/read-file")
@handle_exceptions
async def read_file(
    request: FileReadRequest,
    file_read_controller: FileReadController = Depends(),
):

    return await file_read_controller.execute(request)


@router.post("/delete-file")
@handle_exceptions
async def delete_file(
    request: FilesDeleteRequest,
    file_deletion_controller: FileDeletionController = Depends(),
):

    return await file_deletion_controller.execute(request)


@router.post("/list-directory")
@handle_exceptions
async def list_directory(
    request: DirectoryListRequest,
    directory_list_controller: DirectoryListController = Depends(),
):

    return await directory_list_controller.execute(request)


@router.post("/search-files")
@handle_exceptions
async def search_files(
    request: FileSearchRequest,
    file_search_controller: FileSearchController = Depends(),
):

    return await file_search_controller.execute(request)
