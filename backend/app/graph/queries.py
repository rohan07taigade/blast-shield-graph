"""Predefined Cypher queries for BlastShield."""

# Query 1: Check whether an identity exists.
GET_IDENTITY_QUERY = """
MATCH (i:Identity {id: $identity_id})
RETURN i.id AS id
LIMIT 1
"""


# Query 2: Find paths from active sessions to critical data assets.
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
            type: type(rel)
        }
    ] AS edges
"""