import subprocess
from pathlib import Path
from urllib.parse import urlparse

from app.connectors.base import BaseConnector, ConnectorFile


class GitRepositoryConnector(BaseConnector):

    SUPPORTED_EXTENSIONS = {
        ".md",
        ".txt",
        ".py",
        ".js",
        ".ts",
        ".tsx",
        ".jsx",
        ".java",
        ".cpp",
        ".c",
        ".h",
        ".json",
        ".yaml",
        ".yml",
    }

    IGNORED_DIRECTORIES = {
        ".git",
        "node_modules",
        "__pycache__",
        "dist",
        "build",
        ".venv",
        "venv",
    }

    def __init__(
        self,
        url: str,
        branch: str = "main",
        local_path: str = "datasets/raw_datasets/git",
    ):
        self.url = url
        self.branch = branch

        repo_name = self._get_repo_name(url)

        self.local_path = (
            Path(local_path) / repo_name
        )

    @staticmethod
    def _get_repo_name(url: str) -> str:
        path = urlparse(url).path.rstrip("/")

        name = Path(path).stem

        if not name:
            raise ValueError("Invalid Git repository URL")

        return name

    def _run_git(
        self,
        *args: str,
        cwd: str | None = None,
    ) -> subprocess.CompletedProcess:

        return subprocess.run(
            ["git", *args],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True,
        )

    def validate(self) -> bool:

        try:
            self._run_git(
                "ls-remote",
                "--exit-code",
                "--heads",
                self.url,
                self.branch,
            )

            return True

        except (
            subprocess.CalledProcessError,
            FileNotFoundError,
        ):
            return False

    def sync_repository(self) -> None:

        self.local_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if not self.local_path.exists():

            self._run_git(
                "clone",
                "--depth",
                "1",
                "--branch",
                self.branch,
                self.url,
                str(self.local_path),
            )

        else:

            self._run_git(
                "fetch",
                "--depth",
                "1",
                "origin",
                self.branch,
                cwd=str(self.local_path),
            )

            self._run_git(
                "checkout",
                self.branch,
                cwd=str(self.local_path),
            )

            self._run_git(
                "reset",
                "--hard",
                f"origin/{self.branch}",
                cwd=str(self.local_path),
            )

    def list_files(self) -> list[ConnectorFile]:

        if not self.local_path.exists():
            self.sync_repository()

        files = []

        for file_path in self.local_path.rglob("*"):

            if not file_path.is_file():
                continue

            relative_parts = file_path.relative_to(
                self.local_path
            ).parts

            if any(
                directory in self.IGNORED_DIRECTORIES
                for directory in relative_parts
            ):
                continue

            if file_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
                continue

            files.append(
                ConnectorFile(
                    path=str(file_path),
                    name=file_path.name,
                    extension=file_path.suffix.lower(),
                    size=file_path.stat().st_size,
                )
            )

        return files

    def read_file(self, path: str) -> str:

        file_path = Path(path)

        if not file_path.exists():
            raise FileNotFoundError(
                f"File not found: {path}"
            )

        return file_path.read_text(
            encoding="utf-8",
            errors="replace",
        )