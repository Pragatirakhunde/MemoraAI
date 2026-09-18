from app.ai_engine.prompt_builder import PromptBuilder


def main():
    print("PROMPT BUILDER TEST")

    context = [
        {
            "source_type": "vector",
            "score": 0.82,
            "content": (
                "Inventory Management uses React for the frontend "
                "and FastAPI for the backend."
            ),
            "reference": {
                "title": "Inventory Architecture",
                "file_path": "architecture/inventory.md",
            },
        },
        {
            "source_type": "graph",
            "score": 0.76,
            "content": (
                "Inventory Management USES Technology React."
            ),
            "reference": {
                "title": "Knowledge Graph",
                "file_path": "neo4j",
            },
        },
    ]

    prompt = PromptBuilder.build_grounded_prompt(
        query="What technologies are used by Inventory Management?",
        fused_context=context,
        entities=[
            {"name": "Inventory Management", "type": "Project"},
            {"name": "React", "type": "Technology"},
        ],
    )

    print("\n" + "=" * 70)
    print(prompt)
    print("=" * 70)


if __name__ == "__main__":
    main()