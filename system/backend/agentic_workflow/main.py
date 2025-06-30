import uuid
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from system.backend.agentic_workflow.app.config.database import mongodb_database
from system.backend.agentic_workflow.app.utils.session_context import (
    session_state,
)
from system.backend.agentic_workflow.app.apis.stage_iv_route import router as stage_iv_router


@asynccontextmanager
async def db_lifespan(app: FastAPI):
    mongodb_database.connect()
    yield
    mongodb_database.disconnect()


app = FastAPI(title="Agentic Workflow", lifespan=db_lifespan)

# Include routers
app.include_router(stage_iv_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3001",
        "http://localhost:3000",
    ],  # Specify the exact origin of your frontend
    allow_credentials=True,
    allow_methods=["POST", "GET"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)


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
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
