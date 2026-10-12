from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api.v1.auth.authorization import require_project_access
from app.api.v1.auth.roles import require_admin, require_employee
from app.connectors.git.github_webhook import (
    payload_matches_repository,
    verify_github_signature,
)
from app.core.config import settings
from app.database.postgres import get_db
from app.models.project import Project
from app.models.user import User
from app.codemind.schemas.models import (
    BusinessRuleRequest, CodeAskRequest, CodeRepositoryCreate,
    CodeRepositoryResponse, CodeSearchRequest,
)
from app.codemind.repositories import CodeMindRepositoryRepository
from app.codemind.services.analysis_service import CodeMindAnalysisService
from app.codemind.services.indexing_service import CodeMindIndexingService
from app.codemind.services.query_service import CodeMindQueryService
from app.codemind.services.repository_service import CodeRepositoryService
from app.services.authorization_scope_service import AuthorizationScopeService

router = APIRouter(prefix="/codemind", tags=["CodeMind"])


@router.post("/repositories", response_model=CodeRepositoryResponse, status_code=status.HTTP_201_CREATED)
def create_repository(data: CodeRepositoryCreate, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    try:
        return CodeRepositoryService.create(db, current_user.organization_id, data)
    except ValueError as exc:
        raise HTTPException(400, str(exc))


@router.get("/repositories", response_model=list[CodeRepositoryResponse])
def list_repositories(db: Session = Depends(get_db), current_user: User = Depends(require_employee)):
    scope = AuthorizationScopeService.get_scope(db=db, current_user=current_user)
    return CodeMindRepositoryRepository.authorized(db, current_user.organization_id, scope.project_ids)


@router.get("/repositories/{repository_id}", response_model=CodeRepositoryResponse)
def get_repository(repository_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_employee)):
    repo = CodeMindRepositoryRepository.by_id_org(db, repository_id, current_user.organization_id)
    if repo is None:
        raise HTTPException(404, "Repository not found")
    if current_user.role != "admin":
        require_project_access(repo.project_id, db, current_user)
    return repo


