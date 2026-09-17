from app.connectors.base import BaseConnector
from app.connectors.git.repository import (
    GitRepositoryConnector,
)
from app.connectors.local.directory import (
    LocalDirectoryConnector,
)


def get_connector(
    source_type: str,
    config: dict,
) -> BaseConnector:

    if source_type == "local_directory":

        directory = config.get("directory")

        if not directory:
            raise ValueError(
                "Directory path is required"
            )

        return LocalDirectoryConnector(directory)

    if source_type == "git":

        url = config.get("url")

        if not url:
            raise ValueError(
                "Git repository URL is required"
            )

        return GitRepositoryConnector(
            url=url,
            branch=config.get("branch", "main"),
            local_path=config.get(
                "local_path",
                "datasets/raw_datasets/git",
            ),
        )

    raise ValueError(
        f"Unsupported connector type: {source_type}"
    )