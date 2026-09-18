from app.services.neo4j_service import Neo4jService


query = """
CREATE (n:TestNode {
    name: $name
})
RETURN n.name AS name
"""

result = Neo4jService.execute_query(
    query,
    {
        "name": "Enterprise Memory Engine"
    },
)

print(result)