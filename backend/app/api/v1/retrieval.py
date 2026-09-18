from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.auth.roles import require_employee
from app.database.postgres import get_db
from app.models.user import User
from app.schemas.retrieval import (
    RetrievalEntity,
    RetrievalEvidence,
    RetrievalReference,
    RetrievalResponse,
)
from app.schemas.search import SearchRequest
from app.services.hybrid_retrieval_service import (
    HybridRetrievalService,
)


router = APIRouter(
    prefix="/retrieval",
    tags=["Hybrid Retrieval"],
)


@router.post(
    "",
    response_model=RetrievalResponse,
)
def hybrid_retrieval(
    data: SearchRequest,
    current_user: User = Depends(
        require_employee
    ),
    db: Session = Depends(get_db),
):

    service = HybridRetrievalService()

    raw_retrieval = service.retrieve(
        db=db,
        query=data.query,
        organization_id=(
            current_user.organization_id
        ),
        limit=data.limit,
    )

    fused_context = service.retrieve_fused_context(
        db=db,
        query=data.query,
        organization_id=(
            current_user.organization_id
        ),
        limit=data.limit,
        max_context_items=10,
    )

    evidence = []

    for item in fused_context:

        reference = RetrievalReference(
            **item.reference
        )

        evidence.append(
            RetrievalEvidence(
                source_type=item.source_type,
                score=item.score,
                content=item.content,
                reference=reference,
            )
        )

    entities = [
        RetrievalEntity(
            name=entity["name"],
            type=entity["type"],
            confidence=entity["confidence"],
        )
        for entity in raw_retrieval.entities
    ]

    vector_count = len(
        raw_retrieval.vector_results
    )

    graph_count = len(
        raw_retrieval.graph_results
    )

    return RetrievalResponse(
        query=data.query,
        entities=entities,
        evidence=evidence,
        vector_result_count=vector_count,
        graph_result_count=graph_count,
    )