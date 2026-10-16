"""Integration tests for the BlastShield GraphService."""

from backend.app.services.graph_service import (
    find_sensitive_resource_paths,
)


def main():
    # Test 1: An identity with a known access path.
    print("TEST 1: Investigating developer_07")

    result = find_sensitive_resource_paths("developer_07")

    assert result["status"] == "path_found", result

    assert len(result["paths"]) == 1, result

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
    assert len(path["edges"]) == 5, path["edges"]

    print("PASS: Actual path returned correctly.")

    # Test 2: An identity that does not exist.
    print("\nTEST 2: Investigating an unknown identity")

    result = find_sensitive_resource_paths("unknown_identity")

    assert result["status"] == "unknown_identity", result
    assert result["paths"] == [], result

    print("PASS: Unknown identity handled correctly.")

    # Test 3: Invalid input.
    print("\nTEST 3: Checking empty identity input")

    result = find_sensitive_resource_paths("")

    assert result["status"] == "invalid_input", result

    print("PASS: Invalid input handled correctly.")

    print("\nALL GRAPH SERVICE TESTS PASSED!")


if __name__ == "__main__":
    main()