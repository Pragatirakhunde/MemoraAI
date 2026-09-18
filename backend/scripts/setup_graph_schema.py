from app.services.graph_schema_service import (
    GraphSchemaService,
)


print("Creating Neo4j constraints...")

GraphSchemaService.create_constraints()

print("\nNeo4j constraints:")

constraints = (
    GraphSchemaService.get_constraints()
)

for constraint in constraints:
    print(
        f"- {constraint.get('name')}"
    )

print(
    "\nGraph schema setup complete."
)