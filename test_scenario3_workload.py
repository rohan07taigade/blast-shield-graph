"""Tests for Scenario 3: Exposed Workload and Blast Radius."""

from pprint import pprint

from backend.app.graph.connection import graph_connection
from backend.app.graph.queries import (
    GET_WORKLOAD_QUERY,
    FIND_WORKLOAD_BLAST_RADIUS_QUERY,
)


def main() -> None:
    """Verify that an exposed workload's reachable assets are discovered."""

    workload_id = "exposed-api-01"

    with graph_connection() as graph:

        # TEST 1: Verify that the workload exists.
        print("TEST 1: Checking exposed-api-01...")

        workload_result = graph.ro_query(
            GET_WORKLOAD_QUERY,
            {"workload_id": workload_id},
        ).result_set

        assert workload_result, (
            f"Workload not found: {workload_id}"
        )

        print("PASS: Exposed workload found.")

        # TEST 2: Discover its potential blast radius.
        print("\nTEST 2: Finding reachable critical resources...")

        path_result = graph.ro_query(
            FIND_WORKLOAD_BLAST_RADIUS_QUERY,
            {"workload_id": workload_id},
        ).result_set

        assert path_result, (
            "Expected paths from the exposed workload "
            "to critical data assets."
        )

        print(f"PASS: Found {len(path_result)} qualifying path(s).")

        discovered_assets = set()

        for index, row in enumerate(path_result, start=1):
            nodes = [dict(node) for node in row[0]]
            edges = [dict(edge) for edge in row[1]]
            evidence = dict(row[2])

            node_ids = [node["id"] for node in nodes]
            edge_types = [edge["type"] for edge in edges]

            print(f"\n--- PATH {index} ---")

            print("\nNodes:")
            pprint(nodes)

            print("\nRelationships:")
            pprint(edges)

            print("\nEvidence:")
            pprint(evidence)

            print("\nDiscovered path:")
            print(" -> ".join(node_ids))

            # Every path must begin at the requested workload.
            assert node_ids[0] == workload_id, node_ids

            # Every path must end at a critical data asset.
            assert nodes[-1]["label"] == "DataAsset", nodes

            assert len(nodes) == 3, node_ids

            assert edge_types == [
                "RUNS_AS",
                "CAN_READ",
            ], edge_types

            assert evidence["workload_exposure"] == "PUBLIC"
            assert evidence["workload_status"] == "RUNNING"
            assert evidence["asset_sensitivity"] == "critical"

            discovered_assets.add(nodes[-1]["id"])

        # Verify that all three expected assets were discovered.
        expected_assets = {
            "customer-db",
            "payments-db",
            "config-store",
        }

        assert discovered_assets == expected_assets, (
            f"Expected assets: {expected_assets}; "
            f"discovered: {discovered_assets}"
        )

        print("\nPASS: All expected critical resources discovered.")
        print(f"Total reachable resources: {len(discovered_assets)}")


if __name__ == "__main__":
    main()