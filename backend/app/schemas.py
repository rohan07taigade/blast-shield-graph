
from typing import Literal

from pydantic import BaseModel, Field


class InvestigationRequest(BaseModel):
    alert_id: str = Field(min_length=1, max_length=64)


class GraphNode(BaseModel):
    id: str
    label: str
    type: str


class GraphEdge(BaseModel):
    source: str
    target: str
    type: str


class GraphPath(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]


class ProposedAction(BaseModel):
    action_id: str
    action_type: Literal[
        "REVOKE_SESSION",
        "ISOLATE_WORKLOAD",
    ]
    target_id: str
    title: str
    reason: str
    status: Literal["PROPOSED"]


class InvestigationResponse(BaseModel):
    investigation_id: str
    alert_id: str
    identity_id: str

    outcome: Literal[
        "path_found",
        "no_path_in_graph",
    ]

    risk_score: int = Field(ge=0, le=100)
    severity: Literal[
        "LOW",
        "MEDIUM",
        "HIGH",
        "CRITICAL",
    ]

    summary: str
    paths: list[GraphPath]
    evidence: list[str]
    proposed_actions: list[ProposedAction]
    warnings: list[str] = Field(default_factory=list)

    # Makes it clear that this result is synthetic.
    data_source: Literal["mock"] = "mock"