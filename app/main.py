import os
import secrets
from uuid import uuid4

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel
from langgraph.types import Command

from app.agent_graph import agent_graph


app = FastAPI(
    title="Agentic AI Operations Copilot",
    version="1.0.0",
)


def require_api_key(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
):
    expected_key = os.getenv("APP_API_KEY")

    if not expected_key:
        raise HTTPException(
            status_code=500,
            detail="Server API key is not configured.",
        )

    if not x_api_key or not secrets.compare_digest(
        x_api_key,
        expected_key,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key.",
        )


class AskRequest(BaseModel):
    query: str
    thread_id: str | None = None


class ApprovalRequest(BaseModel):
    thread_id: str
    decision: str


@app.get("/")
def root():
    return {
        "service": "Agentic AI Operations Copilot",
        "status": "running",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
    }


@app.post("/ask", dependencies=[Depends(require_api_key)])
def ask(request: AskRequest):
    thread_id = request.thread_id or str(uuid4())

    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    result = agent_graph.invoke(
        {
            "user_query": request.query,
        },
        config=config,
    )

    response = {
        "thread_id": thread_id,
        "route": result.get("route"),
        "answer": result.get("final_answer"),
        "proposed_action": result.get("proposed_action"),
        "requires_approval": result.get(
            "requires_approval",
            False,
        ),
        "approval_status": result.get("approval_status"),
        "action_result": result.get("action_result"),
    }

    if "__interrupt__" in result:
        response["status"] = "awaiting_approval"
    else:
        response["status"] = "completed"

    return response


@app.post("/approve", dependencies=[Depends(require_api_key)])
def approve(request: ApprovalRequest):
    config = {
        "configurable": {
            "thread_id": request.thread_id,
        }
    }

    result = agent_graph.invoke(
        Command(
            resume=request.decision,
        ),
        config=config,
    )

    return {
        "thread_id": request.thread_id,
        "approval_status": result.get(
            "approval_status"
        ),
        "action_result": result.get(
            "action_result"
        ),
        "status": "completed",
    }
