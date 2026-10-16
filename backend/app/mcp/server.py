
from typing import Any

from mcp.server import MCPServer
from app.mock_graph_service import get_mock_investigation

mcp = MCPServer("BlastShield Investigation Tools")

MOCK_IDENTITIES = {
    "developer_07": "BH-1042",
    "developer_09": "BH-1043",
}


def get_result(alert_id: str) -> dict[str, Any] | None:
    result = get_mock_investigation(alert_id)
    if result is None:
        return None
    if hasattr(result, "model_dump"):
        return result.model_dump(mode="json")
    return result.dict()


@mcp.tool()
def investigate_alert(alert_id: str) -> dict[str, Any]:
    """Retrieve investigation evidence for a mock alert."""
    result = get_result(alert_id)
    if result is None:
        return {
            "status": "unknown_alert",
            "alert_id": alert_id,
        }
    return {"status": "found", "investigation": result}


@mcp.tool()
def find_sensitive_resource_paths(
    identity_id: str,
) -> dict[str, Any]:
    """Return represented access paths for a known identity."""
    alert_id = MOCK_IDENTITIES.get(identity_id)
    if alert_id is None:
        return {
            "status": "unknown_identity",
            "identity_id": identity_id,
            "paths": [],
        }

    result = get_result(alert_id)
    if result is None:
        return {
            "status": "mock_data_error",
            "identity_id": identity_id,
            "paths": [],
        }

    return {
        "status": result["outcome"],
        "identity_id": identity_id,
        "paths": result["paths"],
        "warnings": result["warnings"],
    }


@mcp.tool()
def get_blast_radius(identity_id: str) -> dict[str, Any]:
    """Summarise workloads, roles and data assets in the paths."""
    alert_id = MOCK_IDENTITIES.get(identity_id)
    if alert_id is None:
        return {
            "status": "unknown_identity",
            "identity_id": identity_id,
            "entities": [],
        }

    result = get_result(alert_id)
    if result is None:
        return {
            "status": "mock_data_error",
            "identity_id": identity_id,
            "entities": [],
        }

    entities = {}
    for path in result["paths"]:
        for node in path["nodes"]:
            if node["type"] in {
                "Workload",
                "IAMRole",
                "DataAsset",
            }:
                entities[node["id"]] = node

    return {
        "status": result["outcome"],
        "identity_id": identity_id,
        "path_count": len(result["paths"]),
        "entities": list(entities.values()),
        "warnings": result["warnings"],
    }


if __name__ == "__main__":
    mcp.run()