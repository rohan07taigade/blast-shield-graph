
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.mock_graph_service import get_mock_investigation
from app.schemas import (
    InvestigationRequest,
    InvestigationResponse,
)

app = FastAPI(
    title="BlastShield API",
    description="Member 2 development API using mock data",
    version="0.1.0",
)

# Allows the Vite frontend to call the API during development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


MOCK_ALERTS = [
    {
        "id": "BH-1042",
        "title": "Suspicious login with a potential path to critical data",
        "status": "NEW",
    },
    {
        "id": "BH-1043",
        "title": "Suspicious login with no qualifying critical-data path",
        "status": "NEW",
    },
]


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "mode": "mock",
    }


@app.get("/api/alerts")
def list_alerts():
    return {"items": MOCK_ALERTS}


@app.post(
    "/api/investigations",
    response_model=InvestigationResponse,
)
def investigate(
    request: InvestigationRequest,
) -> InvestigationResponse:
    result = get_mock_investigation(request.alert_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail={
                "outcome": "unknown_alert",
                "message": (
                    f"Alert '{request.alert_id}' "
                    "does not exist in the mock dataset."
                ),
            },
        )

    return result