@router.post("/repositories/{repository_id}/validate")
def validate_repository(repository_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    repo = CodeMindRepositoryRepository.by_id_org(db, repository_id, current_user.organization_id)
    if repo is None:
        raise HTTPException(404, "Repository not found")
    try:
        valid = CodeRepositoryService.validate_repository(repo)
        return {"repository_id": repo.id, "valid": valid, "path": repo.local_path}
    except Exception as exc:
        return {"repository_id": repo.id, "valid": False, "error": str(exc)}


@router.post("/repositories/{repository_id}/index")
def index_repository(repository_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    repo = CodeMindRepositoryRepository.by_id_org(db, repository_id, current_user.organization_id)
    if repo is None:
        raise HTTPException(404, "Repository not found")
    try:
        CodeRepositoryService.sync_provider(repo)
        result = CodeMindIndexingService(db).index_repository(repo)
        return {"status": "completed", **result}
    except ValueError as exc:
        repo.index_status = "failed"
        repo.last_index_error = str(exc)[:4000]
        db.commit()
        raise HTTPException(400, str(exc))
    except Exception as exc:
        repo.index_status = "failed"
        repo.last_index_error = str(exc)[:4000]
        db.commit()
        raise HTTPException(500, f"CodeMind indexing failed: {exc}")


@router.get("/projects/{project_id}/repositories", response_model=list[CodeRepositoryResponse])
def project_repositories(project_id: int, project: Project = Depends(require_project_access), db: Session = Depends(get_db), current_user: User = Depends(require_employee)):
    return CodeMindRepositoryRepository.by_project(db, project.id, current_user.organization_id)


@router.get("/projects/{project_id}/files")
def files(project_id: int, project: Project = Depends(require_project_access), db: Session = Depends(get_db), current_user: User = Depends(require_employee)):
    return CodeMindAnalysisService.files(db, current_user.organization_id, project.id)


@router.get("/projects/{project_id}/symbols")
def symbols(project_id: int, project: Project = Depends(require_project_access), db: Session = Depends(get_db), current_user: User = Depends(require_employee)):
    return CodeMindAnalysisService.symbols(db, current_user.organization_id, project.id)


@router.get("/projects/{project_id}/history")
def history(project_id: int, project: Project = Depends(require_project_access), db: Session = Depends(get_db), current_user: User = Depends(require_employee)):
    return CodeMindAnalysisService.history(db, current_user.organization_id, project.id)


@router.get("/projects/{project_id}/architecture")
def architecture(project_id: int, project: Project = Depends(require_project_access), current_user: User = Depends(require_employee)):
    return CodeMindQueryService.architecture(current_user.organization_id, project.id)


@router.post("/projects/{project_id}/search")
def search(project_id: int, data: CodeSearchRequest, project: Project = Depends(require_project_access), current_user: User = Depends(require_employee)):
    return CodeMindQueryService().search(data.query, current_user.organization_id, project.id, data.limit)


@router.post("/projects/{project_id}/similar")
def similar(project_id: int, data: CodeSearchRequest, project: Project = Depends(require_project_access), current_user: User = Depends(require_employee)):
    return CodeMindQueryService().similar(data.query, current_user.organization_id, project.id, data.limit)


@router.post("/projects/{project_id}/ask")
def ask(project_id: int, data: CodeAskRequest, project: Project = Depends(require_project_access), current_user: User = Depends(require_employee)):
    try:
        return {"project_id": project.id, "query": data.query, **CodeMindQueryService().ask(data.query, current_user.organization_id, project.id, data.limit)}
    except Exception as exc:
        raise HTTPException(500, f"CodeMind query failed: {exc}")


@router.get("/projects/{project_id}/dependencies/{symbol_id}")
def dependencies(project_id: int, symbol_id: int, project: Project = Depends(require_project_access), current_user: User = Depends(require_employee)):
    return CodeMindQueryService.dependencies(current_user.organization_id, project.id, symbol_id)


@router.get("/projects/{project_id}/impact/{symbol_id}")
def impact(project_id: int, symbol_id: int, project: Project = Depends(require_project_access), current_user: User = Depends(require_employee)):
    return CodeMindQueryService.impact(current_user.organization_id, project.id, symbol_id)


@router.post("/projects/{project_id}/business-rule")
def business_rule(project_id: int, data: BusinessRuleRequest, project: Project = Depends(require_project_access), db: Session = Depends(get_db), current_user: User = Depends(require_employee)):
    return CodeMindQueryService.business_rule(db, data.rule, current_user.organization_id, project.id, data.limit)


@router.post("/webhook/github/{repository_id}")
async def github_webhook(repository_id: int, request: Request, db: Session = Depends(get_db)):
    """Validate a GitHub push delivery and enqueue an incremental CodeMind refresh.

    The endpoint is intentionally unauthenticated via user JWT because GitHub calls
    it directly; authenticity is instead established by the per-hook HMAC secret.
    The configured repository URL and branch are also checked before enqueueing.
    """
    secret = settings.GITHUB_WEBHOOK_SECRET
    if not secret:
        raise HTTPException(503, "GitHub webhook secret is not configured")

    body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256", "")
    if not verify_github_signature(body, signature, secret):
        raise HTTPException(401, "Invalid webhook signature")

    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(400, "Webhook body must be valid JSON")
    if not isinstance(payload, dict):
        raise HTTPException(400, "Webhook JSON root must be an object")

    from app.models.code_repository import CodeRepository
    repo = db.get(CodeRepository, repository_id)
    if repo is None or repo.status != "active" or repo.provider != "github":
        raise HTTPException(404, "Active GitHub repository not found")

    payload_repository = payload.get("repository") or {}
    if not isinstance(payload_repository, dict) or not payload_matches_repository(repo.remote_url, payload_repository):
        raise HTTPException(403, "Webhook repository does not match the configured repository")

    event = request.headers.get("X-GitHub-Event", "")
    if event == "ping":
        return {"status": "received", "repository_id": repo.id, "message": "Webhook secret and repository verified."}
    if event != "push":
        return {"status": "ignored", "repository_id": repo.id, "reason": "unsupported_event"}

    expected_ref = f"refs/heads/{repo.default_branch}"
    if payload.get("ref") != expected_ref:
        return {
            "status": "ignored",
            "repository_id": repo.id,
            "reason": "branch_not_configured",
            "expected_ref": expected_ref,
            "received_ref": payload.get("ref"),
        }
    if payload.get("deleted") or not payload.get("after") or set(payload.get("after", "")) == {"0"}:
        return {"status": "ignored", "repository_id": repo.id, "reason": "branch_deleted_or_empty"}

    # Persist pending state before dispatch so the worker can't race with a later
    # status commit from this request.
    repo.index_status = "pending"
    repo.last_index_error = None
    db.commit()

    from app.workers.tasks import codemind_index_repository_task
    try:
        task = codemind_index_repository_task.delay(repository_id)
    except Exception as exc:
        repo.index_status = "failed"
        repo.last_index_error = f"Unable to enqueue GitHub update: {str(exc)[:3500]}"
        db.commit()
        raise HTTPException(503, "Unable to queue repository indexing; check the Celery worker/broker.")

    return {
        "status": "queued",
        "task_id": task.id,
        "repository_id": repo.id,
        "commit": payload.get("after"),
        "message": "Repository refresh queued. Changed files are re-indexed; the embedding model is not retrained.",
    }
