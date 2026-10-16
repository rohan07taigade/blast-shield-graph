"""Tests for BlastShield graph investigation services."""

from backend.app.services.graph_service import (
    find_sensitive_resource_paths,
    find_excessive_permission_paths,
    find_workload_blast_radius,
)


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

    # Verify evidence returned for every discovered path.
    for item in result["evidence"]:
        evidence = item["additional_evidence"]

        assert evidence["workload_exposure"] == "PUBLIC"
        assert evidence["workload_status"] == "RUNNING"
        assert evidence["workload_criticality"] == "HIGH"
        assert evidence["asset_sensitivity"] == "critical"
        assert evidence["role_id"] == "api-service-role"

    print("PASS: Scenario 3 returned all three critical assets.")
    print("PASS: Exposure, workload status, and asset evidence verified.")


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


def main() -> None:
    """Run all graph service tests."""

    test_scenario1_identity_investigation()
    test_unknown_identity()
    test_invalid_identity_input()

    test_scenario2_excessive_iam_permissions()
    test_unknown_iam_role()

    test_scenario3_workload_blast_radius()
    test_unknown_workload()
    test_invalid_workload_input()

    print("\n" + "=" * 55)
    print("ALL GRAPH SERVICE TESTS PASSED!")
    print("=" * 55)


if __name__ == "__main__":
    main()