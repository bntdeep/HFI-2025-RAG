"""
SQLite metadata store for uploaded documents.

Table: documents
  id           TEXT PRIMARY KEY   (UUID)
  name         TEXT
  path         TEXT
  total_chunks INTEGER
  status       TEXT               (indexing | ready | error)
  created_at   TEXT               (ISO-8601)
  updated_at   TEXT
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from pathlib import Path

import aiosqlite

from ..config import settings

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS documents (
    id           TEXT PRIMARY KEY,
    name         TEXT NOT NULL,
    path         TEXT NOT NULL,
    total_chunks INTEGER DEFAULT 0,
    status       TEXT DEFAULT 'indexing',
    created_at   TEXT NOT NULL,
    updated_at   TEXT NOT NULL
);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class MetadataDB:
    def __init__(self) -> None:
        self._db_path = str(settings.metadata_db_file)
        Path(self._db_path).parent.mkdir(parents=True, exist_ok=True)

    async def _init(self, conn: aiosqlite.Connection) -> None:
        await conn.execute(_CREATE_TABLE)
        await conn.commit()

    # ── Write ─────────────────────────────────────────────────────────────────

    async def add_document(
        self,
        document_id: str,
        document_name: str,
        pdf_path: str,
        total_chunks: int = 0,
        status: str = "indexing",
    ) -> None:
        now = _now()
        async with aiosqlite.connect(self._db_path) as conn:
            await self._init(conn)
            await conn.execute(
                """
                INSERT INTO documents (id, name, path, total_chunks, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name=excluded.name,
                    path=excluded.path,
                    total_chunks=excluded.total_chunks,
                    status=excluded.status,
                    updated_at=excluded.updated_at
                """,
                (document_id, document_name, pdf_path, total_chunks, status, now, now),
            )
            await conn.commit()

    async def set_status(self, document_id: str, status: str) -> None:
        async with aiosqlite.connect(self._db_path) as conn:
            await self._init(conn)
            await conn.execute(
                "UPDATE documents SET status=?, updated_at=? WHERE id=?",
                (status, _now(), document_id),
            )
            await conn.commit()

    async def delete_document(self, document_id: str) -> bool:
        async with aiosqlite.connect(self._db_path) as conn:
            await self._init(conn)
            cur = await conn.execute(
                "DELETE FROM documents WHERE id=?", (document_id,)
            )
            await conn.commit()
            return cur.rowcount > 0

    # ── Read ──────────────────────────────────────────────────────────────────

    async def get_document(self, document_id: str) -> dict | None:
        async with aiosqlite.connect(self._db_path) as conn:
            await self._init(conn)
            conn.row_factory = aiosqlite.Row
            cur = await conn.execute(
                "SELECT * FROM documents WHERE id=?", (document_id,)
            )
            row = await cur.fetchone()
            return dict(row) if row else None

    async def list_documents(self) -> list[dict]:
        async with aiosqlite.connect(self._db_path) as conn:
            await self._init(conn)
            conn.row_factory = aiosqlite.Row
            cur = await conn.execute(
                "SELECT * FROM documents ORDER BY created_at DESC"
            )
            rows = await cur.fetchall()
            return [dict(r) for r in rows]
