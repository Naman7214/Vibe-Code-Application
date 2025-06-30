import uvicorn
from fastapi import FastAPI

app = FastAPI(title="Agentic Workflow")

@app.get("/")
async def root():
    return {"message": "Welcome to my FastAPI application!"}


if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
