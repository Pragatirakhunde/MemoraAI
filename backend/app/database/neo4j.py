from neo4j import GraphDatabase

from app.core.config import settings


driver = GraphDatabase.driver(
    settings.NEO4J_URI,
    auth=(
        settings.NEO4J_USER,
        settings.NEO4J_PASSWORD,
    ),
)


def get_neo4j_driver():
    return driver


def test_neo4j_connection() -> bool:
    try:
        with driver.session() as session:
            result = session.run(
                "RETURN 1 AS result"
            )

            value = result.single()["result"]

            return value == 1

    except Exception:
        return False


def close_neo4j():
    driver.close()