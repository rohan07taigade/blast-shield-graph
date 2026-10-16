# BlastShield GraphService Contract

## Purpose

GraphService provides graph investigation functions backed by
FalkorDB. It returns actual graph evidence for the AI agent
and frontend.

## Initial Function

find_sensitive_resource_paths(identity_id: str) -> dict

## Responsibilities

1. Find the requested identity.
2. Identify its active sessions.
3. Follow the represented access and permission relationships.
4. Find paths to critical data assets.
5. Return the actual nodes and relationships in each path.
6. Distinguish missing identities, empty results, and query errors.

## Response Structure

{
  "status": "path_found",
  "identity_id": "developer_07",
  "paths": [
    {
      "nodes": [],
      "edges": []
    }
  ],
  "evidence": [],
  "error": null
}

## Allowed Status Values

- path_found
- no_path
- unknown_identity
- query_error
- invalid_input

## Path Node Structure

{
  "id": "developer_07",
  "label": "Identity"
}

## Path Edge Structure

{
  "source": "developer_07",
  "target": "sess_007",
  "type": "HAS_SESSION"
}

## Implementation Rules

- FalkorDB is the source of graph evidence.
- Cypher queries must be predefined and parameterised.
- The service must not depend on the LLM or frontend.
- Actual graph relationships must be returned.
- A failed query must not be reported as an empty result.
- Member 2 must be able to use the service without depending
  on its internal Cypher implementation.