from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ConnectorFile:
    path: str
    name: str
    extension: str
    size: int


class BaseConnector(ABC):

    @abstractmethod
    def validate(self) -> bool:
        """Check whether the data source is accessible."""
        pass

    @abstractmethod
    def list_files(self) -> list[ConnectorFile]:
        """Return files available from the source."""
        pass

    @abstractmethod
    def read_file(self, path: str) -> str:
        """Read a file's text content."""
        pass