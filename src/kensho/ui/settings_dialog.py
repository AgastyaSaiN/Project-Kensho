"""Dialog for editing a clock's interval and sound."""

from __future__ import annotations

import tkinter as tk
from typing import Callable, Dict

SOUNDS = [
    ("Soft Chime", "chime"),
    ("Metronome", "metronome"),
]


class ClockSettingsDialog:
    """Simple modal dialog to adjust clock properties."""

    def __init__(
        self,
        master: tk.Misc,
        *,
        initial_minutes: int,
        initial_sound: str,
        on_apply: Callable[[int, str], None],
        on_close: Callable[[], None],
        allow_delete: bool,
        on_delete: Callable[[], None] | None = None,
    ) -> None:
        self.master = master
        self.on_apply = on_apply
        self._on_close = on_close
        self._on_delete = on_delete if allow_delete else None

        self.window = tk.Toplevel(master)
        self.window.title("Clock Settings")
        self.window.configure(bg="#f6f5f3")
        self.window.resizable(False, False)
        self.window.transient(master)
        self.window.grab_set()

        self.window.protocol("WM_DELETE_WINDOW", self.close)

        body = tk.Frame(self.window, bg="#f6f5f3", padx=18, pady=18)
        body.pack(fill="both", expand=True)

        font_label = ("Segoe UI", 10)
        font_input = ("Segoe UI", 10)

        minutes_label = tk.Label(
            body,
            text="Interval (minutes)",
            bg="#f6f5f3",
            fg="#374151",
            font=font_label,
        )
        minutes_label.grid(row=0, column=0, sticky="w")

        self.minutes_var = tk.IntVar(value=max(initial_minutes, 1))
        self.minutes_spin = tk.Spinbox(
            body,
            from_=1,
            to=240,
            textvariable=self.minutes_var,
            increment=1,
            width=5,
            justify="center",
            font=font_input,
        )
        self.minutes_spin.grid(row=0, column=1, sticky="e", padx=(12, 0))

        sound_label = tk.Label(
            body,
            text="Sound",
            bg="#f6f5f3",
            fg="#374151",
            font=font_label,
        )
        sound_label.grid(row=1, column=0, pady=(12, 0), sticky="w")

        self.sound_map: Dict[str, str] = {label: value for label, value in SOUNDS}
        initial_label = next(
            (label for label, value in SOUNDS if value == initial_sound),
            SOUNDS[0][0],
        )
        self.sound_var = tk.StringVar(value=initial_label)
        self.sound_menu = tk.OptionMenu(
            body, self.sound_var, *self.sound_map.keys()
        )
        self.sound_menu.configure(
            font=font_input,
            highlightthickness=0,
            bg="#ffffff",
            fg="#1f2933",
            relief="flat",
        )
        self.sound_menu.grid(row=1, column=1, pady=(12, 0), sticky="e")
        menu = self.sound_menu["menu"]
        menu.configure(font=font_input)

        actions = tk.Frame(self.window, bg="#f6f5f3", pady=12)
        actions.pack(fill="x")

        if self._on_delete is not None:
            delete_btn = tk.Button(
                actions,
                text="Delete",
                command=self._handle_delete,
                width=10,
                bg="#fee2e2",
                fg="#b91c1c",
                relief="flat",
                activebackground="#fecaca",
            )
            delete_btn.pack(side="left", padx=(10, 0))

        cancel_btn = tk.Button(
            actions,
            text="Cancel",
            command=self.close,
            width=10,
            bg="#ffffff",
            fg="#4b5563",
            relief="groove",
        )
        cancel_btn.pack(side="right", padx=(0, 10))

        apply_btn = tk.Button(
            actions,
            text="Apply",
            command=self._apply,
            width=10,
            bg="#4e7bff",
            fg="#ffffff",
            activebackground="#2e53d6",
        )
        apply_btn.pack(side="right", padx=(0, 10))

        self.minutes_spin.focus_set()

    def _apply(self) -> None:
        try:
            minutes = int(self.minutes_spin.get())
        except (ValueError, tk.TclError):
            minutes = 1
        minutes = max(minutes, 1)
        sound = self.sound_map.get(self.sound_var.get(), "chime")
        self.on_apply(minutes, sound)
        self.close()

    def _handle_delete(self) -> None:
        if self._on_delete is None:
            return
        self._on_delete()

    def close(self) -> None:
        self.window.grab_release()
        self.window.destroy()
        self._on_close()


__all__ = ["ClockSettingsDialog", "SOUNDS"]
