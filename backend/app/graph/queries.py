"""Predefined Cypher queries used by BlastShield."""


# ============================================================
# SCENARIO 1: SUSPICIOUS LOGIN / IDENTITY INVESTIGATION
# ============================================================

GET_IDENTITY_QUERY = """
MATCH (i:Identity {id: $identity_id})
RETURN i.id AS id
LIMIT 1
"""


FIND_SENSITIVE_RESOURCE_PATHS_QUERY = """
MATCH p =
    (i:Identity {id: $identity_id})
    -[:HAS_SESSION]->
    (s:Session {status: 'ACTIVE'})
    -[:CAN_ACCESS]->
    (w:Workload {status: 'RUNNING'})
    -[:RUNS_AS]->
    (r:IAMRole)
    -[:CAN_ASSUME]->
    (pr:IAMRole)
    -[:CAN_READ]->
    (d:DataAsset {sensitivity: 'critical'})

RETURN
    [
        node IN nodes(p) |
        {
            id: node.id,
            label: labels(node)[0]
        }
    ] AS nodes,

    [
        rel IN relationships(p) |
        {
            source: startNode(rel).id,
            target: endNode(rel).id,
            type: type(rel),
            properties: properties(rel)
        }
    ] AS edges
"""


# ============================================================
# SCENARIO 2: EXCESSIVE IAM PERMISSIONS
# ============================================================

GET_IAM_ROLE_QUERY = """
MATCH (r:IAMRole {id: $role_id})
RETURN r.id AS id
LIMIT 1
"""


FIND_EXCESSIVE_PERMISSION_PATHS_QUERY = """
MATCH p =
    (ar:IAMRole {id: $role_id})
    -[permission:CAN_ASSUME {assessment: 'EXCESSIVE'}]->
    (pr:IAMRole)
    -[:CAN_READ]->
    (d:DataAsset {sensitivity: 'critical'})

RETURN
    [
        node IN nodes(p) |
        {
            id: node.id,
            label: labels(node)[0]
        }
    ] AS nodes,

    [
        rel IN relationships(p) |
        {
            source: startNode(rel).id,
            target: endNode(rel).id,
            type: type(rel),
            properties: properties(rel)
        }
    ] AS edges,

    properties(permission) AS excessive_permission
"""