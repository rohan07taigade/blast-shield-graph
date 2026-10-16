"""Tests for BlastShield graph investigation services."""

from backend.app.graph.connection import graph_connection
from backend.app.graph.scenario4_seed import seed_scenario4_graph

from backend.app.services.graph_service import (
    find_sensitive_resource_paths,
    find_excessive_permission_paths,
    find_workload_blast_radius,
    find_remaining_containment_paths,
    simulate_containment,
    get_containment_route_statuses,
)


# ============================================================
# SCENARIO 1: IDENTITY INVESTIGATION
# ============================================================

def test_scenario1_identity_investigation() -> None:
    """Verify identity-to-critical-asset path discovery."""

    print("\nTEST 1: Investigating developer_07")

    result = find_sensitive_resource_paths("developer_07")

    assert result["status"] == "path_found", result
    assert len(result["paths"]) == 1, result

    path = result["paths"][0]

    assert len(path["nodes"]) == 6, path
    assert len(path["edges"]) == 5, path

    expected_nodes = [
        "developer_07",
        "sess_007",
        "build-runner-03",
        "deployment-role",
        "production-role",
        "customer-db",
    ]

    actual_nodes = [
        node["id"] for node in path["nodes"]
    ]

    assert actual_nodes == expected_nodes, actual_nodes

    print("PASS: Scenario 1 access path returned correctly.")


def test_unknown_identity() -> None:
    """Verify that unknown identities are handled."""

    print("\nTEST 2: Checking an unknown identity")

    result = find_sensitive_resource_paths(
        "identity_does_not_exist"
    )

    assert result["status"] == "unknown_identity", result
    assert result["paths"] == []
    assert result["evidence"] == []

    print("PASS: Unknown identity handled correctly.")


def test_invalid_identity_input() -> None:
    """Verify invalid identity input is rejected."""

    print("\nTEST 3: Checking invalid identity input")

    result = find_sensitive_resource_paths("")

    assert result["status"] == "invalid_input", result
    assert result["paths"] == []
    assert result["evidence"] == []

    print("PASS: Invalid identity input handled correctly.")


# ============================================================
# SCENARIO 2: EXCESSIVE IAM PERMISSIONS
# ============================================================

def test_scenario2_excessive_iam_permissions() -> None:
    """Verify excessive IAM permission path discovery."""

    print("\nTEST 4: Investigating analytics-role")

    result = find_excessive_permission_paths(
        "analytics-role"
    )

    assert result["status"] == "path_found", result
    assert len(result["paths"]) == 1, result

    path = result["paths"][0]

    expected_nodes = [
        "analytics-role",
        "production-role",
        "customer-db",
    ]

    actual_nodes = [
        node["id"] for node in path["nodes"]
    ]

    assert actual_nodes == expected_nodes, actual_nodes
    assert len(path["edges"]) == 2, path

    additional_evidence = result["evidence"][0][
        "additional_evidence"
    ]

    assert additional_evidence["assessment"] == "EXCESSIVE"

    print("PASS: Scenario 2 path and evidence returned correctly.")


def test_unknown_iam_role() -> None:
    """Verify that unknown IAM roles are handled."""

    print("\nTEST 5: Checking an unknown IAM role")

    result = find_excessive_permission_paths(
        "role_does_not_exist"
    )

    assert result["status"] == "unknown_role", result
    assert result["paths"] == []
    assert result["evidence"] == []

    print("PASS: Unknown IAM role handled correctly.")


# ============================================================
# SCENARIO 3: EXPOSED WORKLOAD AND BLAST RADIUS
# ============================================================

def test_scenario3_workload_blast_radius() -> None:
    """Verify exposed workload blast-radius discovery."""

    print("\nTEST 6: Investigating exposed-api-01")

    result = find_workload_blast_radius("exposed-api-01")

    assert result["status"] == "path_found", result
    assert len(result["paths"]) == 3, result
    assert len(result["evidence"]) == 3, result

    expected_assets = {
        "customer-db",
        "payments-db",
        "config-store",
    }

    discovered_assets = set()

    for path in result["paths"]:
        nodes = path["nodes"]
        edges = path["edges"]

        node_ids = [
            node["id"] for node in nodes
        ]

        edge_types = [
            edge["type"] for edge in edges
        ]

        assert node_ids[0] == "exposed-api-01", node_ids
        assert len(nodes) == 3, node_ids

        assert edge_types == [
            "RUNS_AS",
            "CAN_READ",
        ], edge_types

        assert nodes[-1]["label"] == "DataAsset", nodes

        discovered_assets.add(nodes[-1]["id"])

    assert discovered_assets == expected_assets, (
        f"Expected assets: {expected_assets}; "
        f"discovered: {discovered_assets}"
    )

    # Verify the evidence for every discovered path.
    for item in result["evidence"]:
        evidence = item["additional_evidence"]

        assert evidence["workload_exposure"] == "PUBLIC"
        assert evidence["workload_status"] == "RUNNING"
        assert evidence["workload_criticality"] == "HIGH"
        assert evidence["asset_sensitivity"] == "critical"
        assert evidence["role_id"] == "api-service-role"

    print("PASS: Scenario 3 returned all three critical assets.")
    print("PASS: Exposure and workload evidence verified.")


