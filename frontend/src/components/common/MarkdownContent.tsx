import type { ReactNode } from "react";

interface MarkdownContentProps {
    content: string;
    className?: string;
}

function inlineMarkdown(text: string, keyPrefix: string): ReactNode[] {
    // A deliberately small, safe Markdown subset for model-generated prose.
    // It renders React elements directly and never injects raw HTML.
    const pattern = /(\*\*.+?\*\*|__.+?__|~~.+?~~|`[^`]+`|\*[^*\n]+\*|\[[^\]]+\]\(https?:\/\/[^)\s]+\))/g;
    const result: ReactNode[] = [];
    let cursor = 0;
    let match: RegExpExecArray | null;
    let tokenIndex = 0;

    while ((match = pattern.exec(text)) !== null) {
        if (match.index > cursor) {
            result.push(text.slice(cursor, match.index));
        }
        const token = match[0];
        const key = `${keyPrefix}-inline-${tokenIndex++}`;
        const link = token.match(/^\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)$/);

        if (link) {
            result.push(
                <a key={key} href={link[2]} target="_blank" rel="noopener noreferrer" className="font-medium text-blue-700 underline underline-offset-2">
                    {link[1]}
                </a>,
            );
        } else if (token.startsWith("**") || token.startsWith("__")) {
            result.push(<strong key={key} className="font-semibold text-slate-900">{token.slice(2, -2)}</strong>);
        } else if (token.startsWith("~~")) {
            result.push(<del key={key}>{token.slice(2, -2)}</del>);
        } else if (token.startsWith("`")) {
            result.push(<code key={key} className="rounded bg-slate-100 px-1.5 py-0.5 font-mono text-[0.9em] text-rose-700">{token.slice(1, -1)}</code>);
        } else if (token.startsWith("*")) {
            result.push(<em key={key}>{token.slice(1, -1)}</em>);
        }
        cursor = match.index + token.length;
    }

    if (cursor < text.length) result.push(text.slice(cursor));
    return result;
}

function cellsFromRow(line: string): string[] {
    let row = line.trim();
    if (row.startsWith("|")) row = row.slice(1);
    if (row.endsWith("|")) row = row.slice(0, -1);
    return row.split("|").map((cell) => cell.trim());
}

function isTableDivider(line: string): boolean {
    const cells = cellsFromRow(line);
    return cells.length > 0 && cells.every((cell) => /^:?-{3,}:?$/.test(cell.replace(/\s/g, "")));
}

function isBlockStart(lines: string[], index: number): boolean {
    const line = lines[index].trim();
    return (
        line.startsWith("```") ||
        /^#{1,6}\s/.test(line) ||
        /^[-*_]{3,}\s*$/.test(line) ||
        /^>\s?/.test(line) ||
        /^\s*[-*+]\s+/.test(lines[index]) ||
        /^\s*\d+[.)]\s+/.test(lines[index]) ||
        (line.includes("|") && index + 1 < lines.length && isTableDivider(lines[index + 1]))
    );
}

