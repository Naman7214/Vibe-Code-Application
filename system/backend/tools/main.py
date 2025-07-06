from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from system.backend.tools.app.apis import (
    code_base_search_routes,
    file_access_routes,
    modification_routes,
    run_terminal_cmd_routes,
)
from system.backend.tools.app.config.database import mongodb_database


@asynccontextmanager
async def db_lifespan(app: FastAPI):
    mongodb_database.connect()

    yield

    mongodb_database.disconnect()


app = FastAPI(title="My FastAPI Application", lifespan=db_lifespan)
app.include_router(
    code_base_search_routes.router, prefix="/api/v1", tags=["search tools"]
)
app.include_router(
    run_terminal_cmd_routes.router, prefix="/api/v1", tags=["environment tools"]
)
app.include_router(
    modification_routes.router, prefix="/api/v1", tags=["modification tools"]
)
app.include_router(
    file_access_routes.router, prefix="/api/v1", tags=["file access tools"]
)
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://localhost:8001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Welcome to my velocity.new tools!"}


if __name__ == "__main__":
    uvicorn.run(
        "system.backend.tools.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        reload_exclude=["artifacts/*", "artifacts/**/*"],
    )
