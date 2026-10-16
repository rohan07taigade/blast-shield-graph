from app.schemas import InvestigationResponse


def get_mock_investigation(
    alert_id: str,
) -> InvestigationResponse | None:
    """
    Temporary mock service.
    Replace this dependency with Member 1's real
    GraphService after both interfaces are agreed upon.
    """

    if alert_id == "BH-1042":
        return InvestigationResponse(
            investigation_id="INV-BH-1042",
            alert_id="BH-1042",
            identity_id="developer_07",
            outcome="path_found",
            risk_score=88,
            severity="HIGH",
            summary=(
                "The represented graph contains a potential "
                "access path from the developer identity to "
                "a critical customer database."
            ),
            paths=[
                {
                    "nodes": [
                        {
                            "id": "developer_07",
                            "label": "Developer Account",
                            "type": "Identity",
                        },
                        {
                            "id": "sess_007",
                            "label": "Active Session",
                            "type": "Session",
                        },
                        {
                            "id": "build-runner-03",
                            "label": "Build Runner",
                            "type": "Workload",
                        },
                        {
                            "id": "deployment-role",
                            "label": "Deployment Role",
                            "type": "IAMRole",
                        },
                        {
                            "id": "production-role",
                            "label": "Production Role",
                            "type": "IAMRole",
                        },
                        {
                            "id": "customer-db",
                            "label": "Customer Database",
                            "type": "DataAsset",
                        },
                    ],
                    "edges": [
                        {
                            "source": "developer_07",
                            "target": "sess_007",
                            "type": "HAS_SESSION",
                        },
                        {
                            "source": "sess_007",
                            "target": "build-runner-03",
                            "type": "CAN_ACCESS",
                        },
                        {
                            "source": "build-runner-03",
                            "target": "deployment-role",
                            "type": "RUNS_AS",
                        },
                        {
                            "source": "deployment-role",
                            "target": "production-role",
                            "type": "CAN_ASSUME",
                        },
                        {
                            "source": "production-role",
                            "target": "customer-db",
                            "type": "CAN_READ",
                        },
                    ],
                }
            ],
            evidence=[
                "A suspicious login finding is associated with BH-1042.",
                "The example includes an active session.",
                "The represented relationships lead to a critical data asset.",
            ],
            proposed_actions=[
                {
                    "action_id": "ACT-BH-1042-01",
                    "action_type": "REVOKE_SESSION",
                    "target_id": "sess_007",
                    "title": "Revoke the suspicious session",
                    "reason": (
                        "Test whether removing this session "
                        "interrupts the represented access path."
                    ),
                    "status": "PROPOSED",
                }
            ],
            warnings=[
                "Mock result only; not retrieved from FalkorDB.",
                "Potential reachability does not prove successful exploitation.",
                "Risk score is illustrative, not a production security rating.",
            ],
        )

    if alert_id == "BH-1043":
        return InvestigationResponse(
            investigation_id="INV-BH-1043",
            alert_id="BH-1043",
            identity_id="developer_09",
            outcome="no_path_in_graph",
            risk_score=42,
            severity="MEDIUM",
            summary=(
                "No qualifying path to a critical data asset "
                "is represented in this mock scenario."
            ),
            paths=[],
            evidence=[
                "The synthetic scenario contains no qualifying path "
                "from developer_09 to a critical data asset."
            ],
            proposed_actions=[],
            warnings=[
                "Mock result only; not retrieved from FalkorDB.",
                "No path in the represented graph does not prove "
                "that the real environment is safe.",
                "The suspicious login still requires appropriate investigation.",
            ],
        )

    return None