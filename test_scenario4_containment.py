"""Tests for Scenario 4: Containment Verification."""

from backend.app.graph.connection import graph_connection
from backend.app.graph.scenario4_seed import seed_scenario4_graph
from backend.app.graph.queries import (
    GET_CONTAINMENT_IDENTITY_QUERY,
    FIND_REMAINING_CONTAINMENT_PATHS_QUERY,
    SIMULATE_CONTAINMENT_QUERY,
    GET_CONTAINMENT_ROUTE_STATUS_QUERY,
)


IDENTITY_ID = "containment-user-01"

PRIMARY_ROUTE_ID = "primary"
ALTERNATE_ROUTE_ID = "alternate"

EXPECTED_ASSET_ID = "customer-db"


def find_remaining_paths(graph) -> list:
    """Return all qualifying active paths to critical assets."""

    return graph.ro_query(
        FIND_REMAINING_CONTAINMENT_PATHS_QUERY,
        {"identity_id": IDENTITY_ID},
    ).result_set


def simulate_containment(graph, route_id: str) -> None:
    """Block a route in the synthetic graph."""

    result = graph.query(
        SIMULATE_CONTAINMENT_QUERY,
        {
            "identity_id": IDENTITY_ID,
            "route_id": route_id,
        },
    ).result_set

    assert result, (
        f"Could not simulate containment for route: {route_id}"
    )

    assert result[0][0] == route_id, result
    assert result[0][1] == "BLOCKED", result


def main() -> None:
    """Verify containment and alternative-route detection."""

    print("=" * 60)
    print("SCENARIO 4: CONTAINMENT VERIFICATION")
    print("=" * 60)

    with graph_connection() as graph:

        # Start from a known state.
        seed_scenario4_graph(graph)

        try:
            # ------------------------------------------------
            # TEST 1: Verify the identity exists.
            # ------------------------------------------------

            print("\nTEST 1: Checking containment test identity...")

            identity_result = graph.ro_query(
                GET_CONTAINMENT_IDENTITY_QUERY,
                {"identity_id": IDENTITY_ID},
            ).result_set

            assert identity_result, (
                f"Identity not found: {IDENTITY_ID}"
            )

            print("PASS: Containment test identity exists.")

            # ------------------------------------------------
            # TEST 2: Verify both routes initially exist.
            # ------------------------------------------------

            print("\nTEST 2: Finding initial access paths...")

            initial_paths = find_remaining_paths(graph)

            assert len(initial_paths) == 2, (
                f"Expected 2 paths; found {len(initial_paths)}."
            )

            initial_routes = {
                row[2]["route_id"]
                for row in initial_paths
            }

            assert initial_routes == {
                PRIMARY_ROUTE_ID,
                ALTERNATE_ROUTE_ID,
            }, initial_routes

            for row in initial_paths:
                evidence = dict(row[2])

                assert evidence["containment_status"] == "ACTIVE"
                assert evidence["asset_id"] == EXPECTED_ASSET_ID
                assert evidence["asset_sensitivity"] == "critical"

                print(
                    f"  Active route: {evidence['route_id']} "
                    f"-> {evidence['asset_id']}"
                )

            print("PASS: Both routes reach the critical database.")

            # ------------------------------------------------
            # TEST 3: Block the primary route.
            # ------------------------------------------------

            print("\nTEST 3: Simulating containment of primary route...")

            simulate_containment(
                graph,
                PRIMARY_ROUTE_ID,
            )

            print("PASS: Primary route marked BLOCKED.")

            # ------------------------------------------------
            # TEST 4: Detect the alternative route.
            # ------------------------------------------------

            print("\nTEST 4: Checking for alternative access paths...")

            remaining_paths = find_remaining_paths(graph)

            assert len(remaining_paths) == 1, (
                "Expected exactly one remaining path after "
                f"blocking the primary route; found "
                f"{len(remaining_paths)}."
            )

            remaining_evidence = dict(remaining_paths[0][2])

            assert (
                remaining_evidence["route_id"]
                == ALTERNATE_ROUTE_ID
            ), remaining_evidence

            assert (
                remaining_evidence["containment_status"]
                == "ACTIVE"
            ), remaining_evidence

            assert (
                remaining_evidence["asset_id"]
                == EXPECTED_ASSET_ID
            ), remaining_evidence

            print(
                "PASS: Alternative route detected: "
                f"{remaining_evidence['route_id']}"
            )

            print(
                "WARNING: The critical database remains "
                "reachable through the alternative route."
            )

            # ------------------------------------------------
            # TEST 5: Block the alternative route.
            # ------------------------------------------------

            print(
                "\nTEST 5: Simulating containment of "
                "the alternative route..."
            )

            simulate_containment(
                graph,
                ALTERNATE_ROUTE_ID,
            )

            print("PASS: Alternative route marked BLOCKED.")

            # ------------------------------------------------
            # TEST 6: Verify that no qualifying path remains.
            # ------------------------------------------------

            print(
                "\nTEST 6: Verifying that no active "
                "access paths remain..."
            )

            final_paths = find_remaining_paths(graph)

            assert len(final_paths) == 0, (
                "Expected no remaining active paths, but found "
                f"{len(final_paths)}."
            )

            print(
                "PASS: No qualifying active access paths "
                "remain in the synthetic graph."
            )

            # ------------------------------------------------
            # TEST 7: Verify both route statuses.
            # ------------------------------------------------

            print("\nTEST 7: Verifying final route statuses...")

            status_rows = graph.ro_query(
                GET_CONTAINMENT_ROUTE_STATUS_QUERY,
                {"identity_id": IDENTITY_ID},
            ).result_set

            route_statuses = {
                row[0]: row[1]
                for row in status_rows
            }

            assert route_statuses == {
                PRIMARY_ROUTE_ID: "BLOCKED",
                ALTERNATE_ROUTE_ID: "BLOCKED",
            }, route_statuses

            print(f"Final route statuses: {route_statuses}")
            print("PASS: Both routes are marked BLOCKED.")

            print("\n" + "=" * 60)
            print("ALL SCENARIO 4 TESTS PASSED!")
            print("=" * 60)

        finally:
            # Restore both routes to ACTIVE so this test is
            # repeatable and does not leave the graph modified.
            seed_scenario4_graph(graph)

            print(
                "\nScenario 4 graph reset: "
                "both routes restored to ACTIVE."
            )


if __name__ == "__main__":
    main()