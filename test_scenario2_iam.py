"""Integration tests for BlastShield Scenario 2: Excessive IAM Permissions."""

from pprint import pprint

from backend.app.graph.connection import graph_connection
from backend.app.graph.queries import (
    GET_IAM_ROLE_QUERY,
    FIND_EXCESSIVE_PERMISSION_PATHS_QUERY,
)


def main() -> None:
    """Test the excessive IAM permission investigation."""

    role_id = "analytics-role"

    with graph_connection() as graph:

        # TEST 1: Verify that the analytics role exists.
        print("TEST 1: Checking analytics-role...")

        role_result = graph.ro_query(
            GET_IAM_ROLE_QUERY,
            {"role_id": role_id},
        ).result_set

        assert role_result, f"Role not found: {role_id}"

        print("PASS: Analytics role found.")

        # TEST 2: Find paths through excessive permissions.
        print("\nTEST 2: Finding excessive-permission paths...")

        path_result = graph.ro_query(
            FIND_EXCESSIVE_PERMISSION_PATHS_QUERY,
            {"role_id": role_id},
        ).result_set

        assert path_result, "Expected an excessive-permission path."

        print(f"PASS: Found {len(path_result)} qualifying path(s).")

        for index, row in enumerate(path_result, start=1):
            nodes = [dict(node) for node in row[0]]
            edges = [dict(edge) for edge in row[1]]
            permission = dict(row[2])

            node_ids = [node["id"] for node in nodes]
            edge_types = [edge["type"] for edge in edges]

            print(f"\n--- PATH {index} ---")

            print("\nNodes:")
            pprint(nodes)

            print("\nRelationships:")
            pprint(edges)

            print("\nExcessive permission:")
            pprint(permission)

            print("\nDiscovered path:")
            print(" -> ".join(node_ids))

            # Confirm that the expected path was retrieved.
            assert node_ids == [
                "analytics-role",
                "production-role",
                "customer-db",
            ], f"Unexpected path: {node_ids}"

            assert edge_types == [
                "CAN_ASSUME",
                "CAN_READ",
            ], f"Unexpected relationships: {edge_types}"

            assert permission.get("assessment") == "EXCESSIVE", (
                f"Unexpected permission assessment: {permission}"
            )

    print("\nALL SCENARIO 2 TESTS PASSED!")


if __name__ == "__main__":
    main()