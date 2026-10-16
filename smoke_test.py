"""End-to-end smoke test for BlastShield's graph investigation."""

from backend.app.graph.connection import graph_connection
from backend.app.graph.seed import seed_blastshield_graph
from backend.app.services.graph_service import (
    find_sensitive_resource_paths,
)


def main() -> None:
    """Seed the graph and verify a known investigation."""

    print("Initializing BlastShield graph...")

    # Seed the synthetic environment using the reusable module.
    with graph_connection() as graph:
        seed_blastshield_graph(graph)

    print("Graph initialised successfully.")
    print("\nInvestigating developer_07...")

    # Use the GraphService instead of executing Cypher directly.
    result = find_sensitive_resource_paths("developer_07")

    if result["status"] != "path_found":
        print("Investigation did not find the expected path.")
        print(f"Status: {result['status']}")
        print(f"Error: {result['error']}")
        return

    print(f"\nStatus: {result['status']}")
    print(f"Paths found: {len(result['paths'])}")

    for index, path in enumerate(result["paths"], start=1):
        node_ids = [node["id"] for node in path["nodes"]]

        print(f"\nPath {index}:")
        print(" -> ".join(node_ids))

        print("\nRelationships:")
        for edge in path["edges"]:
            print(
                f"{edge['source']} "
                f"--[{edge['type']}]--> "
                f"{edge['target']}"
            )

    print("\n✅ BlastShield smoke test passed!")


if __name__ == "__main__":
    main()