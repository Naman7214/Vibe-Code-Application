from fastapi import APIRouter, Depends

from backend.app.controllers.search_tools.code_base_search_controller import (
    CodeBaseSearchController,
)
from backend.app.controllers.search_tools.grep_search_controller import (
    GrepSearchController,
)
from backend.app.models.schemas.code_base_search_schema import (
    CodeBaseSearchQueryRequest,
)
from backend.app.models.schemas.grep_search_query_schema import (
    GrepSearchQueryRequest,
)

router = APIRouter()


@router.post("/code-base-search")
async def code_base_search(
    request: CodeBaseSearchQueryRequest,
    code_base_search_controller: CodeBaseSearchController = Depends(),
):

    return await code_base_search_controller.process_query(request)


@router.post("/grep-search")
async def grep_search(
    request: GrepSearchQueryRequest,
    grep_search_controller: GrepSearchController = Depends(),
):
    return await grep_search_controller.process_grep_query(request)
