"""
Table detection and extraction from markdown text.

Tables are identified by the standard GFM pattern:
  | col | col |
  |-----|-----|
  | val | val |

They are extracted so the chunker can treat each table as an atomic unit
(never split mid-table).
"""
from __future__ import annotations

import re
from dataclasses import dataclass


# Matches a GFM table: header row + separator row + 1+ data rows
_TABLE_RE = re.compile(
    r"(?:^|\n)"                        # start-of-string or newline before table
    r"(\|[^\n]+\|\n"                   # header row
    r"\|[-:| ]+\|\n"                   # separator row
    r"(?:\|[^\n]+\|\n?)+)",            # one or more data rows
    re.MULTILINE,
)


@dataclass
class TableSpan:
    text: str        # full table markdown
    start: int       # character offset in the source markdown
    end: int


def find_tables(markdown: str) -> list[TableSpan]:
    """Return all GFM tables found in *markdown* with their character spans."""
    tables: list[TableSpan] = []
    for m in _TABLE_RE.finditer(markdown):
        tables.append(TableSpan(
            text=m.group(1).strip(),
            start=m.start(1),
            end=m.end(1),
        ))
    return tables


def replace_tables_with_placeholders(
    markdown: str,
) -> tuple[str, dict[str, str]]:
    """
    Replace each table in *markdown* with a unique placeholder token.
    Returns (modified_markdown, {placeholder: original_table_text}).
    """
    tables = find_tables(markdown)
    placeholders: dict[str, str] = {}

    # Process in reverse order so offsets stay valid after replacements
    result = markdown
    for i, table in enumerate(reversed(tables)):
        idx = len(tables) - 1 - i
        token = f"\n\n<<HFI_TABLE_{idx}>>\n\n"
        placeholders[f"<<HFI_TABLE_{idx}>>"] = table.text
        result = result[: table.start] + token + result[table.end :]

    return result, placeholders
