"""Platform-specific notification helpers."""

from __future__ import annotations

import threading
from typing import Optional

try:
    from win10toast import ToastNotifier
except Exception:  # pragma: no cover - fallback for non-Windows dev
    ToastNotifier = None

try:
    import winsound
except Exception:  # pragma: no cover - winsound is Windows-only
    winsound = None

_toast_instance: Optional["ToastNotifier"] = None
_toast_lock = threading.Lock()


def _get_toast() -> Optional["ToastNotifier"]:
    global _toast_instance
    if ToastNotifier is None:
        return None
    with _toast_lock:
        if _toast_instance is None:
            _toast_instance = ToastNotifier()
    return _toast_instance


def play_sound(sound_id: str) -> None:
    """Play a short notification tone."""
    if winsound is None:
        return

    if sound_id == "metronome":
        winsound.Beep(880, 150)
        winsound.Beep(660, 150)
    else:
        # Default to a single soft chime.
        winsound.Beep(880, 300)


def show_toast(title: str, message: str) -> None:
    notifier = _get_toast()
    if notifier is None:
        return
    notifier.show_toast(title, message, duration=3, threaded=True)


def notify_clock_due(clock_label: str, sound_id: str) -> None:
    """Send a combined toast + sound notification when a clock completes."""
    play_sound(sound_id)
    show_toast("Kenshō", f"{clock_label} is ready for a check-in.")


__all__ = ["notify_clock_due", "play_sound", "show_toast"]
