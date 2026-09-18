from app.database.postgres import SessionLocal
from app.services.agent_service import AgentService
from app.services.conversation_service import ConversationService


ORGANIZATION_ID = 1
USER_ID = 1


def print_separator():
    print("\n" + "=" * 80)


def test_basic_question(db):
    print_separator()
    print("TEST 1 - BASIC ORGANIZATIONAL QUESTION")

    query = "What technologies are used by Inventory Management?"

    result = AgentService.run(
        db=db,
        query=query,
        organization_id=ORGANIZATION_ID,
    )

    print("\nQuestion:")
    print(query)

    print("\nAnswer:")
    print(result.get("answer"))

    print("\nEntities:")
    print(result.get("entities"))

    print("\nReferences:")
    for reference in result.get("references", []):
        print(reference)

    assert result.get("answer")
    assert result.get("references")

    print("\nPASS")


def test_graph_vector_question(db):
    print_separator()
    print("TEST 2 - HYBRID GRAPH + VECTOR QUESTION")

    query = "What database does Inventory Management use?"

    result = AgentService.run(
        db=db,
        query=query,
        organization_id=ORGANIZATION_ID,
    )

    print("\nQuestion:")
    print(query)

    print("\nAnswer:")
    print(result.get("answer"))

    print("\nEntities:")
    print(result.get("entities"))

    print("\nReferences:")
    for reference in result.get("references", []):
        print(reference)

    assert result.get("answer")

    print("\nPASS")


def test_insufficient_knowledge(db):
    print_separator()
    print("TEST 3 - INSUFFICIENT KNOWLEDGE")

    query = (
        "What quantum computing hardware is used by "
        "TechNova Solutions for the Mars Colony project?"
    )

    result = AgentService.run(
        db=db,
        query=query,
        organization_id=ORGANIZATION_ID,
    )

    answer = result.get("answer", "")

    print("\nQuestion:")
    print(query)

    print("\nAnswer:")
    print(answer)

    assert answer

    print("\nPASS")
    print(
        "Note: Manually verify that the answer states that "
        "the organizational knowledge is insufficient."
    )


def test_conversation_memory(db):
    print_separator()
    print("TEST 4 - CONVERSATION MEMORY")

    conversation = ConversationService.create_conversation(
        db=db,
        organization_id=ORGANIZATION_ID,
        user_id=USER_ID,
        title="Phase 9 Validation",
    )

    first_question = (
        "What technologies are used by Inventory Management?"
    )

    first_result = AgentService.run(
        db=db,
        query=first_question,
        organization_id=ORGANIZATION_ID,
        conversation_history=[],
    )

    first_answer = first_result.get("answer", "")

    ConversationService.add_message(
        db=db,
        conversation_id=conversation.id,
        role="user",
        content=first_question,
    )

    ConversationService.add_message(
        db=db,
        conversation_id=conversation.id,
        role="assistant",
        content=first_answer,
    )

    second_question = "What database does it use?"

    history = ConversationService.get_messages(
        db=db,
        conversation_id=conversation.id,
    )

    conversation_history = [
        {
            "role": message.role,
            "content": message.content,
        }
        for message in history
    ]

    second_result = AgentService.run(
        db=db,
        query=second_question,
        organization_id=ORGANIZATION_ID,
        conversation_history=conversation_history,
    )

    second_answer = second_result.get("answer", "")

    ConversationService.add_message(
        db=db,
        conversation_id=conversation.id,
        role="user",
        content=second_question,
    )

    ConversationService.add_message(
        db=db,
        conversation_id=conversation.id,
        role="assistant",
        content=second_answer,
    )

    print("\nConversation ID:")
    print(conversation.id)

    print("\nFirst question:")
    print(first_question)

    print("\nFirst answer:")
    print(first_answer)

    print("\nSecond question:")
    print(second_question)

    print("\nSecond answer:")
    print(second_answer)

    assert first_answer
    assert second_answer

    print("\nPASS")


def test_reference_structure(db):
    print_separator()
    print("TEST 5 - REFERENCE STRUCTURE")

    query = "What technologies are used by Inventory Management?"

    result = AgentService.run(
        db=db,
        query=query,
        organization_id=ORGANIZATION_ID,
    )

    references = result.get("references", [])

    print("\nReference count:")
    print(len(references))

    for index, reference in enumerate(references, start=1):
        print(f"\nReference {index}:")
        print(reference)

        assert "source_type" in reference
        assert "score" in reference

        if reference["source_type"] == "vector":
            assert "document_id" in reference
            assert "chunk_id" in reference

        elif reference["source_type"] == "graph":
            assert "content" in reference

    print("\nPASS")


def main():
    print("\n" + "#" * 80)
    print("# PHASE 9 VALIDATION")
    print("#" * 80)

    db = SessionLocal()

    try:
        test_basic_question(db)
        test_graph_vector_question(db)
        test_insufficient_knowledge(db)
        test_conversation_memory(db)
        test_reference_structure(db)

        print_separator()
        print("PHASE 9 VALIDATION COMPLETE")
        print("ALL AUTOMATED TESTS PASSED")

    except Exception as exc:
        print_separator()
        print("PHASE 9 VALIDATION FAILED")
        print(f"Error: {exc}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()