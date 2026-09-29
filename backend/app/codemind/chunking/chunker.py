from __future__ import annotations

from dataclasses import dataclass
import hashlib

from app.codemind.parsing.parser import ParsedFile, ParsedSymbol


@dataclass
class CodeChunkDraft:
    index: int
    content: str
    start_line: int
    end_line: int
    symbol: ParsedSymbol | None
    checksum: str


class CodeChunker:
    def build(self, path: str, source: str, parsed: ParsedFile) -> list[CodeChunkDraft]:
        lines = source.splitlines()
        drafts: list[CodeChunkDraft] = []
        for index, symbol in enumerate(parsed.symbols):
            start = max(symbol.start_line - 1, 0)
            end = min(symbol.end_line, len(lines))
            body = "\n".join(lines[start:end]).strip()
            content = (
                f"FILE: {path}\n"
                f"SYMBOL: {symbol.qualified_name}\n"
                f"TYPE: {symbol.symbol_type}\n"
                f"LINES: {symbol.start_line}-{symbol.end_line}\n\n"
                f"{body}"
            ).strip()
            drafts.append(CodeChunkDraft(
                index=index,
                content=content,
                start_line=symbol.start_line,
                end_line=symbol.end_line,
                symbol=symbol,
                checksum=hashlib.sha256(content.encode()).hexdigest(),
            ))
        if not drafts and source.strip():
            content = f"FILE: {path}\nTYPE: file\n\n{source.strip()}"
            drafts.append(CodeChunkDraft(
                index=0,
                content=content,
                start_line=1,
                end_line=max(1, len(lines)),
                symbol=None,
                checksum=hashlib.sha256(content.encode()).hexdigest(),
            ))
        return drafts
