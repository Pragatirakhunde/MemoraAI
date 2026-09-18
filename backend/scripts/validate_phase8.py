from app.database.postgres import SessionLocal

from app.services.hybrid_retrieval_service import (
    HybridRetrievalService,
)


db = SessionLocal()

try:

    print("=" * 70)
    print("PHASE 8 VALIDATION")
    print("=" * 70)

    query = (
        "Which database and technologies "
        "are used by the Inventory Management project?"
    )

    service = HybridRetrievalService()

    # ----------------------------------------
    # 1. Hybrid retrieval
    # ----------------------------------------

    retrieval = service.retrieve(
        db=db,
        query=query,
        organization_id=1,
        limit=5,
    )

    print("\n1. QUERY")
    print(query)

    # ----------------------------------------
    # 2. Entities
    # ----------------------------------------

    print("\n2. DETECTED ENTITIES")

    for entity in retrieval.entities:
        print(
            f"- {entity['type']}: "
            f"{entity['name']} "
            f"(confidence={entity['confidence']})"
        )

    if not retrieval.entities:
        raise RuntimeError(
            "No entities detected/resolved."
        )

    # ----------------------------------------
    # 3. Vector retrieval
    # ----------------------------------------

    vector_count = len(
        retrieval.vector_results
    )

    print("\n3. VECTOR RETRIEVAL")
    print(
        "Results:",
        vector_count,
    )

    for result in retrieval.vector_results[:3]:
        print(
            f"- {result.title} "
            f"(score={result.score})"
        )

    if vector_count == 0:
        raise RuntimeError(
            "No vector results returned."
        )

    # ----------------------------------------
    # 4. Graph retrieval
    # ----------------------------------------

    graph_count = len(
        retrieval.graph_results
    )

    print("\n4. GRAPH RETRIEVAL")
    print(
        "Results:",
        graph_count,
    )

    for result in retrieval.graph_results[:5]:
        print(
            f"- {result.entity_name} "
            f"-[:{result.relationship}]-> "
            f"{result.related_name}"
        )

    if graph_count == 0:
        raise RuntimeError(
            "No graph results returned."
        )

    # ----------------------------------------
    # 5. Fused context
    # ----------------------------------------

    fused = service.retrieve_fused_context(
        db=db,
        query=query,
        organization_id=1,
        limit=5,
        max_context_items=10,
    )

    print("\n5. FUSED CONTEXT")
    print(
        "Items:",
        len(fused),
    )

    sources = {
        item.source_type
        for item in fused
    }

    for item in fused:
        print(
            f"- {item.source_type} "
            f"(score={item.score})"
        )

    if "vector" not in sources:
        raise RuntimeError(
            "Fused context has no vector evidence."
        )

    if "graph" not in sources:
        raise RuntimeError(
            "Fused context has no graph evidence."
        )

    # ----------------------------------------
    # 6. Success
    # ----------------------------------------

    print("\n" + "=" * 70)
    print("PHASE 8 VALIDATION SUCCESSFUL")
    print("=" * 70)

finally:
    db.close()