from fastapi import Depends, status
from fastapi.responses import JSONResponse

from system.backend.tools.app.models.schemas.grep_search_query_schema import (
    GrepSearchQueryRequest,
)
from system.backend.tools.app.usecases.search_tools.grep_search_usecase import (
    GrepSearchUsecase,
)


class GrepSearchController:
    def __init__(
        self,
        grep_search_usecase: GrepSearchUsecase = Depends(GrepSearchUsecase),
    ):
        self.grep_search_usecase = grep_search_usecase

    async def process_grep_query(self, request: GrepSearchQueryRequest):
        result = await self.grep_search_usecase.execute_grep_search(request)
        return JSONResponse(
            content={
                "data": result,
                "message": "Grep search completed successfully",
                "error": None,
            },
            status_code=status.HTTP_200_OK,
        )
