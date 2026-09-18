from app.services.graph_query_service import (
    GraphQueryService,
)


query = (
    "Which database and technologies "
    "are used by the Inventory Management project?"
)

results = (
    GraphQueryService.resolve_entities_from_query(
        organization_id=1,
        query_text=query,
    )
)

print("\nQuery:")
print(query)

print("\nResolved Graph Entities:")

for result in results:
    print(result)