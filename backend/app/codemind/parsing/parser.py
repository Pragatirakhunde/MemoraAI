from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field


@dataclass
class ParsedSymbol:
    symbol_type: str
    name: str
    qualified_name: str
    signature: str
    docstring: str | None
    start_line: int
    end_line: int
    parent_name: str | None = None
    metadata: dict = field(default_factory=dict)
    call_names: list[str] = field(default_factory=list)


@dataclass
class ParsedFile:
    language: str
    symbols: list[ParsedSymbol]
    imports: list[str]


class CodeParser:
    LANGUAGE_MAP = {
        ".py": "python",
        ".js": "javascript",
        ".jsx": "javascript",
        ".ts": "typescript",
        ".tsx": "tsx",
    }

    def language_for_extension(self, extension: str) -> str | None:
        return self.LANGUAGE_MAP.get(extension.lower())

    @staticmethod
    def _python_calls(node: ast.AST) -> list[str]:
        names: set[str] = set()
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                fn = child.func
                if isinstance(fn, ast.Name):
                    names.add(fn.id)
                elif isinstance(fn, ast.Attribute):
                    names.add(fn.attr)
        return sorted(names)

    @staticmethod
    def _tree_sitter_parse(source: str, language: str):
        """Best-effort Tree-sitter parsing. The normal AST/regex extractors
        remain as a compatibility fallback if an optional grammar is not
        installed or a grammar API differs between package versions.
        """
        try:
            from tree_sitter import Language, Parser
            import tree_sitter_python
            import tree_sitter_javascript
            import tree_sitter_typescript
        except ImportError:
            return None

        grammar_factories = {
            "python": tree_sitter_python.language,
            "javascript": tree_sitter_javascript.language,
            "typescript": tree_sitter_typescript.language_typescript,
            "tsx": tree_sitter_typescript.language_tsx,
        }
        factory = grammar_factories.get(language)
        if factory is None:
            return None

        try:
            parser = Parser(Language(factory()))
            return parser.parse(source.encode("utf-8"))
        except Exception:
            return None

    def _parse_python(self, source: str) -> ParsedFile:
        tree = ast.parse(source)
        symbols: list[ParsedSymbol] = []
        imports: list[str] = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                segment = ast.get_source_segment(source, node)
                if segment:
                    imports.append(segment)

        def walk_defs(nodes: list[ast.AST], parents: list[str]):
            for node in nodes:
                if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                    symbol_type = "class" if isinstance(node, ast.ClassDef) else "function"
                    qualified = ".".join([*parents, node.name]) if parents else node.name
                    segment = ast.get_source_segment(source, node) or node.name
                    signature = segment.splitlines()[0][:1000]
                    symbols.append(
                        ParsedSymbol(
                            symbol_type=symbol_type,
                            name=node.name,
                            qualified_name=qualified,
                            signature=signature,
                            docstring=ast.get_docstring(node),
                            start_line=node.lineno,
                            end_line=getattr(node, "end_lineno", node.lineno),
                            parent_name=parents[-1] if parents else None,
                            call_names=self._python_calls(node),
                        )
                    )
                    walk_defs(getattr(node, "body", []), [*parents, node.name])
                elif isinstance(node, (ast.If, ast.For, ast.While, ast.Try, ast.With, ast.AsyncWith)):
                    walk_defs(getattr(node, "body", []), parents)

        walk_defs(tree.body, [])
        return ParsedFile("python", symbols, sorted(set(x.strip() for x in imports if x.strip())))

    @staticmethod
    def _brace_end_line(lines: list[str], start_index: int) -> int:
        depth = 0
        seen_open = False
        for i in range(start_index, len(lines)):
            line = lines[i]
            opens = line.count("{")
            closes = line.count("}")
            if opens:
                seen_open = True
            depth += opens - closes
            if seen_open and depth <= 0:
                return i + 1
        return min(len(lines), start_index + 1)

    def _parse_js_like(self, source: str, language: str) -> ParsedFile:
        # Validate syntax with Tree-sitter when available. Extraction uses a
        # conservative declaration parser so it remains usable if a grammar
        # package is unavailable in an offline environment.
        self._tree_sitter_parse(source, language)

        symbols: list[ParsedSymbol] = []
        imports: list[str] = []
        lines = source.splitlines()

        for i, line in enumerate(lines):
            line_no = i + 1
            stripped = line.strip()
            if re.match(r"^(?:import\s+|export\s*\{).*", stripped):
                imports.append(stripped)

            class_match = re.search(r"\bclass\s+([A-Za-z_$][\w$]*)", stripped)
            if class_match:
                name = class_match.group(1)
                end_line = self._brace_end_line(lines, i)
                symbols.append(
                    ParsedSymbol("class", name, name, stripped[:1000], None, line_no, end_line)
                )

            fn = re.search(
                r"(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s+([A-Za-z_$][\w$]*)\s*\(",
                stripped,
            )
            if fn:
                name = fn.group(1)
                end_line = self._brace_end_line(lines, i)
                body = "\n".join(lines[i:end_line])
                symbols.append(
                    ParsedSymbol(
                        "function", name, name, stripped[:1000], None, line_no, end_line,
                        call_names=sorted(set(re.findall(r"\b([A-Za-z_$][\w$]*)\s*\(", body))),
                    )
                )

            arrow = re.search(
                r"(?:export\s+)?(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?(?:\([^)]*\)|[A-Za-z_$][\w$]*)\s*=>",
                stripped,
            )
            if arrow:
                name = arrow.group(1)
                end_line = self._brace_end_line(lines, i)
                body = "\n".join(lines[i:end_line])
                symbols.append(
                    ParsedSymbol(
                        "function", name, name, stripped[:1000], None, line_no, end_line,
                        call_names=sorted(set(re.findall(r"\b([A-Za-z_$][\w$]*)\s*\(", body))),
                    )
                )

            method = re.search(r"^([A-Za-z_$][\w$]*)\s*\([^)]*\)\s*\{", stripped)
            if method and not stripped.startswith(("if", "for", "while", "switch", "catch", "function")):
                name = method.group(1)
                end_line = self._brace_end_line(lines, i)
                body = "\n".join(lines[i:end_line])
                symbols.append(
                    ParsedSymbol(
                        "method", name, name, stripped[:1000], None, line_no, end_line,
                        call_names=sorted(set(re.findall(r"\b([A-Za-z_$][\w$]*)\s*\(", body))),
                    )
                )

        # Keep the first occurrence of a declaration at the same source line.
        seen = set()
        unique_symbols = []
        for symbol in symbols:
            key = (symbol.symbol_type, symbol.name, symbol.start_line)
            if key in seen:
                continue
            seen.add(key)
            unique_symbols.append(symbol)

        return ParsedFile(language, unique_symbols, sorted(set(imports)))

    def parse(self, source: str, extension: str) -> ParsedFile:
        language = self.language_for_extension(extension)
        if language is None:
            return ParsedFile("unknown", [], [])
        if language == "python":
            try:
                return self._parse_python(source)
            except SyntaxError:
                return ParsedFile(language, [], [])
        return self._parse_js_like(source, language)
