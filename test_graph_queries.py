"""Test BlastShield's predefined FalkorDB queries."""

from pprint import pprint

from backend.app.graph.connection import graph_connection
from backend.app.graph.queries import (
    GET_IDENTITY_QUERY,
    FIND_SENSITIVE_RESOURCE_PATHS_QUERY,
)


def main():
    identity_id = "developer_07"

    with graph_connection() as graph:

        # Test 1: Check whether the identity exists.
        print("TEST 1: Checking identity...")

        identity_result = graph.ro_query(
            GET_IDENTITY_QUERY,
            {"identity_id": identity_id},
        ).result_set

        if not identity_result:
            print(f"Unknown identity: {identity_id}")
            return

        print(f"Identity found: {identity_id}")

        # Test 2: Find paths to critical data assets.
        print("\nTEST 2: Finding sensitive-resource paths...")

        path_result = graph.ro_query(
            FIND_SENSITIVE_RESOURCE_PATHS_QUERY,
            {"identity_id": identity_id},
        ).result_set

        if not path_result:
            print("No qualifying path found.")
            return

        print(f"\nAccess paths found: {len(path_result)}")

        for index, row in enumerate(path_result, start=1):
            nodes = row[0]
            edges = row[1]

            print(f"\n--- PATH {index} ---")

            print("\nNodes:")
            pprint(nodes)

            print("\nRelationships:")
            pprint(edges)

            print("\nAccess path:")
            print(" -> ".join(node["id"] for node in nodes))

        print("\n✅ All graph-query checks passed.")


if __name__ == "__main__":
    main()