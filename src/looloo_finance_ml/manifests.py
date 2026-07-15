"""Manifest and raw-response persistence with stable hashes."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

from .hashing import canonical_json, sha256_bytes, sha256_json
from .schema import Manifest


def dataframe_schema_hash(frame: pd.DataFrame) -> str:
    schema = [{"name": str(column), "dtype": str(frame[column].dtype)} for column in frame.columns]
    return sha256_json(schema)


def raw_response_hash(body: bytes) -> str:
    """Hash the exact downloaded response bytes, before parsing or normalization."""
    return sha256_bytes(body)


def content_hash(payload: Any) -> str:
    """Hash a normalized JSON value when no raw response exists (fixtures only)."""
    return sha256_bytes(canonical_json(payload))


def write_json(path: str | Path, value: Any) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(canonical_json(value) + b"\n")


def write_jsonl(path: str | Path, rows: Iterable[dict[str, Any]]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("wb") as handle:
        for row in rows:
            handle.write(canonical_json(row) + b"\n")


def read_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_manifest(path: str | Path, manifest: Manifest) -> None:
    write_json(path, {**manifest.as_dict(), "manifest_hash": manifest.manifest_hash})


def manifest_for_frame(
    frame: pd.DataFrame,
    *,
    source: str,
    stream: str,
    params: dict[str, Any],
    symbols: tuple[str, ...],
    start: str,
    end: str,
    raw_payload: Any | None = None,
    raw_response_digest: str | None = None,
    retrieved_at: datetime | None = None,
    notes: tuple[str, ...] = (),
) -> Manifest:
    retrieved = retrieved_at or datetime.now(timezone.utc)
    if retrieved.tzinfo is None or retrieved.utcoffset() is None:
        raise ValueError("retrieved_at must be timezone-aware")
    digest = raw_response_digest
    if digest is None:
        if raw_payload is None:
            raise ValueError("raw_response_digest or raw_payload is required")
        digest = content_hash(raw_payload)
        notes = (*notes, "content_hash used because no raw response bytes were supplied")
    return Manifest(
        source=source,
        stream=stream,
        params=params,
        retrieved_at=retrieved,
        response_hash=digest,
        schema_hash=dataframe_schema_hash(frame),
        row_count=len(frame),
        symbols=tuple(symbols),
        start=start,
        end=end,
        notes=notes,
    )
