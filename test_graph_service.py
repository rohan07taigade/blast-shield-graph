"""Integration tests for the BlastShield GraphService."""

from backend.app.services.graph_service import (
    find_sensitive_resource_paths,
    find_excessive_permission_paths,
)


def test_scenario1_identity_investigation():
    """Verify the identity-to-data access path."""

    print("TEST 1: Investigating developer_07")

    result = find_sensitive_resource_paths("developer_07")

    assert result["status"] == "path_found", result
    assert result["identity_id"] == "developer_07"
    assert len(result["paths"]) == 1

    path = result["paths"][0]

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
    assert len(path["edges"]) == 5

    print("PASS: Scenario 1 access path returned correctly.")


def test_unknown_identity():
    """Verify handling of an identity that does not exist."""

    print("\nTEST 2: Checking an unknown identity")

    result = find_sensitive_resource_paths("unknown_identity")

    assert result["status"] == "unknown_identity", result
    assert result["paths"] == []

    print("PASS: Unknown identity handled correctly.")


def test_invalid_identity():
    """Verify handling of invalid identity input."""

    print("\nTEST 3: Checking invalid identity input")

    result = find_sensitive_resource_paths("")

    assert result["status"] == "invalid_input", result
    assert result["paths"] == []

    print("PASS: Invalid input handled correctly.")


def test_scenario2_excessive_permissions():
    """Verify the excessive IAM permission investigation."""

    print("\nTEST 4: Investigating analytics-role")

    result = find_excessive_permission_paths("analytics-role")

    assert result["status"] == "path_found", result
    assert result["role_id"] == "analytics-role"
    assert len(result["paths"]) == 1

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

    expected_relationships = [
        "CAN_ASSUME",
        "CAN_READ",
    ]

    actual_relationships = [
        edge["type"] for edge in path["edges"]
    ]

    assert actual_relationships == expected_relationships

    # Confirm that the excessive permission evidence is preserved.
    evidence = result["evidence"][0]["additional_evidence"]

    assert evidence["assessment"] == "EXCESSIVE"
    assert "outside its intended scope" in evidence["reason"]

    # Confirm that the actual edge also includes its properties.
    permission_edge = path["edges"][0]

    assert permission_edge["properties"]["assessment"] == "EXCESSIVE"

    print("PASS: Scenario 2 path and evidence returned correctly.")


def test_unknown_role():
    """Verify handling of a role that does not exist."""

    print("\nTEST 5: Checking an unknown IAM role")

    result = find_excessive_permission_paths("unknown-role")

    assert result["status"] == "unknown_role", result
    assert result["paths"] == []

    print("PASS: Unknown IAM role handled correctly.")


def main():
    test_scenario1_identity_investigation()
    test_unknown_identity()
    test_invalid_identity()
    test_scenario2_excessive_permissions()
    test_unknown_role()

    print("\nALL GRAPH SERVICE TESTS PASSED!")


if __name__ == "__main__":
    main()