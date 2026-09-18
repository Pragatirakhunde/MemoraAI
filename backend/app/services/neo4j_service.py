from app.database.neo4j import driver


class Neo4jService:

    @staticmethod
    def execute_query(
        query: str,
        parameters: dict | None = None,
    ):

        with driver.session() as session:
            result = session.run(
                query,
                parameters or {},
            )

            return result.data()

    @staticmethod
    def test_connection() -> bool:

        result = Neo4jService.execute_query(
            "RETURN 1 AS result"
        )

        return (
            bool(result)
            and result[0]["result"] == 1
        )