from __future__ import annotations

import base64
import os
import subprocess
from pathlib import Path
from urllib.parse import urlparse

from app.connectors.base import BaseConnector, ConnectorFile
from app.core.config import settings
from app.connectors.git.github_webhook import canonical_github_repository


class GitRepositoryConnector(BaseConnector):
    """Clone/update Git repositories while preserving bounded commit history."""

    SUPPORTED_EXTENSIONS = {
        ".md", ".txt", ".py", ".js", ".ts", ".tsx", ".jsx", ".java",
        ".cpp", ".c", ".h", ".json", ".yaml", ".yml",
    }
    IGNORED_DIRECTORIES = {
        ".git", "node_modules", "__pycache__", "dist", "build", ".venv", "venv",
    }

    def __init__(
        self,
        url: str,
        branch: str = "main",
        local_path: str = "datasets/raw_datasets/git",
        token: str | None = None,
    ):
        self.url = url
        self.branch = branch.strip() or "main"
        self.token = token if token is not None else settings.GITHUB_TOKEN
        repo_name = self._get_repo_name(url)
        self.local_path = Path(local_path) / repo_name

    @staticmethod
    def _get_repo_name(url: str) -> str:
        canonical = canonical_github_repository(url)
        if canonical:
            return canonical[1].split("/", 1)[1]
        parsed = urlparse(url)
        path = parsed.path.rstrip("/")
        name = Path(path).stem
        if not name:
            raise ValueError("Invalid Git repository URL")
        return name

    def _git_env(self) -> dict[str, str]:
        env = os.environ.copy()
        # Apply credentials only to GitHub requests and only for this subprocess;
        # the token is not embedded in the persisted remote URL or command line.
        parsed_host = (urlparse(self.url).hostname or "").lower()
        if self.url.startswith("git@") and ":" in self.url:
            parsed_host = self.url[4:].split(":", 1)[0].lower()
        if self.token and parsed_host == "github.com":
            credential = base64.b64encode(f"x-access-token:{self.token}".encode()).decode()
            existing_count = int(env.get("GIT_CONFIG_COUNT", "0") or "0")
            env[f"GIT_CONFIG_KEY_{existing_count}"] = "http.https://github.com/.extraheader"
            env[f"GIT_CONFIG_VALUE_{existing_count}"] = f"AUTHORIZATION: basic {credential}"
            env["GIT_CONFIG_COUNT"] = str(existing_count + 1)
        return env

    def _run_git(self, *args: str, cwd: str | None = None) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["git", *args], cwd=cwd, capture_output=True, text=True,
            check=True, env=self._git_env(),
        )

    def validate(self) -> bool:
        try:
            self._run_git("ls-remote", "--exit-code", "--heads", self.url, self.branch)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, ValueError):
            return False

    def sync_repository(self) -> None:
        depth = max(1, min(int(settings.CODEMIND_GIT_HISTORY_DEPTH), 5000))
        self.local_path.parent.mkdir(parents=True, exist_ok=True)

        if not self.local_path.exists():
            self._run_git(
                "clone", "--depth", str(depth), "--single-branch", "--branch",
                self.branch, self.url, str(self.local_path),
            )
            return

        if not (self.local_path / ".git").exists():
            raise ValueError(
                f"Repository target exists but is not a Git checkout: {self.local_path}"
            )

        current_remote = self._run_git("remote", "get-url", "origin", cwd=str(self.local_path)).stdout.strip()
        configured = canonical_github_repository(self.url)
        current = canonical_github_repository(current_remote)
        if configured and current and configured != current:
            raise ValueError("Existing checkout origin does not match the configured GitHub repository.")
        if not configured and current_remote.rstrip("/") != self.url.rstrip("/"):
            raise ValueError("Existing checkout origin does not match the configured repository URL.")

        # A checkout created by the older version may be depth=1. Fetch the
        # configured recent-history window so commit history has useful entries.
        self._run_git(
            "fetch", "--depth", str(depth), "--prune", "origin", self.branch,
            cwd=str(self.local_path),
        )
        self._run_git(
            "checkout", "-B", self.branch, f"origin/{self.branch}", cwd=str(self.local_path)
        )
        self._run_git("reset", "--hard", f"origin/{self.branch}", cwd=str(self.local_path))

    def list_files(self) -> list[ConnectorFile]:
        if not self.local_path.exists():
            self.sync_repository()
        files = []
        for file_path in self.local_path.rglob("*"):
            if not file_path.is_file():
                continue
            relative_parts = file_path.relative_to(self.local_path).parts
            if any(directory in self.IGNORED_DIRECTORIES for directory in relative_parts):
                continue
            if file_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
                continue
            files.append(ConnectorFile(
                path=str(file_path), name=file_path.name,
                extension=file_path.suffix.lower(), size=file_path.stat().st_size,
            ))
        return files

    def read_file(self, path: str) -> str:
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        return file_path.read_text(encoding="utf-8", errors="replace")
