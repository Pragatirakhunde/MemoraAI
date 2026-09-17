from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.auth.roles import require_employee
from app.database.postgres import get_db
from app.models.user import User
from app.schemas.search import (
    SearchRequest,
    SearchResult,
)
from app.services.search_service import SearchService


router = APIRouter(
    prefix="/search",
    tags=["Semantic Search"],
)


@router.post(
    "",
    response_model=list[SearchResult],
)
def semantic_search(
    data: SearchRequest,
    current_user: User = Depends(
        require_employee
    ),
    db: Session = Depends(get_db),
):

    service = SearchService()

    return service.search(
        db=db,
        query=data.query,
        organization_id=(
            current_user.organization_id
        ),
        limit=data.limit,
        document_type=data.document_type,
        language=data.language,
        data_source_id=data.data_source_id,
        extension=data.extension,
    )