from app.models.document import Document

from app.processors.parsers.code_parser import CodeParser
from app.processors.parsers.markdown_parser import MarkdownParser
from app.processors.parsers.plain_text_parser import PlainTextParser


markdown_parser = MarkdownParser()
code_parser = CodeParser()
plain_text_parser = PlainTextParser()


def parse_document(document: Document) -> str:

    extension = document.extension.lower()

    if extension == ".md":
        return markdown_parser.parse(document)

    if extension in CodeParser.SUPPORTED_EXTENSIONS:
        return code_parser.parse(document)

    if extension in PlainTextParser.SUPPORTED_EXTENSIONS:
        return plain_text_parser.parse(document)

    raise ValueError(
        f"No parser available for {extension}"
    )