"""API module providing REST endpoints and authentication for Salesforce WebDev automation."""

from typing import Any, Dict, Optional
import os
from fastapi import Depends, FastAPI, Header, HTTPException, status
from pydantic import BaseModel

app = FastAPI(
    title="Salesforce WebDev API",
    description="API service for Salesforce web development automation and triage.",
    version="1.0.0",
)

API_KEY_ENV_VAR = "API_SECRET_KEY"
DEFAULT_API_KEY = "default-dev-key"


class TriageRequest(BaseModel):
    title: str
    description: str
    labels: list[str] = []


class TriageResponse(BaseModel):
    status: str
    category: str
    priority: str
    suggested_action: str


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


def verify_api_key(x_api_key: Optional[str] = Header(None)) -> str:
    """Validate the incoming API key header against environment configuration."""
    expected_key = os.getenv(API_KEY_ENV_VAR, DEFAULT_API_KEY)
    if not x_api_key or x_api_key != expected_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    return x_api_key


@app.get("/health")
def health_check() -> Dict[str, str]:
    """Public health check endpoint."""
    return {"status": "ok", "service": "salesforce-webdev-api"}


@app.post("/v1/triage", response_model=TriageResponse)
def triage_issue(
    payload: TriageRequest,
    api_key: str = Depends(verify_api_key),
) -> TriageResponse:
    """Triage an incoming issue using automated classification rules."""
    title_lower = payload.title.lower()
    if "bug" in title_lower or "error" in title_lower:
        category = "bug"
        priority = "high"
        suggested_action = "Assign to engineering on-call"
    elif "feature" in title_lower or "enhancement" in title_lower:
        category = "feature"
        priority = "medium"
        suggested_action = "Add to product backlog"
    else:
        category = "general"
        priority = "low"
        suggested_action = "Review during weekly triage"

    return TriageResponse(
        status="processed",
        category=category,
        priority=priority,
        suggested_action=suggested_action,
    )


@app.post("/v1/search")
def natural_language_search(
    payload: SearchRequest,
    api_key: str = Depends(verify_api_key),
) -> Dict[str, Any]:
    """Execute a natural language search query across release notes."""
    return {
        "query": payload.query,
        "results": [],
        "count": 0,
    }
