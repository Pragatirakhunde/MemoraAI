from __future__ import annotations

from datetime import datetime
import hashlib
from pathlib import Path
import subprocess

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.codemind.chunking.chunker import CodeChunker
from app.codemind.graph.service import CodeGraphService
from app.codemind.ingestion.scanner import CodeRepositoryScanner
from app.codemind.parsing.parser import CodeParser
from app.codemind.retrieval.vector_store import CodeVectorStore
from app.models.code_chunk import CodeChunk
from app.models.code_commit import CodeCommit
from app.models.code_file import CodeFile
from app.models.code_repository import CodeRepository
from app.models.code_symbol import CodeSymbol
from app.models.project import Project
from app.core.config import settings


class CodeMindIndexingService:
    def __init__(self, db: Session):
        self.db = db
        self.parser = CodeParser()
        self.chunker = CodeChunker()
        self.vector_store = CodeVectorStore()

    @staticmethod
    def _checksum(content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def index_repository(self, repository: CodeRepository) -> dict:
        if repository.status != "active":
            raise ValueError("Archived code repositories cannot be indexed.")
        if not repository.local_path:
            raise ValueError("Repository has no local_path.")

        root = Path(repository.local_path).expanduser().resolve()
        scanner = CodeRepositoryScanner(root, settings.CODEMIND_MAX_FILE_SIZE_MB * 1024 * 1024)
        if not scanner.validate():
            raise ValueError(f"Repository path does not exist: {root}")

        repository.index_status = "running"
        repository.last_index_error = None
        self.db.commit()

        try:
            scanned = scanner.scan()
            seen = {item.relative_path for item in scanned}
            changed = skipped = deleted_count = symbols_count = chunks_count = 0

            project = self.db.get(Project, repository.project_id)
            if project is None or project.organization_id != repository.organization_id:
                raise ValueError("Project not found for repository.")

            CodeGraphService.index_repository(
                repository.id,
                repository.organization_id,
                repository.project_id,
                repository.name,
                project.name,
            )

            for item in scanned:
                content = item.absolute_path.read_text(encoding="utf-8", errors="replace")
                checksum = self._checksum(content)
                existing = self.db.scalar(select(CodeFile).where(
                    CodeFile.repository_id == repository.id,
                    CodeFile.file_path == item.relative_path,
                ))

                if existing and existing.status == "active" and existing.checksum == checksum:
                    skipped += 1
                    continue

                if existing:
                    old_chunks = self.db.scalars(select(CodeChunk).where(CodeChunk.file_id == existing.id)).all()
                    self.vector_store.delete_ids([row.id for row in old_chunks])
                    self.db.execute(delete(CodeChunk).where(CodeChunk.file_id == existing.id))
                    self.db.execute(delete(CodeSymbol).where(CodeSymbol.file_id == existing.id))
                    self.db.commit()
                    CodeGraphService.clear_file(existing.id)
                    code_file = existing
                    code_file.status = "active"
                else:
                    code_file = CodeFile(
                        organization_id=repository.organization_id,
                        project_id=repository.project_id,
                        repository_id=repository.id,
                        file_path=item.relative_path,
                        file_name=item.name,
                        extension=item.extension,
                        language=self.parser.language_for_extension(item.extension),
                        size_bytes=item.size_bytes,
                        checksum=checksum,
                        status="active",
                    )
                    self.db.add(code_file)
                    self.db.flush()

                parsed = self.parser.parse(content, item.extension)
                code_file.analysis_json = {
                    "imports": parsed.imports,
                    "symbols": [s.qualified_name for s in parsed.symbols],
                    "calls": {s.qualified_name: s.call_names for s in parsed.symbols},
                }
                code_file.language = parsed.language if parsed.language != "unknown" else code_file.language
                code_file.size_bytes = item.size_bytes
                code_file.checksum = checksum
                code_file.last_indexed_at = datetime.utcnow()
                self.db.flush()

                symbol_by_qualified = {}
                created_symbols = []
                for parsed_symbol in parsed.symbols:
                    parent_id = None
                    if parsed_symbol.parent_name:
                        parent = symbol_by_qualified.get(parsed_symbol.parent_name)
                        if parent:
                            parent_id = parent.id
                    row = CodeSymbol(
                        organization_id=repository.organization_id,
                        project_id=repository.project_id,
                        repository_id=repository.id,
                        file_id=code_file.id,
                        parent_symbol_id=parent_id,
                        symbol_type=("api" if parsed_symbol.metadata.get("api_method") else parsed_symbol.symbol_type),
                        name=parsed_symbol.name,
                        qualified_name=parsed_symbol.qualified_name,
                        signature=parsed_symbol.signature,
                        docstring=parsed_symbol.docstring,
                        start_line=parsed_symbol.start_line,
                        end_line=parsed_symbol.end_line,
                        metadata_json=parsed_symbol.metadata,
                    )
                    self.db.add(row)
                    self.db.flush()
                    symbol_by_qualified[row.qualified_name] = row
                    created_symbols.append((row, parsed_symbol))

                vector_rows = []
                for draft in self.chunker.build(item.relative_path, content, parsed):
                    symbol_id = None
                    if draft.symbol and draft.symbol.qualified_name in symbol_by_qualified:
                        symbol_id = symbol_by_qualified[draft.symbol.qualified_name].id
                    chunk = CodeChunk(
                        organization_id=repository.organization_id,
                        project_id=repository.project_id,
                        repository_id=repository.id,
                        file_id=code_file.id,
                        symbol_id=symbol_id,
                        chunk_index=draft.index,
                        content=draft.content,
                        start_line=draft.start_line,
                        end_line=draft.end_line,
                        checksum=draft.checksum,
                        status="active",
                    )
                    self.db.add(chunk)
                    self.db.flush()
                    vector_rows.append((
                        chunk.id,
                        draft.content,
                        {
                            "kind": "code",
                            "organization_id": repository.organization_id,
                            "project_id": repository.project_id,
                            "repository_id": repository.id,
                            "file_id": code_file.id,
                            "symbol_id": symbol_id,
                            "file_path": item.relative_path,
                            "language": code_file.language,
                            "symbol_type": draft.symbol.symbol_type if draft.symbol else "file",
                            "symbol_name": draft.symbol.qualified_name if draft.symbol else item.name,
                            "start_line": draft.start_line,
                            "end_line": draft.end_line,
                            "content": draft.content,
                        },
                    ))

                self.db.commit()
                self.vector_store.upsert_many(vector_rows)
                CodeGraphService.index_file(
                    repository.id,
                    repository.organization_id,
                    repository.project_id,
                    code_file.id,
                    item.relative_path,
                    code_file.language,
                    [
                        {
                            "id": row.id,
                            "name": row.name,
                            "qualified_name": row.qualified_name,
                            "symbol_type": row.symbol_type,
                            "start_line": row.start_line,
                            "end_line": row.end_line,
                            "call_targets": parsed_symbol.call_names,
                        }
                        for row, parsed_symbol in created_symbols
                    ],
                )
                CodeGraphService.index_imports(code_file.id, repository.organization_id, repository.project_id, parsed.imports)
                changed += 1
                symbols_count += len(created_symbols)
                chunks_count += len(vector_rows)

            active_files = self.db.scalars(select(CodeFile).where(
                CodeFile.repository_id == repository.id,
                CodeFile.status == "active",
            )).all()
            for row in active_files:
                if row.file_path not in seen:
                    old_chunks = self.db.scalars(select(CodeChunk).where(CodeChunk.file_id == row.id)).all()
                    self.vector_store.delete_ids([chunk.id for chunk in old_chunks])
                    self.db.execute(delete(CodeChunk).where(CodeChunk.file_id == row.id))
                    self.db.execute(delete(CodeSymbol).where(CodeSymbol.file_id == row.id))
                    row.status = "deleted"
                    CodeGraphService.clear_file(row.id)
                    deleted_count += 1
            self.db.commit()

            history_stats = self._index_git_history(
                repository, limit=settings.CODEMIND_GIT_HISTORY_LIMIT
            )
            CodeGraphService.rebuild_calls(repository.id, repository.organization_id, repository.project_id)

            repository.index_status = "completed"
            repository.last_indexed_at = datetime.utcnow()
            repository.last_index_error = None
            self.db.commit()
            return {
                "repository_id": repository.id,
                "files_found": len(scanned),
                "files_changed": changed,
                "files_skipped": skipped,
                "files_deleted": deleted_count,
                "symbols": symbols_count,
                "chunks": chunks_count,
                **history_stats,
            }
        except Exception as exc:
            self.db.rollback()
            repository.index_status = "failed"
            repository.last_index_error = str(exc)[:4000]
            self.db.commit()
            raise

    def _index_git_history(self, repository: CodeRepository, limit: int = 100) -> dict[str, int]:
        """Persist the most recent commits and their changed-file statistics.

        Git history is metadata only: refreshing it does not train or fine-tune
        the embedding model. File embeddings are upserted only for changed files
        in ``index_repository`` above.
        """
        root = Path(repository.local_path).expanduser().resolve()
        if not (root / ".git").exists():
            return {"commits_scanned": 0, "commits_added": 0, "commits_updated": 0}

        safe_limit = max(1, min(int(limit), 5000))
        try:
            output = subprocess.run(
                ["git", "-C", str(root), "log", f"-n{safe_limit}", "--date=iso-strict",
                 "--format=%H%x1f%an%x1f%ae%x1f%aI%x1f%s"],
                check=True, capture_output=True, text=True,
            ).stdout
        except (OSError, subprocess.CalledProcessError) as exc:
            raise ValueError(f"Unable to read Git commit history: {exc}") from exc

        added = updated = scanned = 0
        for line in output.splitlines():
            parts = line.split("\x1f", 4)
            if len(parts) != 5:
                continue
            sha, author, email, committed_at, message = parts
            scanned += 1

            try:
                status_output = subprocess.run(
                    ["git", "-C", str(root), "diff-tree", "--root", "--no-commit-id",
                     "--name-status", "-r", "--no-renames", sha],
                    check=True, capture_output=True, text=True,
                ).stdout
                numstat_output = subprocess.run(
                    ["git", "-C", str(root), "show", "--format=", "--numstat", "--no-renames", sha],
                    check=True, capture_output=True, text=True,
                ).stdout
            except (OSError, subprocess.CalledProcessError) as exc:
                raise ValueError(f"Unable to read changed files for commit {sha[:10]}: {exc}") from exc

            changes_by_path: dict[str, dict] = {}
            for row in status_output.splitlines():
                fields = row.split("\t", 1)
                if len(fields) == 2:
                    changes_by_path[fields[1]] = {
                        "status": fields[0], "path": fields[1],
                        "additions": 0, "deletions": 0,
                    }

            additions_total = deletions_total = 0
            for row in numstat_output.splitlines():
                fields = row.split("\t", 2)
                if len(fields) != 3:
                    continue
                add_text, delete_text, path = fields
                # Binary files use '-' instead of numeric line counts.
                try:
                    additions = int(add_text)
                    deletions = int(delete_text)
                except ValueError:
                    additions = deletions = 0
                additions_total += additions
                deletions_total += deletions
                if path in changes_by_path:
                    changes_by_path[path]["additions"] = additions
                    changes_by_path[path]["deletions"] = deletions
                else:
                    changes_by_path[path] = {
                        "status": "M", "path": path,
                        "additions": additions, "deletions": deletions,
                    }

            changed_files = list(changes_by_path.values())
            committed_at_value = datetime.fromisoformat(
                committed_at.replace("Z", "+00:00")
            ).replace(tzinfo=None)

            existing = self.db.scalar(select(CodeCommit).where(
                CodeCommit.repository_id == repository.id,
                CodeCommit.sha == sha,
            ))
            if existing is None:
                existing = CodeCommit(
                    organization_id=repository.organization_id,
                    project_id=repository.project_id,
                    repository_id=repository.id,
                    sha=sha,
                    author_name=author,
                    author_email=email,
                    committed_at=committed_at_value,
                    message=message,
                    changed_files=changed_files,
                    additions=additions_total,
                    deletions=deletions_total,
                )
                self.db.add(existing)
                added += 1
            else:
                # Backfill stats for commits previously indexed by an older build,
                # but avoid reporting every unchanged commit as updated on each sync.
                changed_record = any((
                    existing.author_name != author,
                    existing.author_email != email,
                    existing.committed_at != committed_at_value,
                    existing.message != message,
                    existing.changed_files != changed_files,
                    existing.additions != additions_total,
                    existing.deletions != deletions_total,
                ))
                if changed_record:
                    existing.author_name = author
                    existing.author_email = email
                    existing.committed_at = committed_at_value
                    existing.message = message
                    existing.changed_files = changed_files
                    existing.additions = additions_total
                    existing.deletions = deletions_total
                    updated += 1

        self.db.commit()
        return {"commits_scanned": scanned, "commits_added": added, "commits_updated": updated}
