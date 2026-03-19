import asyncio
import uuid
from datetime import datetime
from typing import Optional, Dict, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from agent import execute_agent, load_agents
from intent_parser import parse_intent
from router import route_with_logging


request_store: Dict[str, dict] = {}
pending_requests: List[asyncio.Task] = []
agents_cache = None


class RequestInput(BaseModel):
    text: str = Field(..., description="The user's request text")
    priority: int = Field(
        default=0, description="Request priority (higher = more important)"
    )


class RequestResponse(BaseModel):
    request_id: str
    status: str
    message: str


class RequestResult(BaseModel):
    request_id: str
    status: str
    input_text: str
    result: Optional[str] = None
    error: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None
    processing_time: Optional[float] = None


async def process_request(request_id: str, user_input: str, priority: int):
    """Process a request asynchronously."""
    start_time = datetime.now()

    request_store[request_id]["status"] = "processing"

    try:
        intent = await parse_intent(user_input)
        selected_agent = await route_with_logging(intent, agents_cache)

        if not selected_agent:
            raise Exception("No agent found to handle request")

        result = await execute_agent(selected_agent, user_input)

        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()

        request_store[request_id].update(
            {
                "status": "completed",
                "result": result,
                "completed_at": end_time.isoformat(),
                "processing_time": processing_time,
            }
        )

    except Exception as e:
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()

        request_store[request_id].update(
            {
                "status": "failed",
                "error": str(e),
                "completed_at": end_time.isoformat(),
                "processing_time": processing_time,
            }
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown."""
    global agents_cache
    agents_cache = load_agents()
    print(f"[Server] Loaded {len(agents_cache)} agents")

    yield

    print("[Server] Shutting down...")
    if pending_requests:
        print(f"[Server] Waiting for {len(pending_requests)} pending requests...")
        await asyncio.gather(*pending_requests, return_exceptions=True)


app = FastAPI(
    title="AI Agent System",
    description="Concurrent AI agent system for processing requests",
    version="2.0.0",
    lifespan=lifespan,
)


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": "AI Agent System",
        "version": "2.0.0",
        "status": "running",
        "endpoints": {
            "POST /request": "Submit a new request for processing",
            "GET /request/{request_id}": "Get status/result of a request",
            "GET /requests": "List all requests",
            "GET /health": "Health check",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_requests": len(
            [r for r in request_store.values() if r["status"] == "processing"]
        ),
        "total_requests": len(request_store),
        "agents_loaded": len(agents_cache) if agents_cache else 0,
    }


@app.post("/request", response_model=RequestResponse)
async def create_request(request: RequestInput, background_tasks: BackgroundTasks):
    """Submit a new request for async processing."""
    request_id = str(uuid.uuid4())[:8]
    created_at = datetime.now()

    request_store[request_id] = {
        "request_id": request_id,
        "input_text": request.text,
        "priority": request.priority,
        "status": "queued",
        "created_at": created_at.isoformat(),
        "result": None,
        "error": None,
        "completed_at": None,
        "processing_time": None,
    }

    task = asyncio.create_task(
        process_request(request_id, request.text, request.priority)
    )
    pending_requests.append(task)
    task.add_done_callback(
        lambda t: pending_requests.remove(t) if t in pending_requests else None
    )

    return RequestResponse(
        request_id=request_id,
        status="queued",
        message=f"Request queued for processing. Use GET /request/{request_id} to check status.",
    )


@app.get("/request/{request_id}", response_model=RequestResult)
async def get_request(request_id: str):
    """Get the status and result of a request."""
    if request_id not in request_store:
        raise HTTPException(status_code=404, detail=f"Request {request_id} not found")

    req = request_store[request_id]
    return RequestResult(**req)


@app.get("/requests", response_model=List[RequestResult])
async def list_requests(
    status: Optional[str] = None, limit: int = 100, offset: int = 0
):
    """List all requests, optionally filtered by status."""
    requests = list(request_store.values())

    if status:
        requests = [r for r in requests if r["status"] == status]

    requests.sort(key=lambda x: x["created_at"], reverse=True)

    return requests[offset : offset + limit]


@app.delete("/request/{request_id}")
async def delete_request(request_id: str):
    """Delete a completed request from the store."""
    if request_id not in request_store:
        raise HTTPException(status_code=404, detail=f"Request {request_id} not found")

    req = request_store[request_id]
    if req["status"] == "processing":
        raise HTTPException(
            status_code=400,
            detail="Cannot delete a request that is currently processing",
        )

    del request_store[request_id]
    return {"message": f"Request {request_id} deleted", "request_id": request_id}


@app.post("/clear")
async def clear_completed():
    """Clear all completed/failed requests from the store."""
    to_delete = [
        rid
        for rid, req in request_store.items()
        if req["status"] in ["completed", "failed"]
    ]

    for rid in to_delete:
        del request_store[rid]

    return {
        "message": f"Cleared {len(to_delete)} requests",
        "remaining_requests": len(request_store),
    }
