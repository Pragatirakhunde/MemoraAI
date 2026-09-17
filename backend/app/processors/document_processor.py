from app.models.document import Document

from app.processors.cleaners.text_cleaner import TextCleaner
from app.processors.chunkers.text_chunker import TextChunker
from app.processors.metadata.extractor import MetadataExtractor
from app.processors.parsers.factory import parse_document
from app.processors.result import ProcessingResult


class DocumentProcessor:

    def __init__(self):

        self.cleaner = TextCleaner()
        self.metadata_extractor = MetadataExtractor()
        self.chunker = TextChunker()

    def process(
        self,
        document: Document,
    ) -> ProcessingResult:

        raw_text = parse_document(document)

        cleaned_text = self.cleaner.clean(
            raw_text
        )

        metadata = self.metadata_extractor.extract(
            document,
            cleaned_text,
        )

        chunks = self.chunker.chunk(
            cleaned_text,
            extension=document.extension,
        )

        return ProcessingResult(
            document_id=document.id,
            cleaned_text=cleaned_text,
            metadata=metadata,
            chunks=chunks,
        )