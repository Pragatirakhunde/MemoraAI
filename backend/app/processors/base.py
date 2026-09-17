from abc import ABC, abstractmethod

from app.models.document import Document


class BaseProcessor(ABC):

    @abstractmethod
    def process(self, document: Document) -> dict:
        """
        Process a document and return processed data.
        """
        pass