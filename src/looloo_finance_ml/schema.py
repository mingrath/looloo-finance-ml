"""Small, JSON-safe schemas shared by fetchers, models, and replay."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import math
from typing import Any, Mapping

from .hashing import canonical_json, sha256_json


_RESERVED_EVENT_FIELDS = frozenset(
    {
        "run_id",
        "event_id",
        "contract_version",
        "code_commit",
        "event_at",
        "event_seq",
        "event_type",
        "decision_at",
        "decision_event_at",
        "execution_at",
        "label_end",
        "retrieved_at",
        "generated_at",
    }
)


def _require_aware(name: str, value: datetime | None, *, optional: bool = False) -> None:
    if value is None and optional:
        return
    if value is None or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")


@dataclass(frozen=True)
class Bar:
    symbol: str
    bar_end_at: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    source: str
    adjustment: str
    retrieved_at: datetime | None = None
    raw_timestamp: str | None = None

    def __post_init__(self) -> None:
        if not self.symbol or not self.source or not self.adjustment:
            raise ValueError("Bar symbol, source, and adjustment are required")
        _require_aware("bar_end_at", self.bar_end_at)
        _require_aware("retrieved_at", self.retrieved_at, optional=True)
        self.validate()

    def validate(self) -> None:
        values = (self.open, self.high, self.low, self.close, self.volume)
        if any(not math.isfinite(float(v)) for v in values):
            raise ValueError(f"non-finite OHLCV for {self.symbol} at {self.bar_end_at}")
        if min(values) <= 0:
            raise ValueError(f"non-positive OHLCV for {self.symbol} at {self.bar_end_at}")
        if self.high < max(self.open, self.close) or self.low > min(self.open, self.close):
            raise ValueError(f"malformed OHLC for {self.symbol} at {self.bar_end_at}")

    def as_dict(self) -> dict[str, Any]:
        return {
            "symbol": self.symbol,
            "bar_end_at": self.bar_end_at.isoformat(),
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume,
            "source": self.source,
            "adjustment": self.adjustment,
            "retrieved_at": self.retrieved_at.isoformat() if self.retrieved_at else None,
            "raw_timestamp": self.raw_timestamp,
        }


@dataclass(frozen=True)
class Manifest:
    source: str
    stream: str
    params: Mapping[str, Any]
    retrieved_at: datetime
    response_hash: str
    schema_hash: str
    row_count: int
    symbols: tuple[str, ...]
    start: str
    end: str
    notes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.source or not self.stream:
            raise ValueError("Manifest source and stream are required")
        _require_aware("retrieved_at", self.retrieved_at)
        if self.row_count < 0:
            raise ValueError("Manifest row_count cannot be negative")
        if not self.response_hash or not self.schema_hash:
            raise ValueError("Manifest response_hash and schema_hash are required")
        object.__setattr__(self, "symbols", tuple(self.symbols))
        object.__setattr__(self, "notes", tuple(self.notes))

    @property
    def manifest_hash(self) -> str:
        return sha256_json(self.as_dict())

    def as_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "stream": self.stream,
            "params": dict(self.params),
            "retrieved_at": self.retrieved_at.isoformat(),
            "response_hash": self.response_hash,
            "schema_hash": self.schema_hash,
            "row_count": self.row_count,
            "symbols": list(self.symbols),
            "start": self.start,
            "end": self.end,
            "notes": list(self.notes),
        }


@dataclass(frozen=True)
class Event:
    run_id: str
    event_id: str
    contract_version: str
    code_commit: str
    event_at: datetime
    event_seq: int
    event_type: str
    decision_at: datetime | None = None
    decision_event_at: datetime | None = None
    execution_at: datetime | None = None
    label_end: datetime | None = None
    retrieved_at: datetime | None = None
    generated_at: datetime | None = None
    fields: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.run_id or not self.event_id or not self.contract_version or not self.event_type:
            raise ValueError("Event identifiers, contract_version, and event_type are required")
        if self.event_seq < 0:
            raise ValueError("event_seq cannot be negative")
        _require_aware("event_at", self.event_at)
        for name in (
            "decision_at",
            "decision_event_at",
            "execution_at",
            "label_end",
            "retrieved_at",
            "generated_at",
        ):
            _require_aware(name, getattr(self, name), optional=True)
        fields = dict(self.fields)
        collisions = _RESERVED_EVENT_FIELDS.intersection(fields)
        if collisions:
            raise ValueError(f"Event.fields collides with reserved keys: {sorted(collisions)}")
        object.__setattr__(self, "fields", fields)

    def as_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "run_id": self.run_id,
            "event_id": self.event_id,
            "contract_version": self.contract_version,
            "code_commit": self.code_commit,
            "event_at": self.event_at.isoformat(),
            "event_seq": self.event_seq,
            "event_type": self.event_type,
            "decision_at": self.decision_at.isoformat() if self.decision_at else None,
            "decision_event_at": self.decision_event_at.isoformat()
            if self.decision_event_at
            else None,
            "execution_at": self.execution_at.isoformat() if self.execution_at else None,
            "label_end": self.label_end.isoformat() if self.label_end else None,
            "retrieved_at": self.retrieved_at.isoformat() if self.retrieved_at else None,
            "generated_at": self.generated_at.isoformat() if self.generated_at else None,
        }
        data.update(self.fields)
        return data

    def json_bytes(self) -> bytes:
        return canonical_json(self.as_dict())
