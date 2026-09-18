from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.v1.auth.dependencies import get_current_user
from app.database.postgres import get_db
from app.models.user import User
from app.schemas.ai import AIChatRequest, AIChatResponse
from app.services.agent_service import AgentService
from app.services.conversation_service import ConversationService
from app.models.conversation import Conversation


router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


@router.post("/chat", response_model=AIChatResponse)
def chat(
    request: AIChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    organization_id = current_user.organization_id

    # -------------------------------------------------
    # Get or create conversation
    # -------------------------------------------------

    if request.conversation_id is None:

        conversation = ConversationService.create_conversation(
            db=db,
            organization_id=organization_id,
            user_id=current_user.id,
            title=request.message[:80],
        )

    else:

        conversation = ConversationService.get_conversation(
            db=db,
            conversation_id=request.conversation_id,
        )

        if conversation is None:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found.",
            )

        if (
            conversation.user_id != current_user.id
            or conversation.organization_id != organization_id
        ):
            raise HTTPException(
                status_code=403,
                detail="You cannot access this conversation.",
            )

    # -------------------------------------------------
    # Load previous messages
    # -------------------------------------------------

    previous_messages = ConversationService.get_messages(
        db=db,
        conversation_id=conversation.id,
    )

    conversation_history = [
        {
            "role": message.role,
            "content": message.content,
        }
        for message in previous_messages
    ]

    # -------------------------------------------------
    # Save user message
    # -------------------------------------------------

    ConversationService.add_message(
        db=db,
        conversation_id=conversation.id,
        role="user",
        content=request.message,
    )

    # -------------------------------------------------
    # Run AI agent
    # -------------------------------------------------

    result = AgentService.run(
        db=db,
        query=request.message,
        organization_id=organization_id,
        conversation_history=conversation_history,
    )

    if result.get("error"):
        raise HTTPException(
            status_code=500,
            detail=result["error"],
        )

    answer = result.get("answer", "")

    # -------------------------------------------------
    # Save assistant response
    # -------------------------------------------------

    ConversationService.add_message(
        db=db,
        conversation_id=conversation.id,
        role="assistant",
        content=answer,
    )

    return AIChatResponse(
        conversation_id=conversation.id,
        query=request.message,
        answer=answer,
        references=result.get("references", []),
        entities=result.get("entities", []),
    )

@router.get("/conversations/{conversation_id}/messages")
def get_conversation_messages(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation = ConversationService.get_conversation(
        db=db,
        conversation_id=conversation_id,
    )

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found.",
        )

    if (
        conversation.user_id != current_user.id
        or conversation.organization_id != current_user.organization_id
    ):
        raise HTTPException(
            status_code=403,
            detail="You cannot access this conversation.",
        )

    messages = ConversationService.get_messages(
        db=db,
        conversation_id=conversation_id,
    )

    return [
        {
            "id": message.id,
            "conversation_id": message.conversation_id,
            "role": message.role,
            "content": message.content,
            "created_at": message.created_at,
        }
        for message in messages
    ]

@router.get("/conversations")
def get_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversations = ConversationService.get_user_conversations(
        db=db,
        organization_id=current_user.organization_id,
        user_id=current_user.id,
    )

    return [
        {
            "id": conversation.id,
            "title": conversation.title,
            "created_at": conversation.created_at,
        }
        for conversation in conversations
    ]