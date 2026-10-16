"""Seed the synthetic infrastructure graph for BlastShield."""

from backend.app.graph.connection import graph_connection


def seed_blastshield_graph(graph) -> None:
    """
    Create the initial synthetic cloud environment.

    Uses MERGE so repeated runs do not duplicate the same
    nodes and relationships.
    """

    # Create or update the infrastructure entities.
    graph.query("""
        MERGE (i:Identity {id: 'developer_07'})
        SET i.name = 'Developer 07',
            i.status = 'ACTIVE'

        MERGE (s:Session {id: 'sess_007'})
        SET s.status = 'ACTIVE'

        MERGE (w:Workload {id: 'build-runner-03'})
        SET w.name = 'Build Runner 03',
            w.status = 'RUNNING',
            w.environment = 'DEVELOPMENT'

        MERGE (r:IAMRole {id: 'deployment-role'})
        SET r.name = 'Deployment Role'

        MERGE (pr:IAMRole {id: 'production-role'})
        SET pr.name = 'Production Role'

        MERGE (d:DataAsset {id: 'customer-db'})
        SET d.name = 'Customer Database',
            d.sensitivity = 'critical'
    """)

    # Create or reuse the relationships.
    graph.query("""
        MATCH (i:Identity {id: 'developer_07'})
        MATCH (s:Session {id: 'sess_007'})
        MATCH (w:Workload {id: 'build-runner-03'})
        MATCH (r:IAMRole {id: 'deployment-role'})
        MATCH (pr:IAMRole {id: 'production-role'})
        MATCH (d:DataAsset {id: 'customer-db'})

        MERGE (i)-[:HAS_SESSION]->(s)
        MERGE (s)-[:CAN_ACCESS]->(w)
        MERGE (w)-[:RUNS_AS]->(r)
        MERGE (r)-[:CAN_ASSUME]->(pr)
        MERGE (pr)-[:CAN_READ]->(d)
    """)


def main() -> None:
    """Initialise the BlastShield graph."""

    with graph_connection() as graph:
        seed_blastshield_graph(graph)

        node_count = graph.ro_query(
            "MATCH (n) RETURN count(n)"
        ).result_set[0][0]

        edge_count = graph.ro_query(
            "MATCH ()-[r]->() RETURN count(r)"
        ).result_set[0][0]

        print("BlastShield graph initialised successfully.")
        print(f"Total nodes: {node_count}")
        print(f"Total relationships: {edge_count}")


if __name__ == "__main__":
    main()