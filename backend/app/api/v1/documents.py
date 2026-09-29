from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.auth.roles import (
    require_admin,
    require_employee,
)
from app.database.postgres import get_db
from app.models.user import User
from app.schemas.document import (
    DocumentChunkResponse,
    DocumentListResponse,
    DocumentResponse,
)
from app.services.document_processing_service import (
    DocumentProcessingService,
)
from app.services.document_service import DocumentService
from app.services.authorization_scope_service import (
    AuthorizationScopeService,
)


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


@router.get(
    "",
    response_model=list[DocumentListResponse],
)
def get_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_employee),
):
    scope = AuthorizationScopeService.get_scope(
        db=db,
        current_user=current_user,
    )

    return DocumentService.get_accessible_documents(
        db=db,
        organization_id=scope.organization_id,
        project_ids=scope.project_ids,
    )


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_employee),
):
    scope = AuthorizationScopeService.get_scope(
        db=db,
        current_user=current_user,
    )

    document = DocumentService.get_accessible_document(
        db=db,
        document_id=document_id,
        organization_id=scope.organization_id,
        project_ids=scope.project_ids,
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    return document


@router.post(
    "/{document_id}/process",
    response_model=DocumentResponse,
)
def process_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    document = DocumentService.get_document(
        db,
        document_id,
        current_user.organization_id,
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    DocumentProcessingService.process_document(
        db,
        document,
    )

    db.refresh(document)

    return document


@router.get(
    "/{document_id}/chunks",
    response_model=list[DocumentChunkResponse],
)
def get_document_chunks(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_employee),
):
    scope = AuthorizationScopeService.get_scope(
        db=db,
        current_user=current_user,
    )

    document = DocumentService.get_accessible_document(
        db=db,
        document_id=document_id,
        organization_id=scope.organization_id,
        project_ids=scope.project_ids,
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    return DocumentProcessingService.get_chunks(
        db,
        document.id,
    )