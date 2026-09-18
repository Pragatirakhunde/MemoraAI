from sqlalchemy.orm import Session

from app.models.conversation import Conversation, Message


class ConversationService:

    @staticmethod
    def create_conversation(
        db: Session,
        organization_id: int,
        user_id: int,
        title: str | None = None,
    ) -> Conversation:

        conversation = Conversation(
            organization_id=organization_id,
            user_id=user_id,
            title=title,
        )

        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        return conversation

    @staticmethod
    def add_message(
        db: Session,
        conversation_id: int,
        role: str,
        content: str,
    ) -> Message:

        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
        )

        db.add(message)
        db.commit()
        db.refresh(message)

        return message

    @staticmethod
    def get_messages(
        db: Session,
        conversation_id: int,
    ) -> list[Message]:

        return (
            db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .all()
        )

    @staticmethod
    def get_conversation(
        db: Session,
        conversation_id: int,
    ) -> Conversation | None:

        return (
            db.query(Conversation)
            .filter(Conversation.id == conversation_id)
            .first()
        )

    @staticmethod
    def get_user_conversations(
        db: Session,
        organization_id: int,
        user_id: int,
    ) -> list[Conversation]:

        return (
            db.query(Conversation)
            .filter(
                Conversation.organization_id == organization_id,
                Conversation.user_id == user_id,
            )
            .order_by(Conversation.created_at.desc())
            .all()
        )