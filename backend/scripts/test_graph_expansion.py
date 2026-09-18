from app.services.graph_query_service import (
    GraphQueryService,
)


entities = [
    "Inventory Management",
    "postgresql",
    "react",
]


for entity in entities:

    print("\n" + "=" * 60)
    print(f"ENTITY: {entity}")
    print("=" * 60)

    results = (
        GraphQueryService.expand_entity(
            organization_id=1,
            entity_name=entity,
            max_hops=2,
            limit=10,
        )
    )

    if not results:
        print("No graph expansion found.")
        continue

    for result in results:

        print("\nPath:")
        print(
            " -> ".join(
                result["path_nodes"]
            )
        )

        print("Relationships:")
        print(
            " -> ".join(
                result["path_relationships"]
            )
        )

        print(
            "Hops:",
            result["hops"],
        )