from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class ScannedCodeFile:
    relative_path: str
    absolute_path: Path
    name: str
    extension: str
    size_bytes: int


class CodeRepositoryScanner:
    SUPPORTED_EXTENSIONS = {
        ".py", ".js", ".jsx", ".ts", ".tsx",
        ".java", ".cpp", ".c", ".h", ".hpp",
        ".go", ".rs", ".cs", ".json", ".yaml", ".yml",
    }

    IGNORED_DIRECTORIES = {
        ".git", ".hg", ".svn", "node_modules", "__pycache__",
        ".venv", "venv", "env", "dist", "build", "coverage",
        ".pytest_cache", ".mypy_cache", ".idea", ".vscode", "target",
    }

    def __init__(self, root: str | Path, max_size_bytes: int):
        self.root = Path(root).expanduser().resolve()
        self.max_size_bytes = max_size_bytes

    def validate(self) -> bool:
        return self.root.exists() and self.root.is_dir()

    def scan(self) -> list[ScannedCodeFile]:
        if not self.validate():
            raise ValueError(f"Repository path does not exist: {self.root}")
        result: list[ScannedCodeFile] = []
        for path in self.root.rglob("*"):
            if not path.is_file():
                continue
            rel = path.relative_to(self.root)
            if any(part in self.IGNORED_DIRECTORIES for part in rel.parts):
                continue
            if path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
                continue
            size = path.stat().st_size
            if size > self.max_size_bytes:
                continue
            result.append(ScannedCodeFile(
                relative_path=rel.as_posix(),
                absolute_path=path,
                name=path.name,
                extension=path.suffix.lower(),
                size_bytes=size,
            ))
        return sorted(result, key=lambda item: item.relative_path.lower())
