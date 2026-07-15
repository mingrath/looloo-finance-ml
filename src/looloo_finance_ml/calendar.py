"""Frozen XNYS session handling with timezone-aware timestamps."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pandas as pd

XNYS = "XNYS"
SOURCE_TZ = ZoneInfo("America/New_York")
UTC = timezone.utc


@dataclass(frozen=True)
class Session:
    session_date: date
    open_at: datetime
    close_at: datetime


class CalendarError(ValueError):
    """Raised when a requested session cannot be resolved."""


class XNYSCalendar:
    """Adapter around exchange_calendars 4.13.2's XNYS schedule."""

    def __init__(self) -> None:
        import exchange_calendars as xcals

        self._calendar = xcals.get_calendar(XNYS)

    @staticmethod
    def _aware(value: object) -> datetime:
        timestamp = pd.Timestamp(value)
        if timestamp.tzinfo is None:
            timestamp = timestamp.tz_localize("UTC")
        return timestamp.to_pydatetime().astimezone(UTC)

    def sessions(self, start: date | str, end: date | str) -> tuple[Session, ...]:
        start_ts = pd.Timestamp(start).normalize()
        end_ts = pd.Timestamp(end).normalize()
        schedule = self._calendar.schedule.loc[str(start_ts.date()) : str(end_ts.date())]
        result = []
        for index, row in schedule.iterrows():
            session_date = pd.Timestamp(index).date()
            result.append(
                Session(
                    session_date=session_date,
                    open_at=self._aware(row["open"]),
                    close_at=self._aware(row["close"]),
                )
            )
        return tuple(result)

    def session(self, session_date: date | str) -> Session:
        sessions = self.sessions(session_date, session_date)
        if len(sessions) != 1:
            raise CalendarError(f"{session_date} is not an XNYS session")
        return sessions[0]

    def next_session(self, session_date: date | str) -> Session:
        target = pd.Timestamp(session_date).date()
        start = target + timedelta(days=1)
        end = start + timedelta(days=14)
        sessions = self.sessions(start, end)
        if not sessions:
            raise CalendarError(f"no XNYS session after {target}")
        return sessions[0]

    def sessions_after(self, session_date: date | str, count: int) -> tuple[Session, ...]:
        if count < 1:
            return ()
        target = pd.Timestamp(session_date).date()
        return self.sessions(target + timedelta(days=1), target + timedelta(days=30 * (count + 1)))[
            :count
        ]

    def weekly_decisions(self, start: date | str, end: date | str) -> tuple[Session, ...]:
        sessions = self.sessions(start, end)
        by_week: dict[tuple[int, int], Session] = {}
        for session in sessions:
            iso = session.session_date.isocalendar()
            by_week[(iso.year, iso.week)] = session
        return tuple(by_week[key] for key in sorted(by_week))

    @staticmethod
    def is_early_close(session: Session) -> bool:
        normal_close = session.close_at.astimezone(SOURCE_TZ).replace(
            hour=16, minute=0, second=0, microsecond=0
        )
        return session.close_at.astimezone(SOURCE_TZ) != normal_close
