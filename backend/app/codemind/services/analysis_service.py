from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.code_commit import CodeCommit
from app.models.code_file import CodeFile
from app.models.code_symbol import CodeSymbol


class CodeMindAnalysisService:
    @staticmethod
    def files(db: Session, organization_id: int, project_id: int):
        rows = db.scalars(select(CodeFile).where(
            CodeFile.organization_id == organization_id,
            CodeFile.project_id == project_id,
            CodeFile.status == "active",
        ).order_by(CodeFile.file_path)).all()
        return [{
            "id": r.id, "file_path": r.file_path, "language": r.language,
            "extension": r.extension, "size_bytes": r.size_bytes,
            "last_indexed_at": r.last_indexed_at,
        } for r in rows]

    @staticmethod
    def symbols(db: Session, organization_id: int, project_id: int, limit: int = 500):
        rows = db.scalars(select(CodeSymbol).where(
            CodeSymbol.organization_id == organization_id,
            CodeSymbol.project_id == project_id,
        ).order_by(CodeSymbol.qualified_name).limit(limit)).all()
        return [{
            "id": r.id, "file_id": r.file_id, "name": r.name,
            "qualified_name": r.qualified_name, "symbol_type": r.symbol_type,
            "start_line": r.start_line, "end_line": r.end_line,
            "metadata": r.metadata_json,
        } for r in rows]

    @staticmethod
    def history(db: Session, organization_id: int, project_id: int, limit: int = 50):
        rows = db.scalars(select(CodeCommit).where(
            CodeCommit.organization_id == organization_id,
            CodeCommit.project_id == project_id,
        ).order_by(CodeCommit.committed_at.desc().nullslast()).limit(limit)).all()
        return [{
            "sha": r.sha, "author_name": r.author_name, "author_email": r.author_email,
            "committed_at": r.committed_at, "message": r.message, "changed_files": r.changed_files,
        } for r in rows]

    @staticmethod
    def file_content(db: Session, organization_id: int, project_id: int, file_id: int):
        row = db.scalar(select(CodeFile).where(
            CodeFile.id == file_id,
            CodeFile.organization_id == organization_id,
            CodeFile.project_id == project_id,
            CodeFile.status == "active",
        ))
        if row is None:
            return None
        from pathlib import Path
        path = Path(row.file_path)
        return {"id": row.id, "file_path": row.file_path, "language": row.language,
                "size_bytes": row.size_bytes, "analysis": row.analysis_json}
