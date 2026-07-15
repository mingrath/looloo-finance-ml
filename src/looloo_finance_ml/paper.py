"""Deterministic local paper-trading replay with no brokerage integration."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
import math
from typing import Any

import numpy as np
import pandas as pd

from .calendar import Session, XNYSCalendar
from .hashing import canonical_json


class PaperError(ValueError):
    """Raised for invalid replay inputs before any simulated order is emitted."""


@dataclass(frozen=True)
class PaperConfig:
    initial_nav: float = 100_000.0
    fee_rate: float = 0.0001
    slippage_rate: float = 0.0005
    top_n: int = 10
    share_decimals: int = 6
    contract_version: str = "finance-ml-v1"
    code_commit: str = "working-tree"

    def __post_init__(self) -> None:
        if (
            self.initial_nav <= 0
            or self.fee_rate < 0
            or self.slippage_rate < 0
            or self.top_n <= 0
            or self.share_decimals < 0
        ):
            raise PaperError("invalid paper configuration")

    @property
    def one_way_cost(self) -> float:
        return self.fee_rate + self.slippage_rate


@dataclass
class _Position:
    symbol: str
    shares: float
    entry_price: float
    exit_date: date
    score: float
    rank: int
    target_weight: float
    decision_at: str


@dataclass
class ReplayResult:
    events: list[dict[str, Any]]
    summary: dict[str, Any]
    failed: bool = False

    def jsonl(self) -> bytes:
        return b"".join(canonical_json(event) + b"\n" for event in self.events)


@dataclass
class PaperLedger:
    config: PaperConfig = field(default_factory=PaperConfig)
    cash: float = field(init=False)
    gross_cash: float = field(init=False)
    positions: dict[str, _Position] = field(default_factory=dict, init=False)
    events: list[dict[str, Any]] = field(default_factory=list, init=False)
    _event_seq: int = field(default=0, init=False)
    pending: tuple[date, tuple[tuple[str, float, int], ...], tuple[str, ...], date, str] | None = (
        field(default=None, init=False)
    )
    failed: bool = field(default=False, init=False)
    _run_id: str = field(default="local-paper", init=False)
    _data_manifest_hash: str = field(default="", init=False)
    _model_artifact_hash: str = field(default="", init=False)
    _feature_schema_hash: str = field(default="", init=False)

    def __post_init__(self) -> None:
        self.cash = self.config.initial_nav
        self.gross_cash = self.config.initial_nav

    def _event(self, event_type: str, event_at: pd.Timestamp, **fields: Any) -> None:
        event = {
            "run_id": fields.pop("run_id", self._run_id),
            "event_id": f"event-{self._event_seq:06d}",
            "contract_version": self.config.contract_version,
            "code_commit": self.config.code_commit,
            "event_at": (
                pd.Timestamp(event_at).tz_localize("UTC")
                if pd.Timestamp(event_at).tzinfo is None
                else pd.Timestamp(event_at).tz_convert("UTC")
            ).isoformat(),
            "event_seq": self._event_seq,
            "event_type": event_type,
            "source_timezone": "America/New_York",
            "decision_at": None,
            "feature_cutoff_at": None,
            "decision_event_at": None,
            "execution_at": None,
            "label_end": None,
            "data_manifest_hash": self._data_manifest_hash,
            "model_artifact_hash": self._model_artifact_hash,
            "feature_schema_hash": self._feature_schema_hash,
            **fields,
        }
        self._event_seq += 1
        self.events.append(event)

    def _nav(self, close_prices: dict[str, float]) -> tuple[float, float, float]:
        position_value = sum(
            position.shares * close_prices[position.symbol] for position in self.positions.values()
        )
        net_nav = self.cash + position_value
        gross_nav = self.gross_cash + position_value
        return net_nav, gross_nav, position_value / net_nav if net_nav else 0.0

    def _fail(self, event_at: pd.Timestamp, code: str, remediation: str, **fields: Any) -> None:
        self.failed = True
        self._event("error", event_at, error_code=code, remediation=remediation, **fields)

    def _fill_entries(
        self,
        session: Session,
        bars: pd.DataFrame,
        selected: tuple[tuple[str, float, int], ...],
        universe: tuple[str, ...],
        exit_date: date,
        decision_at: str,
    ) -> None:
        selected_symbols = tuple(symbol for symbol, _, _ in selected)
        prices = _prices_for_session(bars, universe, session.session_date, "open")
        missing = sorted(set(universe).difference(prices))
        if missing:
            self.pending = None
            self._event(
                "skip",
                session.open_at,
                decision_at=decision_at,
                feature_cutoff_at=decision_at,
                execution_at=session.open_at.isoformat(),
                reason="entry_missing_bar",
                missing_symbols=missing,
            )
            return
        net_nav, _, _ = self._nav({symbol: prices[symbol] for symbol in self.positions})
        budget = net_nav / (1.0 + self.config.one_way_cost)
        target_weight = 1.0 / len(selected)
        target_notional = budget * target_weight
        scale = 10**self.config.share_decimals
        planned: dict[str, float] = {}
        total = 0.0
        for symbol in selected_symbols:
            shares = math.floor(target_notional / prices[symbol] * scale) / scale
            planned[symbol] = shares
            total += shares * prices[symbol] * (1.0 + self.config.one_way_cost)
        gross_notional = sum(planned[symbol] * prices[symbol] for symbol in selected_symbols)
        if total > self.cash + 1e-8 or gross_notional > net_nav + 1e-8:
            self.pending = None
            self._fail(
                session.open_at,
                "position_limit",
                "reduce target size before replay",
                decision_at=decision_at,
                feature_cutoff_at=decision_at,
                execution_at=session.open_at.isoformat(),
                attempted_notional=total,
                gross_notional=gross_notional,
                nav=net_nav,
                cash=self.cash,
            )
            return
        for symbol, score, rank in selected:
            self._event(
                "order",
                session.open_at,
                decision_at=decision_at,
                feature_cutoff_at=decision_at,
                execution_at=session.open_at.isoformat(),
                symbol=symbol,
                score=score,
                rank=rank,
                target_weight=target_weight,
                previous_weight=0.0,
                order_quantity=planned[symbol],
                entry_budget=budget,
                nav_before_event=net_nav,
            )
        for symbol, score, rank in selected:
            shares = planned[symbol]
            notional = shares * prices[symbol]
            fee = notional * self.config.fee_rate
            slippage = notional * self.config.slippage_rate
            self.cash -= notional + fee + slippage
            self.gross_cash -= notional
            self.positions[symbol] = _Position(
                symbol, shares, prices[symbol], exit_date, score, rank, target_weight, decision_at
            )
            self._event(
                "fill",
                session.open_at,
                decision_at=decision_at,
                feature_cutoff_at=decision_at,
                execution_at=session.open_at.isoformat(),
                symbol=symbol,
                score=score,
                rank=rank,
                shares=shares,
                order_quantity=shares,
                fill_price=prices[symbol],
                trade_notional=notional,
                fee=fee,
                slippage=slippage,
                cash=self.cash,
                residual_cash=self.cash,
                entry_budget=budget,
                nav_before_event=net_nav,
                target_weight=target_weight,
                previous_weight=0.0,
            )
        self.pending = None
        if self.cash < -1e-8:
            self._fail(
                session.open_at,
                "negative_cash",
                "inspect cost-inclusive sizing",
                decision_at=decision_at,
                feature_cutoff_at=decision_at,
                execution_at=session.open_at.isoformat(),
            )

    def _fill_exits(self, session: Session, bars: pd.DataFrame) -> None:
        symbols = tuple(sorted(self.positions))
        vintage_decision_at = self.positions[symbols[0]].decision_at
        prices = _prices_for_session(bars, symbols, session.session_date, "close")
        missing = sorted(set(symbols).difference(prices))
        if missing:
            self._fail(
                session.close_at,
                "missing_exit_bar",
                "restore the label_fill_stream close bar before replay",
                decision_at=vintage_decision_at,
                feature_cutoff_at=vintage_decision_at,
                execution_at=session.close_at.isoformat(),
                missing_symbols=missing,
            )
            return
        net_nav, _, _ = self._nav(prices)
        total_fee = 0.0
        total_slippage = 0.0
        for symbol in symbols:
            position = self.positions.pop(symbol)
            notional = position.shares * prices[symbol]
            fee = notional * self.config.fee_rate
            slippage = notional * self.config.slippage_rate
            total_fee += fee
            total_slippage += slippage
            self.cash += notional - fee - slippage
            self.gross_cash += notional
            self._event(
                "exit",
                session.close_at,
                decision_at=position.decision_at,
                feature_cutoff_at=position.decision_at,
                execution_at=session.close_at.isoformat(),
                symbol=symbol,
                score=position.score,
                rank=position.rank,
                shares=position.shares,
                order_quantity=-position.shares,
                fill_price=prices[symbol],
                trade_notional=notional,
                fee=fee,
                slippage=slippage,
                cash=self.cash,
                residual_cash=self.cash,
                nav_before_event=net_nav,
                target_weight=0.0,
                previous_weight=position.target_weight,
            )
        self._event(
            "summary",
            session.close_at,
            decision_at=vintage_decision_at,
            feature_cutoff_at=vintage_decision_at,
            execution_at=session.close_at.isoformat(),
            label_end=session.close_at.isoformat(),
            fee=total_fee,
            slippage=total_slippage,
            cash=self.cash,
            net_nav=self.cash,
            gross_nav=self.gross_cash,
            gross_exposure=0.0,
        )

    def replay(
        self,
        scores: pd.DataFrame,
        label_fill_bars: pd.DataFrame,
        *,
        symbols: tuple[str, ...],
        calendar: XNYSCalendar | None = None,
        run_id: str = "local-paper",
        data_manifest_hash: str = "",
        model_artifact_hash: str = "",
        feature_schema_hash: str = "",
    ) -> ReplayResult:
        required_scores = {"decision_at", "symbol", "score"}
        required_bars = {"symbol", "bar_end_at", "open", "close", "adjustment"}
        if required_scores.difference(scores.columns) or required_bars.difference(
            label_fill_bars.columns
        ):
            raise PaperError("scores or label_fill_bars missing required columns")
        adjustments = set(label_fill_bars["adjustment"].dropna().astype(str))
        if not label_fill_bars.empty and (
            adjustments != {"all"} or label_fill_bars["adjustment"].isna().any()
        ):
            raise PaperError(
                f"label_fill_bars must contain only adjustment=all; observed={sorted(adjustments)}"
            )
        if self.events or self.positions or self.pending is not None:
            raise PaperError("PaperLedger instances are single-use")
        self._run_id = run_id
        self._data_manifest_hash = data_manifest_hash
        self._model_artifact_hash = model_artifact_hash
        self._feature_schema_hash = feature_schema_hash
        cal = calendar or XNYSCalendar()
        score_data = scores.copy()
        score_data["decision_at"] = pd.to_datetime(score_data["decision_at"], utc=True)
        score_data["score"] = pd.to_numeric(score_data["score"], errors="coerce")
        bars = label_fill_bars.copy()
        bars["bar_end_at"] = pd.to_datetime(bars["bar_end_at"], utc=True)
        if score_data.empty:
            summary = {
                "initial_nav": self.config.initial_nav,
                "final_nav": self.config.initial_nav,
                "final_gross_nav": self.config.initial_nav,
                "failed": False,
                "event_count": 0,
                "rebalances": 0,
            }
            return ReplayResult([], summary)
        decision_dates = sorted(score_data["decision_at"].drop_duplicates())
        start = min(decision_dates).date()
        end = max(decision_dates).date()
        final_exit_date = cal.sessions_after(end, 5)[-1].session_date
        sessions = cal.sessions(start, final_exit_date)
        week_start = start - timedelta(days=start.weekday())
        week_end = end + timedelta(days=6 - end.weekday())
        scheduled_decisions = {
            pd.Timestamp(session.close_at) for session in cal.weekly_decisions(week_start, week_end)
        }
        invalid_decisions = [
            timestamp for timestamp in decision_dates if timestamp not in scheduled_decisions
        ]
        if invalid_decisions:
            raise PaperError(
                f"decision_at must equal a scheduled weekly XNYS close: {invalid_decisions}"
            )
        decision_map = {
            pd.Timestamp(timestamp): group
            for timestamp, group in score_data.groupby("decision_at", sort=True)
        }
        for session in sessions:
            if self.failed:
                break
            if self.pending is not None and self.pending[0] == session.session_date:
                self._fill_entries(
                    session,
                    bars,
                    self.pending[1],
                    self.pending[2],
                    self.pending[3],
                    self.pending[4],
                )
            if self.failed:
                break
            if (
                self.positions
                and next(iter(self.positions.values())).exit_date == session.session_date
            ):
                self._fill_exits(session, bars)
            if self.failed:
                break
            close_prices = _prices_for_session(
                bars, tuple(sorted(self.positions)), session.session_date, "close"
            )
            if self.positions and set(close_prices) != set(self.positions):
                decision_at = next(iter(self.positions.values())).decision_at
                self._fail(
                    session.close_at,
                    "missing_mark_bar",
                    "restore every held-symbol label_fill_stream close bar",
                    decision_at=decision_at,
                    feature_cutoff_at=decision_at,
                    missing_symbols=sorted(set(self.positions).difference(close_prices)),
                )
                break
            net_nav, gross_nav, exposure = self._nav(close_prices)
            active_decision_at = (
                next(iter(self.positions.values())).decision_at if self.positions else None
            )
            self._event(
                "mark",
                session.close_at,
                decision_at=active_decision_at,
                feature_cutoff_at=active_decision_at,
                cash=self.cash,
                gross_cash=self.gross_cash,
                nav=net_nav,
                net_nav=net_nav,
                gross_nav=gross_nav,
                gross_exposure=exposure,
            )
            group = decision_map.get(pd.Timestamp(session.close_at))
            if group is None:
                continue
            normalized = group["symbol"].astype(str).str.upper()
            observed = set(normalized)
            expected = set(symbols)
            missing_scores = sorted(expected.difference(observed))
            extra_scores = sorted(observed.difference(expected))
            duplicate_scores = sorted(normalized[normalized.duplicated()].unique())
            if (
                missing_scores
                or extra_scores
                or duplicate_scores
                or not np.isfinite(group["score"]).all()
            ):
                self._event(
                    "skip",
                    session.close_at,
                    decision_at=session.close_at.isoformat(),
                    feature_cutoff_at=session.close_at.isoformat(),
                    decision_event_at=session.close_at.isoformat(),
                    reason="decision_missing_symbol_or_score",
                    missing_symbols=missing_scores,
                    extra_symbols=extra_scores,
                    duplicate_symbols=duplicate_scores,
                )
                continue
            target_session = cal.sessions_after(session.session_date, 1)[0]
            exit_date = cal.sessions_after(session.session_date, 5)[-1].session_date
            if (
                self.positions
                and target_session.session_date <= next(iter(self.positions.values())).exit_date
            ):
                self._event(
                    "skip",
                    session.close_at,
                    decision_at=session.close_at.isoformat(),
                    feature_cutoff_at=session.close_at.isoformat(),
                    decision_event_at=session.close_at.isoformat(),
                    reason="calendar_overlap",
                    entry_at=target_session.open_at.isoformat(),
                )
                continue
            ranked = group.assign(symbol=normalized).sort_values(
                ["score", "symbol"], ascending=[False, True]
            )
            selected_frame = ranked.head(self.config.top_n)
            if len(selected_frame) != self.config.top_n:
                self._event(
                    "skip",
                    session.close_at,
                    decision_at=session.close_at.isoformat(),
                    feature_cutoff_at=session.close_at.isoformat(),
                    decision_event_at=session.close_at.isoformat(),
                    reason="insufficient_symbols",
                )
                continue
            selected = tuple(
                (str(row.symbol), float(row.score), rank)
                for rank, row in enumerate(selected_frame.itertuples(index=False), start=1)
            )
            decision_at = session.close_at.isoformat()
            self.pending = (target_session.session_date, selected, symbols, exit_date, decision_at)
            self._event(
                "decision",
                session.close_at,
                decision_at=decision_at,
                feature_cutoff_at=decision_at,
                decision_event_at=decision_at,
                selected_symbols=[symbol for symbol, _, _ in selected],
                entry_at=target_session.open_at.isoformat(),
            )
        final_close = (
            self.events[-1].get("event_at") if self.events else pd.Timestamp.utcnow().isoformat()
        )
        marks = [event for event in self.events if event["event_type"] == "mark"]
        final_nav = float(marks[-1]["net_nav"]) if marks else self.config.initial_nav
        final_gross_nav = float(marks[-1]["gross_nav"]) if marks else self.config.initial_nav
        costs = [event for event in self.events if event["event_type"] in {"fill", "exit"}]
        skip_counts = {
            reason: sum(
                event["event_type"] == "skip" and event.get("reason") == reason
                for event in self.events
            )
            for reason in sorted(
                {str(event.get("reason")) for event in self.events if event["event_type"] == "skip"}
            )
        }
        summary = {
            "initial_nav": self.config.initial_nav,
            "final_nav": final_nav,
            "final_gross_nav": final_gross_nav,
            "cost_drag": (final_gross_nav - final_nav) / self.config.initial_nav,
            "fee_total": sum(float(event.get("fee", 0.0)) for event in costs),
            "slippage_total": sum(float(event.get("slippage", 0.0)) for event in costs),
            "failed": self.failed,
            "event_count": len(self.events),
            "rebalances": len(
                {event["event_at"] for event in self.events if event["event_type"] == "fill"}
            ),
            "skip_counts": skip_counts,
            "final_event_at": final_close,
        }
        return ReplayResult(self.events, summary, self.failed)


def _prices_for_session(
    bars: pd.DataFrame, symbols: tuple[str, ...], session_date: date, field: str
) -> dict[str, float]:
    if not symbols:
        return {}
    frame = bars[bars["symbol"].astype(str).str.upper().isin(symbols)].copy()
    frame["bar_date"] = frame["bar_end_at"].dt.date
    frame = frame[frame["bar_date"].eq(session_date)]
    if frame.empty:
        return {}
    if frame.duplicated(["symbol", "bar_date"]).any():
        raise PaperError("duplicate label_fill_stream bar")
    return {
        str(row["symbol"]).upper(): float(row[field])
        for _, row in frame.iterrows()
        if pd.notna(row[field]) and math.isfinite(float(row[field])) and float(row[field]) > 0
    }


def simulate_paper(
    scores: pd.DataFrame,
    label_fill_bars: pd.DataFrame,
    *,
    symbols: tuple[str, ...],
    config: PaperConfig | None = None,
    calendar: XNYSCalendar | None = None,
) -> ReplayResult:
    return PaperLedger(config or PaperConfig()).replay(
        scores, label_fill_bars, symbols=symbols, calendar=calendar
    )
