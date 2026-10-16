"""Reusable graph investigation services for BlastShield."""

import logging
from typing import Any

from backend.app.graph.connection import graph_connection
from backend.app.graph.queries import (
    GET_IDENTITY_QUERY,
    FIND_SENSITIVE_RESOURCE_PATHS_QUERY,
    GET_IAM_ROLE_QUERY,
    FIND_EXCESSIVE_PERMISSION_PATHS_QUERY,
    GET_WORKLOAD_QUERY,
    FIND_WORKLOAD_BLAST_RADIUS_QUERY,
)

logger = logging.getLogger(__name__)


def _format_paths(
    query_result: list,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """
    Convert FalkorDB query rows into plain dictionaries.

    Supports queries returning:
        1. Nodes
        2. Edges
        3. Optional additional evidence
    """

    paths = []
    evidence = []

    for index, row in enumerate(query_result, start=1):
        nodes = [dict(node) for node in row[0]]

        edges = []

        for edge in row[1]:
            edge_data = dict(edge)

            # Normalise nested relationship properties.
            edge_data["properties"] = dict(
                edge_data.get("properties") or {}
            )

            edges.append(edge_data)

        paths.append({
            "nodes": nodes,
            "edges": edges,
        })

        evidence_item = {
            "path_index": index,
            "node_ids": [
                node["id"] for node in nodes
            ],
            "relationship_types": [
                edge["type"] for edge in edges
            ],
        }

        # Preserve any additional evidence returned by the query.
        if len(row) > 2 and row[2] is not None:
            evidence_item["additional_evidence"] = dict(row[2])

        evidence.append(evidence_item)

    return paths, evidence


def _investigate_paths(
    entity_id: str,
    parameter_name: str,
    existence_query: str,
    path_query: str,
    unknown_status: str,
) -> dict[str, Any]:
    """
    Execute a predefined investigation for a graph entity.

    First verifies that the entity exists, then searches for
    qualifying paths and formats the results.
    """

    if not isinstance(entity_id, str) or not entity_id.strip():
        return {
            "status": "invalid_input",
            parameter_name: entity_id,
            "paths": [],
            "evidence": [],
            "error": "A valid entity ID is required.",
        }

    entity_id = entity_id.strip()

    try:
        with graph_connection() as graph:

            # Step 1: Verify that the requested entity exists.
            entity_result = graph.ro_query(
                existence_query,
                {parameter_name: entity_id},
            ).result_set

            if not entity_result:
                return {
                    "status": unknown_status,
                    parameter_name: entity_id,
                    "paths": [],
                    "evidence": [],
                    "error": None,
                }

            # Step 2: Find qualifying graph paths.
            query_result = graph.ro_query(
                path_query,
                {parameter_name: entity_id},
            ).result_set

            if not query_result:
                return {
                    "status": "no_path",
                    parameter_name: entity_id,
                    "paths": [],
                    "evidence": [],
                    "error": None,
                }

            # Step 3: Format paths and evidence.
            paths, evidence = _format_paths(query_result)

            return {
                "status": "path_found",
                parameter_name: entity_id,
                "paths": paths,
                "evidence": evidence,
                "error": None,
            }

    except Exception:
        logger.exception(
            "Graph investigation failed for %s=%s",
            parameter_name,
            entity_id,
        )

        return {
            "status": "query_error",
            parameter_name: entity_id,
            "paths": [],
            "evidence": [],
            "error": "Graph query failed. Check backend logs.",
        }


# ============================================================
# SCENARIO 1: IDENTITY INVESTIGATION
# ============================================================

def find_sensitive_resource_paths(
    identity_id: str,
) -> dict[str, Any]:
    """
    Find represented access paths from an identity to critical assets.

    Scenario 1: Suspicious-login and identity investigation.
    """

    return _investigate_paths(
        entity_id=identity_id,
        parameter_name="identity_id",
        existence_query=GET_IDENTITY_QUERY,
        path_query=FIND_SENSITIVE_RESOURCE_PATHS_QUERY,
        unknown_status="unknown_identity",
    )


# ============================================================
# SCENARIO 2: EXCESSIVE IAM PERMISSIONS
# ============================================================

def find_excessive_permission_paths(
    role_id: str,
) -> dict[str, Any]:
    """
    Find paths through permissions classified as excessive.

    Scenario 2: Excessive IAM permissions.
    """

    return _investigate_paths(
        entity_id=role_id,
        parameter_name="role_id",
        existence_query=GET_IAM_ROLE_QUERY,
        path_query=FIND_EXCESSIVE_PERMISSION_PATHS_QUERY,
        unknown_status="unknown_role",
    )


# ============================================================
# SCENARIO 3: EXPOSED WORKLOAD AND BLAST RADIUS
# ============================================================

def find_workload_blast_radius(
    workload_id: str,
) -> dict[str, Any]:
    """
    Find represented paths from a publicly exposed workload
    to reachable critical data assets.

    Scenario 3: Exposed workload and potential blast radius.

    This identifies graph-represented reachability. It does not
    prove that the workload has been compromised or exploited.
    """

    return _investigate_paths(
        entity_id=workload_id,
        parameter_name="workload_id",
        existence_query=GET_WORKLOAD_QUERY,
        path_query=FIND_WORKLOAD_BLAST_RADIUS_QUERY,
        unknown_status="unknown_workload",
    )