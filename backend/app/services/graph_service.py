"""Reusable graph investigation services for BlastShield."""

import logging
from typing import Any

from backend.app.graph.connection import graph_connection
from backend.app.graph.queries import (
    GET_IDENTITY_QUERY,
    FIND_SENSITIVE_RESOURCE_PATHS_QUERY,
)

logger = logging.getLogger(__name__)


def find_sensitive_resource_paths(
    identity_id: str,
) -> dict[str, Any]:
    """
    Find represented access paths from an identity to critical data assets.

    Returns a structured result suitable for the API, MCP tools,
    and frontend.
    """

    # Validate the input before querying the database.
    if not isinstance(identity_id, str) or not identity_id.strip():
        return {
            "status": "invalid_input",
            "identity_id": identity_id,
            "paths": [],
            "evidence": [],
            "error": "A valid identity ID is required.",
        }

    identity_id = identity_id.strip()

    try:
        with graph_connection() as graph:

            # Step 1: Check whether the identity exists.
            identity_result = graph.ro_query(
                GET_IDENTITY_QUERY,
                {"identity_id": identity_id},
            ).result_set

            if not identity_result:
                return {
                    "status": "unknown_identity",
                    "identity_id": identity_id,
                    "paths": [],
                    "evidence": [],
                    "error": None,
                }

            # Step 2: Retrieve qualifying paths from FalkorDB.
            query_result = graph.ro_query(
                FIND_SENSITIVE_RESOURCE_PATHS_QUERY,
                {"identity_id": identity_id},
            ).result_set

            if not query_result:
                return {
                    "status": "no_path",
                    "identity_id": identity_id,
                    "paths": [],
                    "evidence": [],
                    "error": None,
                }

            # Step 3: Convert database records into plain dictionaries.
            paths = []
            evidence = []

            for index, row in enumerate(query_result, start=1):
                nodes = [dict(node) for node in row[0]]
                edges = [dict(edge) for edge in row[1]]

                paths.append({
                    "nodes": nodes,
                    "edges": edges,
                })

                evidence.append({
                    "path_index": index,
                    "node_ids": [
                        node["id"] for node in nodes
                    ],
                    "relationship_types": [
                        edge["type"] for edge in edges
                    ],
                })

            return {
                "status": "path_found",
                "identity_id": identity_id,
                "paths": paths,
                "evidence": evidence,
                "error": None,
            }

    except Exception:
        # Keep technical details in server logs rather than exposing
        # database errors directly to the caller.
        logger.exception(
            "Graph investigation failed for identity %s",
            identity_id,
        )

        return {
            "status": "query_error",
            "identity_id": identity_id,
            "paths": [],
            "evidence": [],
            "error": "Graph query failed. Check backend logs.",
        }