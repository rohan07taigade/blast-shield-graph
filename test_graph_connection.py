from backend.app.graph.connection import graph_connection


def main():
    try:
        with graph_connection() as graph:
            result = graph.ro_query(
                "RETURN 1 AS connection_test"
            )

            print("Connected successfully!")
            print("Query result:", result.result_set)

    except Exception as error:
        print(f"Connection test failed: {error}")
        raise


if __name__ == "__main__":
    main()