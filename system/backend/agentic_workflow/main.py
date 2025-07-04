import uuid
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from system.backend.agentic_workflow.app.apis.code_generation_route import (
    router as code_generation_router,
)
from system.backend.agentic_workflow.app.apis.context_gathering_route import (
    router as context_gathering_router,
)
from system.backend.agentic_workflow.app.apis.ide_agent_route import (
    router as ide_agent_router,
)
from system.backend.agentic_workflow.app.apis.initial_processing_route import (
    router as initial_processing_router,
)
from system.backend.agentic_workflow.app.config.database import mongodb_database
from system.backend.agentic_workflow.app.utils.session_context import (
    session_state,
)


@asynccontextmanager
async def db_lifespan(app: FastAPI):
    mongodb_database.connect()
    yield
    mongodb_database.disconnect()


app = FastAPI(title="Agentic Workflow", lifespan=db_lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
    ],  # Allow frontend origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods including OPTIONS
    allow_headers=["*"],  # Allow all headers including X-Session-ID
)

# Include API routers
app.include_router(
    initial_processing_router, prefix="/api/v1", tags=["initial-processing"]
)
app.include_router(
    context_gathering_router, prefix="/api/v1", tags=["context-gathering"]
)
app.include_router(
    code_generation_router, prefix="/api/v1", tags=["code-generation"]
)
app.include_router(ide_agent_router, prefix="/api/v1", tags=["ide-agent"])


@app.middleware("http")
async def set_session_context(request: Request, call_next):

    session_id = request.headers.get("X-Session-ID", str(uuid.uuid4()))
    if not session_state.get():
        token = session_state.set(session_id)
    try:
        response = await call_next(request)
    finally:
        session_state.reset(token)

    return response


@app.get("/")
async def root():
    return {"message": "Welcome to my FastAPI application!"}


if __name__ == "__main__":
    uvicorn.run(
        "system.backend.agentic_workflow.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_exclude=[
            "artifacts/*",
            "artifacts/**/*",
            "artifacts/**/**/*",
            "artifacts/**/**/**/*",
            "artifacts",
        ],
    )
