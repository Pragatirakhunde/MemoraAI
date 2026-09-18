from app.ai_engine.graph.nodes import generate_answer, retrieve_knowledge
from app.ai_engine.graph.workflow import build_agent_graph
from app.database.postgres import SessionLocal


def main():
    db = SessionLocal()

    try:
        query = "What technologies are used by Inventory Management?"

        def retrieval_node(state):
            return retrieve_knowledge(state, db)

        def generation_node(state):
            return generate_answer(state)

        graph = build_agent_graph(
            retrieval_node=retrieval_node,
            generation_node=generation_node,
        )

        result = graph.invoke(
            {
                "query": query,
                "organization_id": 1,
            }
        )

        print("\n" + "=" * 70)
        print("P9.4 LANGGRAPH + GEMINI TEST")
        print("=" * 70)

        print("\nQuestion:")
        print(result["query"])

        print("\nAnswer:")
        print(result.get("answer"))

        print("\nReferences:")

        for index, reference in enumerate(
            result.get("references", []),
            start=1,
        ):
            print(f"\n[{index}]")

            if reference["source_type"] == "vector":
                print(f"Type: Vector")
                print(f"Title: {reference.get('title')}")
                print(f"File: {reference.get('file_path')}")
                print(f"Chunk: {reference.get('chunk_index')}")
                print(f"Score: {reference.get('score')}")

            else:
                print("Type: Graph")
                print(f"Evidence: {reference.get('content')}")
                print(f"Score: {reference.get('score')}")

        print("\nEntities:")
        print(result.get("entities"))

        print("\nContext sources:")

        for item in result.get("fused_context", []):
            reference = item.get("reference", {})

            if item["source_type"] == "vector":
                name = reference.get("title", "Unknown document")

            else:
                name = item.get("content", "Graph evidence")

            print(
                f"- [{item['source_type']}] {name}"
            )

        if result.get("error"):
            print("\nError:")
            print(result["error"])

    finally:
        db.close()


if __name__ == "__main__":
    main()