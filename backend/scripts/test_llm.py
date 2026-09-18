from app.services.llm_service import LLMService


def main():
    print("LLM TEST")

    service = LLMService()

    response = service.generate(
        "Explain what an organizational knowledge graph is in 3 simple sentences."
    )

    print("\nResponse:")
    print(response)


if __name__ == "__main__":
    main()