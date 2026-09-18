from app.database.postgres import SessionLocal
from app.services.conversation_service import ConversationService


def main():
    db = SessionLocal()

    try:
        conversation = ConversationService.create_conversation(
            db=db,
            organization_id=1,
            user_id=1,
            title="Inventory Management Discussion",
        )

        ConversationService.add_message(
            db=db,
            conversation_id=conversation.id,
            role="user",
            content="What technologies are used by Inventory Management?",
        )

        ConversationService.add_message(
            db=db,
            conversation_id=conversation.id,
            role="assistant",
            content="Inventory Management uses Docker, Redis, Python and FastAPI.",
        )

        messages = ConversationService.get_messages(
            db=db,
            conversation_id=conversation.id,
        )

        print("\nCONVERSATION MEMORY TEST")
        print("=" * 60)
        print(f"Conversation ID: {conversation.id}")

        for message in messages:
            print(f"\n{message.role.upper()}:")
            print(message.content)

    finally:
        db.close()


if __name__ == "__main__":
    main()