export default function MarkdownContent({ content, className = "" }: MarkdownContentProps) {
    const lines = (content || "").replace(/\r\n?/g, "\n").split("\n");
    const blocks: ReactNode[] = [];
    let index = 0;
    let blockIndex = 0;

    while (index < lines.length) {
        const raw = lines[index];
        const trimmed = raw.trim();
        const key = `markdown-block-${blockIndex++}`;

        if (!trimmed) {
            index += 1;
            continue;
        }

        if (trimmed.startsWith("```")) {
            const language = trimmed.slice(3).trim().split(/\s+/)[0] || "code";
            index += 1;
            const codeLines: string[] = [];
            while (index < lines.length && !lines[index].trim().startsWith("```")) {
                codeLines.push(lines[index]);
                index += 1;
            }
            if (index < lines.length) index += 1;
            blocks.push(
                <div key={key} className="my-3 overflow-hidden rounded-xl border border-slate-200 bg-slate-950">
                    <div className="border-b border-slate-700 px-3 py-1.5 text-[11px] font-medium uppercase tracking-wide text-slate-400">{language}</div>
                    <pre className="overflow-x-auto p-4 text-[13px] leading-6 text-slate-100"><code>{codeLines.join("\n")}</code></pre>
                </div>,
            );
            continue;
        }

        if (/^[-*_]{3,}\s*$/.test(trimmed)) {
            blocks.push(<hr key={key} className="my-4 border-slate-200" />);
            index += 1;
            continue;
        }

        const heading = trimmed.match(/^(#{1,6})\s+(.+)$/);
        if (heading) {
            const level = heading[1].length;
            const sizes = ["text-2xl", "text-xl", "text-lg", "text-base", "text-sm", "text-sm"];
            const headingClass = `mb-2 mt-4 ${sizes[level - 1]} font-semibold tracking-tight text-slate-900 first:mt-0`;
            const children = inlineMarkdown(heading[2], key);
            const element = level === 1 ? <h1 className={headingClass}>{children}</h1>
                : level === 2 ? <h2 className={headingClass}>{children}</h2>
                : level === 3 ? <h3 className={headingClass}>{children}</h3>
                : level === 4 ? <h4 className={headingClass}>{children}</h4>
                : level === 5 ? <h5 className={headingClass}>{children}</h5>
                : <h6 className={headingClass}>{children}</h6>;
            blocks.push(<div key={key}>{element}</div>);
            index += 1;
            continue;
        }

        if (trimmed.includes("|") && index + 1 < lines.length && isTableDivider(lines[index + 1])) {
            const headers = cellsFromRow(raw);
            index += 2;
            const rows: string[][] = [];
            while (index < lines.length && lines[index].trim() && lines[index].includes("|")) {
                rows.push(cellsFromRow(lines[index]));
                index += 1;
            }
            blocks.push(
                <div key={key} className="my-3 overflow-x-auto rounded-lg border border-slate-200">
                    <table className="w-full border-collapse text-left text-sm">
                        <thead className="bg-slate-50"><tr>{headers.map((cell, i) => <th key={`${key}-h-${i}`} className="border-b px-3 py-2.5 font-semibold text-slate-800">{inlineMarkdown(cell, `${key}-h-${i}`)}</th>)}</tr></thead>
                        <tbody>{rows.map((row, r) => <tr key={`${key}-r-${r}`} className="odd:bg-white even:bg-slate-50/50">{headers.map((_, c) => <td key={`${key}-r-${r}-c-${c}`} className="border-b border-slate-100 px-3 py-2.5 align-top last:border-0">{inlineMarkdown(row[c] || "", `${key}-r-${r}-c-${c}`)}</td>)}</tr>)}</tbody>
                    </table>
                </div>,
            );
            continue;
        }

        if (/^>\s?/.test(trimmed)) {
            const quoteLines: string[] = [];
            while (index < lines.length && /^>\s?/.test(lines[index].trim())) {
                quoteLines.push(lines[index].trim().replace(/^>\s?/, ""));
                index += 1;
            }
            blocks.push(<blockquote key={key} className="my-3 border-l-4 border-slate-300 pl-4 text-slate-600">{quoteLines.map((line, i) => <p key={`${key}-${i}`} className="my-1">{inlineMarkdown(line, `${key}-quote-${i}`)}</p>)}</blockquote>);
            continue;
        }

        const unordered = /^\s*[-*+]\s+/.test(raw);
        const ordered = /^\s*\d+[.)]\s+/.test(raw);
        if (unordered || ordered) {
            const listItems: string[] = [];
            while (index < lines.length) {
                const listLine = lines[index];
                const matches = unordered ? /^\s*[-*+]\s+(.+)$/.exec(listLine) : /^\s*\d+[.)]\s+(.+)$/.exec(listLine);
                if (!matches) break;
                listItems.push(matches[1]);
                index += 1;
            }
            const listClass = "my-2 space-y-1 pl-6 marker:text-slate-400";
            blocks.push(unordered
                ? <ul key={key} className={`${listClass} list-disc`}>{listItems.map((item, i) => <li key={`${key}-${i}`} className="pl-1">{inlineMarkdown(item, `${key}-li-${i}`)}</li>)}</ul>
                : <ol key={key} className={`${listClass} list-decimal`}>{listItems.map((item, i) => <li key={`${key}-${i}`} className="pl-1">{inlineMarkdown(item, `${key}-li-${i}`)}</li>)}</ol>);
            continue;
        }

        const paragraphLines: string[] = [];
        while (index < lines.length && lines[index].trim() && !isBlockStart(lines, index)) {
            paragraphLines.push(lines[index].trim());
            index += 1;
        }
        // A non-empty line is consumed in the block-start path only if a specific
        // block type is recognized above. This fallback prevents a parsing loop.
        if (paragraphLines.length === 0) {
            paragraphLines.push(lines[index].trim());
            index += 1;
        }
        blocks.push(<p key={key} className="my-2 leading-7 text-slate-700 first:mt-0 last:mb-0">{paragraphLines.map((line, i) => <span key={`${key}-line-${i}`}>{i > 0 ? " " : ""}{inlineMarkdown(line, `${key}-p-${i}`)}</span>)}</p>);
    }

    return <div className={`min-w-0 break-words text-sm leading-7 ${className}`}>{blocks}</div>;
}
