from app.services.graph_query_service import (
    GraphQueryService,
)


print("\n=== PROJECT KNOWLEDGE ===")

result = (
    GraphQueryService.get_project_knowledge(
        organization_id=1,
        project_name="Inventory Management",
    )
)

print(result)


print("\n=== ENTITY NEIGHBORHOOD ===")

result = (
    GraphQueryService.get_entity_neighborhood(
        organization_id=1,
        entity_name="postgresql",
    )
)

for item in result:
    print(item)