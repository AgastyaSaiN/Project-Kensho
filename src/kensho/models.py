"""Domain models and timer logic for Kenshō."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Dict, List, Tuple

SECONDS_PER_MINUTE = 60
MAX_HISTORY_DAYS = 30


def _today_string() -> str:
    return date.today().isoformat()


@dataclass
class ClockUnit:
    """Represents a single mindful clock."""

    identifier: str
    label: str
    interval_minutes: int
    sound_id: str = "tone"
    elapsed_seconds: float = 0.0
    paused: bool = False
    check_ins_today: int = 0
    last_check_in_date: str = field(default_factory=_today_string)
    due: bool = False
    expanded: bool = False
    history: Dict[str, int] = field(default_factory=dict)
    history_window: int = 5

    def tick(self, seconds: float = 1.0) -> bool:
        """Advance the timer. Return True when the interval completes."""
        self.ensure_today()

        if self.paused:
            return False

        self.elapsed_seconds += seconds
        interval_seconds = self.interval_minutes * SECONDS_PER_MINUTE

        if self.elapsed_seconds >= interval_seconds > 0:
            self.elapsed_seconds = interval_seconds
            self.due = True
            return True
        return False

    def reset(self) -> None:
        """Reset elapsed time and record a check-in."""
        self.ensure_today()
        self.elapsed_seconds = 0.0
        self.paused = False
        self.due = False
        today = _today_string()
        self.check_ins_today += 1
        self.history[today] = self.check_ins_today
        self._prune_history()

    def toggle_pause(self) -> None:
        self.paused = not self.paused

    def remaining_seconds(self) -> float:
        interval_seconds = self.interval_minutes * SECONDS_PER_MINUTE
        return max(interval_seconds - self.elapsed_seconds, 0.0)

    def progress_ratio(self) -> float:
        interval_seconds = self.interval_minutes * SECONDS_PER_MINUTE
        if interval_seconds <= 0:
            return 0.0
        ratio = self.elapsed_seconds / interval_seconds
        return max(0.0, min(ratio, 1.0))

    def ensure_today(self) -> None:
        """Roll counters forward when a new day begins."""
        today = _today_string()
        if self.last_check_in_date != today:
            # Preserve the stored value for the last recorded day.
            if self.last_check_in_date:
                prev_date = self.last_check_in_date
                if self.check_ins_today:
                    stored = self.history.get(prev_date, 0)
                    self.history[prev_date] = max(stored, self.check_ins_today)
            self.last_check_in_date = today
            self.check_ins_today = self.history.get(today, 0)
        self.history.setdefault(today, self.check_ins_today)
        self._prune_history()

    def recent_history(self, days: int | None = None) -> List[Tuple[str, int]]:
        """Return up to `days` entries (inclusive of today) for display."""
        self.ensure_today()
        days = int(days or self.history_window or 5)
        days = max(1, min(days, MAX_HISTORY_DAYS))

        today = date.today()
        records: List[Tuple[str, int]] = []
        for offset in range(days - 1, -1, -1):
            day = today - timedelta(days=offset)
            label = day.strftime("%a")
            count = self.history.get(day.isoformat(), 0)
            records.append((label, count))
        return records

    def _prune_history(self) -> None:
        if len(self.history) <= MAX_HISTORY_DAYS:
            return
        cutoff = date.today() - timedelta(days=MAX_HISTORY_DAYS - 1)
        cutoff_str = cutoff.isoformat()
        keys_to_remove = [key for key in self.history if key < cutoff_str]
        for key in keys_to_remove:
            del self.history[key]

    def set_history_window(self, window: int) -> None:
        self.history_window = self._normalize_history_window(window)

    def history_records(self) -> List[Tuple[str, int]]:
        """Return all recorded days as (iso_date, count) sorted ascending."""
        self.ensure_today()
        return sorted(self.history.items())

    def serialize(self) -> Dict[str, object]:
        return {
            "identifier": self.identifier,
            "label": self.label,
            "interval_minutes": self.interval_minutes,
            "sound_id": self.sound_id,
            "elapsed_seconds": round(float(self.elapsed_seconds), 3),
            "paused": self.paused,
            "check_ins_today": self.check_ins_today,
            "last_check_in_date": self.last_check_in_date,
            "due": self.due,
            "expanded": self.expanded,
            "history": self.history,
            "history_window": self.history_window,
        }

    @classmethod
    def from_dict(cls, payload: Dict[str, object]) -> "ClockUnit":
        return cls(
            identifier=str(payload.get("identifier", "")),
            label=str(payload.get("label", "Mindful Clock")),
            interval_minutes=int(payload.get("interval_minutes", 10)),
            sound_id=str(payload.get("sound_id", "tone")),
            elapsed_seconds=float(payload.get("elapsed_seconds", 0.0)),
            paused=bool(payload.get("paused", False)),
            check_ins_today=int(payload.get("check_ins_today", 0)),
            last_check_in_date=str(
                payload.get("last_check_in_date", _today_string())
            ),
            due=bool(payload.get("due", False)),
            expanded=bool(payload.get("expanded", False)),
            history={
                str(key): int(value)
                for key, value in dict(payload.get("history", {})).items()
            },
            history_window=int(payload.get("history_window", 5)),
        )

    def __post_init__(self) -> None:
        # If history is empty but a previous day count exists, seed it.
        if not self.history and self.check_ins_today:
            self.history[self.last_check_in_date] = self.check_ins_today
        self.history_window = self._normalize_history_window(self.history_window)
        self.ensure_today()

    @staticmethod
    def _normalize_history_window(window: int) -> int:
        if window in (5, 7, 14):
            return window
        window = max(1, min(window, MAX_HISTORY_DAYS))
        if window in (5, 7, 14):
            return window
        return 5


__all__ = ["ClockUnit", "SECONDS_PER_MINUTE"]
