from falkordb import FalkorDB


GRAPH_NAME = "blastshield"


def seed_graph(graph):
    """Create a small, repeatable synthetic cloud environment."""

    print("Seeding the BlastShield graph...")

    # Create the entities.
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

    # Connect the entities through their represented permissions.
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

    print("Graph seeding complete.")


def find_sensitive_resource_paths(graph, identity_id):
    """Find a represented access path to a critical data asset."""

    query = """
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

        RETURN [n IN nodes(p) | n.id] AS path
    """

    result = graph.ro_query(
        query,
        {"identity_id": identity_id}
    )

    return result.result_set


def main():
    db = FalkorDB(host="localhost", port=6379)

    try:
        graph = db.select_graph(GRAPH_NAME)

        seed_graph(graph)

        print("\nInvestigating developer_07...")

        paths = find_sensitive_resource_paths(
            graph,
            "developer_07"
        )

        if paths:
            print("\n✅ ACCESS PATH FOUND\n")

            for index, row in enumerate(paths, start=1):
                path = row[0]

                print(f"Path {index}:")
                print(" -> ".join(path))

        else:
            print(
                "\nNo qualifying path found in the "
                "represented graph."
            )

    except Exception as error:
        print(f"\n❌ BlastShield graph test failed: {error}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()