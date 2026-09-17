import re


class TextChunker:

    def __init__(
        self,
        chunk_size: int = 1000,
        overlap: int = 100,
    ):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(
        self,
        text: str,
        extension: str = ".txt",
    ) -> list[str]:

        if not text:
            return []

        extension = extension.lower()

        if extension == ".md":
            sections = self._split_markdown(text)
        elif extension in {
            ".py",
            ".js",
            ".ts",
            ".tsx",
            ".jsx",
            ".java",
            ".cpp",
            ".c",
            ".h",
        }:
            sections = self._split_code(text)
        else:
            sections = self._split_paragraphs(text)

        return self._build_chunks(sections)

    def _split_markdown(
        self,
        text: str,
    ) -> list[str]:

        lines = text.splitlines()

        sections = []
        current = []

        for line in lines:

            if re.match(r"^#{1,6}\s+", line):

                if current:
                    sections.append(
                        "\n".join(current).strip()
                    )
                    current = []

            current.append(line)

        if current:
            sections.append(
                "\n".join(current).strip()
            )

        return [
            section
            for section in sections
            if section
        ]

    def _split_code(
        self,
        text: str,
    ) -> list[str]:

        blocks = re.split(
            r"\n\s*\n",
            text,
        )

        return [
            block.strip()
            for block in blocks
            if block.strip()
        ]

    def _split_paragraphs(
        self,
        text: str,
    ) -> list[str]:

        paragraphs = re.split(
            r"\n\s*\n",
            text,
        )

        return [
            paragraph.strip()
            for paragraph in paragraphs
            if paragraph.strip()
        ]

    def _build_chunks(
        self,
        sections: list[str],
    ) -> list[str]:

        chunks = []
        current = ""

        for section in sections:

            # If the section itself is too large,
            # split it safely by character size.
            if len(section) > self.chunk_size:

                if current:
                    chunks.append(current.strip())
                    current = ""

                chunks.extend(
                    self._split_large_section(section)
                )

                continue

            if not current:
                current = section
                continue

            combined = (
                current
                + "\n\n"
                + section
            )

            if len(combined) <= self.chunk_size:

                current = combined

            else:

                chunks.append(current.strip())

                overlap_text = current[
                    max(
                        0,
                        len(current) - self.overlap,
                    ):
                ]

                current = (
                    overlap_text
                    + "\n\n"
                    + section
                )

        if current:
            chunks.append(current.strip())

        return chunks

    def _split_large_section(
        self,
        section: str,
    ) -> list[str]:

        chunks = []

        start = 0
        length = len(section)

        while start < length:

            end = min(
                start + self.chunk_size,
                length,
            )

            chunk = section[
                start:end
            ].strip()

            if chunk:
                chunks.append(chunk)

            if end >= length:
                break

            start = max(
                end - self.overlap,
                start + 1,
            )

        return chunks