from fastapi import APIRouter, Depends

from system.backend.tools.app.controllers.search_tools.grep_search_controller import (
    GrepSearchController,
)
from system.backend.tools.app.models.schemas.grep_search_query_schema import (
    GrepSearchQueryRequest,
)

router = APIRouter()


@router.post("/grep-search")
async def grep_search(
    request: GrepSearchQueryRequest,
    grep_search_controller: GrepSearchController = Depends(),
):
    return await grep_search_controller.process_grep_query(request)
