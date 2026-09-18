from app.database.neo4j import (
    test_neo4j_connection,
)

from app.services.neo4j_service import (
    Neo4jService,
)


print(
    "Direct connection:",
    test_neo4j_connection(),
)

print(
    "Service connection:",
    Neo4jService.test_connection(),
)