def test_unknown_workload() -> None:
    """Verify that unknown workloads are handled."""

    print("\nTEST 7: Checking an unknown workload")

    result = find_workload_blast_radius(
        "workload_does_not_exist"
    )

    assert result["status"] == "unknown_workload", result
    assert result["paths"] == []
    assert result["evidence"] == []

    print("PASS: Unknown workload handled correctly.")


def test_invalid_workload_input() -> None:
    """Verify invalid workload input is rejected."""

    print("\nTEST 8: Checking invalid workload input")

    result = find_workload_blast_radius("")

    assert result["status"] == "invalid_input", result
    assert result["paths"] == []
    assert result["evidence"] == []

    print("PASS: Invalid workload input handled correctly.")


# ============================================================
# SCENARIO 4: CONTAINMENT VERIFICATION
# ============================================================

def test_scenario4_containment_workflow() -> None:
    """
    Test the entire containment workflow through GraphService.

    The test restores both synthetic routes to ACTIVE afterward
    so it can be repeated without leaving modified graph state.
    """

    identity_id = "containment-user-01"
    primary_route = "primary"
    alternate_route = "alternate"
    critical_asset = "customer-db"

    print("\nTEST 9: Scenario 4 containment workflow")

    # Establish a known baseline for the test.
    with graph_connection() as graph:
        seed_scenario4_graph(graph)

    try:
        # ----------------------------------------------------
        # TEST 9A: Find both initially active access paths.
        # ----------------------------------------------------

        print("\nTEST 9A: Finding initial access paths...")

        result = find_remaining_containment_paths(identity_id)

        assert result["status"] == "path_found", result
        assert len(result["paths"]) == 2, result

        initial_routes = {
            item["additional_evidence"]["route_id"]
            for item in result["evidence"]
        }

        assert initial_routes == {
            primary_route,
            alternate_route,
        }, initial_routes

        for item in result["evidence"]:
            evidence = item["additional_evidence"]

            assert evidence["containment_status"] == "ACTIVE"
            assert evidence["asset_id"] == critical_asset
            assert evidence["asset_sensitivity"] == "critical"

        print("PASS: Both active routes reach customer-db.")

        # ----------------------------------------------------
        # TEST 9B: Verify route-status service.
        # ----------------------------------------------------

        print("\nTEST 9B: Checking initial route statuses...")

        status_result = get_containment_route_statuses(identity_id)

        assert status_result["status"] == "routes_found", (
            status_result
        )

        initial_statuses = {
            route["route_id"]: route["containment_status"]
            for route in status_result["routes"]
        }

        assert initial_statuses == {
            primary_route: "ACTIVE",
            alternate_route: "ACTIVE",
        }, initial_statuses

        print("PASS: Route-status service returned both ACTIVE routes.")

        # ----------------------------------------------------
        # TEST 9C: Contain the primary route.
        # ----------------------------------------------------

        print("\nTEST 9C: Simulating primary-route containment...")

        containment_result = simulate_containment(
            identity_id,
            primary_route,
        )

        assert containment_result["status"] == "contained", (
            containment_result
        )

        assert (
            containment_result["containment_status"] == "BLOCKED"
        ), containment_result

        print("PASS: Primary route marked BLOCKED.")

        # ----------------------------------------------------
        # TEST 9D: Verify repeated requests are idempotent.
        # ----------------------------------------------------

        print("\nTEST 9D: Repeating primary containment request...")

        repeated_result = simulate_containment(
            identity_id,
            primary_route,
        )

        assert repeated_result["status"] == "already_blocked", (
            repeated_result
        )

        assert (
            repeated_result["containment_status"] == "BLOCKED"
        ), repeated_result

        print("PASS: Repeated request did not change the route state.")

        # ----------------------------------------------------
        # TEST 9E: Detect the surviving alternative route.
        # ----------------------------------------------------

        print("\nTEST 9E: Looking for remaining access paths...")

        remaining_result = find_remaining_containment_paths(
            identity_id
        )

        assert remaining_result["status"] == "path_found", (
            remaining_result
        )

        assert len(remaining_result["paths"]) == 1, (
            remaining_result
        )

        remaining_evidence = remaining_result["evidence"][0][
            "additional_evidence"
        ]

        assert (
            remaining_evidence["route_id"] == alternate_route
        ), remaining_evidence

        assert (
            remaining_evidence["containment_status"] == "ACTIVE"
        ), remaining_evidence

        assert (
            remaining_evidence["asset_id"] == critical_asset
        ), remaining_evidence

        print("PASS: Alternative route detected.")
        print(
            "WARNING: customer-db remains reachable through "
            "the alternate route."
        )

        # ----------------------------------------------------
        # TEST 9F: Verify intermediate route statuses.
        # ----------------------------------------------------

        print("\nTEST 9F: Checking intermediate route statuses...")

        status_result = get_containment_route_statuses(identity_id)

        intermediate_statuses = {
            route["route_id"]: route["containment_status"]
            for route in status_result["routes"]
        }

        assert intermediate_statuses == {
            primary_route: "BLOCKED",
            alternate_route: "ACTIVE",
        }, intermediate_statuses

        print("PASS: One route BLOCKED; alternative route ACTIVE.")

        # ----------------------------------------------------
        # TEST 9G: Contain the alternative route.
        # ----------------------------------------------------

        print("\nTEST 9G: Simulating alternate-route containment...")

        containment_result = simulate_containment(
            identity_id,
            alternate_route,
        )

        assert containment_result["status"] == "contained", (
            containment_result
        )

        assert (
            containment_result["containment_status"] == "BLOCKED"
        ), containment_result

        print("PASS: Alternative route marked BLOCKED.")

        # ----------------------------------------------------
        # TEST 9H: Verify that no qualifying paths remain.
        # ----------------------------------------------------

        print("\nTEST 9H: Verifying final reachability...")

        final_result = find_remaining_containment_paths(identity_id)

        assert final_result["status"] == "no_path", final_result
        assert final_result["paths"] == []
        assert final_result["evidence"] == []

        print("PASS: No qualifying active paths remain.")

        # ----------------------------------------------------
        # TEST 9I: Verify final route statuses.
        # ----------------------------------------------------

        print("\nTEST 9I: Verifying final containment statuses...")

        final_status_result = get_containment_route_statuses(
            identity_id
        )

        assert final_status_result["status"] == "routes_found", (
            final_status_result
        )

        final_statuses = {
            route["route_id"]: route["containment_status"]
            for route in final_status_result["routes"]
        }

        assert final_statuses == {
            primary_route: "BLOCKED",
            alternate_route: "BLOCKED",
        }, final_statuses

        print(f"Final route statuses: {final_statuses}")
        print("PASS: Both routes are BLOCKED.")

        # ----------------------------------------------------
        # TEST 9J: Validate input and unknown-entity handling.
        # ----------------------------------------------------

        print("\nTEST 9J: Checking invalid and unknown inputs...")

        invalid_containment = simulate_containment(
            "",
            primary_route,
        )

        assert (
            invalid_containment["status"] == "invalid_input"
        ), invalid_containment

        invalid_paths = find_remaining_containment_paths("")

        assert invalid_paths["status"] == "invalid_input", invalid_paths

        invalid_statuses = get_containment_route_statuses("")

        assert (
            invalid_statuses["status"] == "invalid_input"
        ), invalid_statuses

        unknown_paths = find_remaining_containment_paths(
            "identity_does_not_exist"
        )

        assert (
            unknown_paths["status"] == "unknown_identity"
        ), unknown_paths

        unknown_statuses = get_containment_route_statuses(
            "identity_does_not_exist"
        )

        assert (
            unknown_statuses["status"] == "unknown_identity"
        ), unknown_statuses

        unknown_route = simulate_containment(
            identity_id,
            "route_does_not_exist",
        )

        assert unknown_route["status"] == "unknown_route", (
            unknown_route
        )

        print("PASS: Invalid inputs, unknown identities, and unknown routes handled.")

    finally:
        # Restore both routes so this test can be rerun.
        with graph_connection() as graph:
            seed_scenario4_graph(graph)

        print(
            "\nCleanup complete: both synthetic routes restored "
            "to ACTIVE."
        )

    print("PASS: Scenario 4 service workflow completed.")


# ============================================================
# TEST RUNNER
# ============================================================

def main() -> None:
    """Execute all service-layer tests."""

    test_scenario1_identity_investigation()
    test_unknown_identity()
    test_invalid_identity_input()

    test_scenario2_excessive_iam_permissions()
    test_unknown_iam_role()

    test_scenario3_workload_blast_radius()
    test_unknown_workload()
    test_invalid_workload_input()

    test_scenario4_containment_workflow()

    print("\n" + "=" * 55)
    print("ALL GRAPH SERVICE TESTS PASSED!")
    print("=" * 55)


if __name__ == "__main__":
    main()