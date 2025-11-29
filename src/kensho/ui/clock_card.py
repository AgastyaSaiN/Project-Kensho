"""Tkinter widget representing a single clock card."""

from __future__ import annotations

import math
import tkinter as tk
from typing import Callable

from ..models import ClockUnit

CARD_BG = "#fdfcf9"
SURFACE_BG = "#eceff4"
ACCENT_BLUE = "#4e7bff"
ACCENT_BLUE_DUE = "#2a4fd9"
TEXT_PRIMARY = "#1f2933"
TEXT_SECONDARY = "#6b7280"
PILL_BG = "#e4e8ef"
PILL_TEXT = "#4a5568"
TREND_BAR = "#c8d6ff"
TREND_BG = "#f6f7fb"
CANVAS_SIZE = 112
RING_THICKNESS = 8
MIN_SCALE = 0.5
MAX_SCALE = 1.2
BASE_CARD_WIDTH = CANVAS_SIZE + 96
CARD_BORDER = "#d9dde2"
BASE_CARD_HEIGHT = CANVAS_SIZE + 200


class ClockCard(tk.Frame):
    """Encapsulates the circular timer UI and controls."""

    BASE_WIDTH = BASE_CARD_WIDTH
    BASE_HEIGHT = BASE_CARD_HEIGHT
    MIN_SCALE = MIN_SCALE
    MAX_SCALE = MAX_SCALE

    def __init__(
        self,
        master: tk.Misc,
        clock: ClockUnit,
        *,
        on_check_in: Callable[[ClockUnit], None],
        on_toggle_pause: Callable[[ClockUnit], None],
        on_label_change: Callable[[ClockUnit, str], None],
        on_toggle_expand: Callable[[ClockUnit, "ClockCard"], None],
        on_share: Callable[[ClockUnit], None],
        on_history_window_change: Callable[[ClockUnit, "ClockCard", int], None],
        on_open_settings: Callable[[ClockUnit, "ClockCard"], None],
        identifier_label: str,
    ) -> None:
        super().__init__(master, bg=SURFACE_BG)
        self.clock = clock
        self._on_check_in = on_check_in
        self._on_toggle_pause = on_toggle_pause
        self._on_label_change = on_label_change
        self._on_toggle_expand = on_toggle_expand
        self._on_share = on_share
        self._on_history_window_change = on_history_window_change
        self._on_open_settings = on_open_settings

        self.card = tk.Frame(
            self,
            bg=CARD_BG,
            bd=0,
            relief="flat",
            highlightthickness=1,
            highlightbackground=CARD_BORDER,
            highlightcolor=CARD_BORDER,
        )
        self.card.pack(padx=4, pady=4, fill="both", expand=True)

        self.header = tk.Frame(self.card, bg=CARD_BG)
        self.header.pack(fill="x", pady=(4, 0), padx=8)

        self.identifier_label = tk.Label(
            self.header,
            text=identifier_label,
            bg=CARD_BG,
            fg=TEXT_SECONDARY,
            font=("Segoe UI", 9, "bold"),
        )
        self.identifier_label.pack(side="left")

        self.header_icons = tk.Frame(self.header, bg=CARD_BG)
        self.header_icons.pack(side="right")

        self.expand_btn = tk.Label(
            self.header_icons,
            text=self._expand_icon(),
            bg=CARD_BG,
            fg=TEXT_SECONDARY,
            font=("Segoe UI Symbol", 9),
            cursor="hand2",
        )
        self.expand_btn.pack(side="left", padx=(0, 4))
        self.expand_btn.bind("<Button-1>", self._handle_expand)
        self._bind_hover(
            self.expand_btn,
            lambda: self.expand_btn.configure(fg=ACCENT_BLUE),
            lambda: self.expand_btn.configure(fg=TEXT_SECONDARY),
        )

        self.settings_btn = tk.Label(
            self.header_icons,
            text="⚙",
            bg=CARD_BG,
            fg=TEXT_SECONDARY,
            font=("Segoe UI Symbol", 9),
            cursor="hand2",
        )
        self.settings_btn.pack(side="left")
        self.settings_btn.bind("<Button-1>", self._handle_settings)
        self._bind_hover(
            self.settings_btn,
            lambda: self.settings_btn.configure(fg=ACCENT_BLUE),
            lambda: self.settings_btn.configure(fg=TEXT_SECONDARY),
        )

        self.ring_canvas = tk.Canvas(
            self.card,
            width=CANVAS_SIZE,
            height=CANVAS_SIZE,
            bg=CARD_BG,
            highlightthickness=0,
            bd=0,
        )
        self.ring_canvas.pack(padx=8, pady=(6, 4))

        padding = RING_THICKNESS + 6
        self._ring_bounds = (
            padding,
            padding,
            CANVAS_SIZE - padding,
            CANVAS_SIZE - padding,
        )
        self.base_circle = self.ring_canvas.create_oval(
            *self._ring_bounds,
            outline="#d9dde2",
            width=RING_THICKNESS,
        )
        self.progress_arc = self.ring_canvas.create_arc(
            *self._ring_bounds,
            start=90,
            extent=0,
            style="arc",
            outline=ACCENT_BLUE,
            width=RING_THICKNESS,
        )

        self.task_var = tk.StringVar(value=self.clock.label)
        self.task_entry = tk.Entry(
            self.card,
            textvariable=self.task_var,
            justify="center",
            bd=0,
            highlightthickness=0,
            font=("Segoe UI", 12, "bold"),
            fg=TEXT_PRIMARY,
            bg=CARD_BG,
            insertbackground=ACCENT_BLUE,
        )

        self.entry_window = self.ring_canvas.create_window(
            CANVAS_SIZE / 2,
            CANVAS_SIZE / 2 - 4,
            window=self.task_entry,
            width=CANVAS_SIZE - 40,
        )

        self.task_entry.bind("<FocusOut>", self._handle_task_update)
        self.task_entry.bind("<Return>", self._handle_task_update)

        self.interval_label = tk.Label(
            self.card,
            text=self._interval_text(),
            font=("Segoe UI", 9),
            bg=CARD_BG,
            fg=PILL_TEXT,
            padx=10,
            pady=4,
        )
        self.interval_label.pack(pady=(0, 8))
        self.interval_label.configure(
            relief="flat", bd=0, highlightthickness=0
        )
        self.interval_label.bind("<Configure>", self._round_interval_bg)

        self.countdown_label = tk.Label(
            self.card,
            text=self._next_ping_text(),
            font=("Segoe UI", 10),
            bg=CARD_BG,
            fg=TEXT_SECONDARY,
            wraplength=CANVAS_SIZE + 60,
            justify="center",
        )
        self.countdown_label.pack(pady=(0, 6))

        self.controls = tk.Frame(self.card, bg=CARD_BG)
        self.controls.pack(pady=(0, 8))

        self.pause_button = tk.Button(
            self.controls,
            text=self._pause_icon(),
            font=("Segoe UI", 10, "bold"),
            width=7,
            relief="flat",
            bg=ACCENT_BLUE,
            fg="#ffffff",
            activebackground=ACCENT_BLUE_DUE,
            activeforeground="#ffffff",
            command=self._handle_pause,
            cursor="hand2",
        )
        self.pause_button.pack(side="left", padx=6)

        self.check_button = tk.Button(
            self.controls,
            text="Check-in",
            font=("Segoe UI", 10),
            width=8,
            relief="groove",
            bg="#ffffff",
            fg=TEXT_SECONDARY,
            activebackground="#edf2ff",
            activeforeground=ACCENT_BLUE,
            command=self._handle_check_in,
            cursor="hand2",
        )
        self.check_button.pack(side="left", padx=6)
        self._bind_hover(
            self.pause_button,
            lambda: self.pause_button.configure(bg=ACCENT_BLUE_DUE),
            lambda: self.pause_button.configure(bg=ACCENT_BLUE),
        )
        self._bind_hover(
            self.check_button,
            lambda: self.check_button.configure(bg="#e5edff", fg=ACCENT_BLUE),
            self._apply_check_base_state,
        )

        self.detail_frame = tk.Frame(self.card, bg=TREND_BG, bd=0, padx=10, pady=10)
        self.summary_label = tk.Label(
            self.detail_frame,
            text=self._detail_text(),
            bg=TREND_BG,
            fg=TEXT_SECONDARY,
            font=("Segoe UI", 8),
            justify="center",
            wraplength=CANVAS_SIZE - 20,
        )
        self.summary_label.pack(fill="x")

        self.trend_canvas = tk.Canvas(
            self.detail_frame,
            width=CANVAS_SIZE - 16,
            height=44,
            bg=TREND_BG,
            highlightthickness=0,
            bd=0,
        )
        self.trend_canvas.pack(pady=(10, 6))

        self.trend_caption = tk.Label(
            self.detail_frame,
            text="Past 5 days",
            bg=TREND_BG,
            fg=TEXT_SECONDARY,
            font=("Segoe UI", 7),
        )
        self.trend_caption.pack()

        self.history_controls = tk.Frame(self.detail_frame, bg=TREND_BG)
        self.history_controls.pack(fill="x", pady=(8, 0))

        self.history_var = tk.IntVar(value=self.clock.history_window or 5)
        self.history_buttons: dict[int, tk.Button] = {}
        for window in (5, 7, 14):
            btn = tk.Button(
                self.history_controls,
                text=f"{window}d",
                command=lambda value=window: self._handle_history_change(value),
                bg="#ffffff",
                fg=TEXT_SECONDARY,
                font=("Segoe UI", 9),
                relief="flat",
                bd=0,
                padx=8,
                pady=3,
                cursor="hand2",
                activebackground="#e5edff",
                activeforeground=ACCENT_BLUE,
            )
            btn.pack(side="left", padx=2, expand=True, fill="x")
            self.history_buttons[window] = btn
            self._bind_hover(
                btn,
                lambda b=btn: b.configure(bg="#e5edff", fg=ACCENT_BLUE),
                lambda b=btn, w=window: (
                    self._style_history_button(w)
                    if self.history_var.get() != w
                    else None
                ),
            )
        self._update_trend_caption()
        self._refresh_history_buttons()

        self.export_button = tk.Button(
            self.detail_frame,
            text="Share",
            bg="#ffffff",
            fg=TEXT_SECONDARY,
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            bd=0,
            padx=10,
            pady=4,
            cursor="hand2",
            command=self._handle_share,
        )
        self.export_button.pack(pady=(8, 0), fill="x")
        self._bind_hover(
            self.export_button,
            lambda: self.export_button.configure(bg="#e5edff", fg=ACCENT_BLUE),
            lambda: self.export_button.configure(bg="#ffffff", fg=TEXT_SECONDARY),
        )

        if self.clock.expanded:
            self._show_details()
        else:
            self._hide_details()

        self._is_due = False
        self._display_ratio = self.clock.progress_ratio()
        self.update_scale(1.0)
        self._apply_check_base_state()
        self.update_progress()

    def _round_interval_bg(self, event: tk.Event) -> None:
        """Apply a round-rectangle background effect via Canvas."""
        # Labels do not support rounded corners natively; we emulate it by
        # drawing a rounded rectangle behind the widget.
        label = event.widget
        if getattr(label, "_rounded_bg", None):
            return

        width = label.winfo_reqwidth()
        height = label.winfo_reqheight()
        radius = min(height // 2, 14)

        canvas = tk.Canvas(
            label.master,
            width=width,
            height=height,
            bg=CARD_BG,
            highlightthickness=0,
            bd=0,
        )
        canvas.place(in_=label, x=0, y=0, relwidth=1, relheight=1)

        x1, y1, x2, y2 = 1, 1, width - 1, height - 1
        r = radius
        canvas.create_arc(x1, y1, x1 + 2 * r, y1 + 2 * r, start=90, extent=90, fill=PILL_BG, outline=PILL_BG)
        canvas.create_arc(x2 - 2 * r, y1, x2, y1 + 2 * r, start=0, extent=90, fill=PILL_BG, outline=PILL_BG)
        canvas.create_arc(x1, y2 - 2 * r, x1 + 2 * r, y2, start=180, extent=90, fill=PILL_BG, outline=PILL_BG)
        canvas.create_arc(x2 - 2 * r, y2 - 2 * r, x2, y2, start=270, extent=90, fill=PILL_BG, outline=PILL_BG)
        canvas.create_rectangle(x1 + r, y1, x2 - r, y2, fill=PILL_BG, outline=PILL_BG)
        canvas.create_rectangle(x1, y1 + r, x2, y2 - r, fill=PILL_BG, outline=PILL_BG)
        label.tkraise()
        label._rounded_bg = canvas  # type: ignore[attr-defined]

    def _pause_icon(self) -> str:
        return "Resume" if self.clock.paused else "Pause"

    def _expand_icon(self) -> str:
        return "⌄" if self.clock.expanded else "⤢"

    def _interval_text(self) -> str:
        minutes = self.clock.interval_minutes
        unit = "min" if minutes == 1 else "min"
        if self.clock.due:
            status = "Ready now"
            prefix = "⚡"
        elif self.clock.paused:
            status = "Paused"
            prefix = "⏸"
        else:
            status = "Running"
            prefix = "🔁"
        return f"{prefix} Every {minutes} {unit} • {status}"

    def _next_ping_text(self) -> str:
        if self.clock.due:
            return "Awaiting your check-in"
        if self.clock.paused:
            return "Paused — resume to continue"
        remaining = max(self.clock.remaining_seconds(), 0.0)
        if remaining <= 0:
            return "Next reminder momentarily"
        remaining_int = max(int(math.ceil(remaining)), 0)
        minutes, seconds = divmod(remaining_int, 60)
        if minutes >= 1:
            return f"Next reminder in {minutes}m {seconds:02d}s"
        return f"Next reminder in {seconds}s"

    def _detail_text(self) -> str:
        count = self.clock.check_ins_today
        suffix = "check-ins today" if count != 1 else "check-in today"
        next_ping = self._next_ping_text()
        return f"{count} {suffix}\n{next_ping}"

    def _handle_task_update(self, event: tk.Event) -> str | None:
        new_label = self.task_var.get().strip() or "Mindful Session"
        self.task_var.set(new_label)
        self.clock.label = new_label
        self._on_label_change(self.clock, new_label)
        # Prevent newline insertion on Return.
        if getattr(event, "keysym", None) == "Return":
            self.task_entry.icursor("end")
            self.task_entry.selection_clear()
            self.task_entry.master.focus_set()
            return "break"

    def _handle_pause(self) -> None:
        self._on_toggle_pause(self.clock)

    def _handle_check_in(self) -> None:
        self._on_check_in(self.clock)

    def _handle_settings(self, _event: tk.Event) -> None:
        self._on_open_settings(self.clock, self)

    def _handle_expand(self, _event: tk.Event) -> None:
        self._on_toggle_expand(self.clock, self)

    def _handle_history_change(self, selection: object) -> None:
        try:
            value = int(selection)
        except (TypeError, ValueError):
            value = self.history_var.get()
        self.history_var.set(value)
        self._on_history_window_change(self.clock, self, value)
        self._update_trend_caption()
        self._draw_trend()
        self._refresh_history_buttons()

    def _handle_share(self) -> None:
        self._on_share(self.clock)

    def update_scale(self, scale: float) -> None:
        scale = max(MIN_SCALE, min(MAX_SCALE, scale))
        previous = getattr(self, "_scale", None)
        if previous is not None and abs(previous - scale) < 0.02:
            return
        self._scale = scale

        size = max(76, int(CANVAS_SIZE * scale))
        ring = max(4, int(RING_THICKNESS * scale))
        padding = ring + int(4 * scale)
        bounds = (
            padding,
            padding,
            size - padding,
            size - padding,
        )
        self._ring_bounds = bounds
        self.ring_canvas.config(width=size, height=size)
        self.ring_canvas.coords(self.base_circle, *bounds)
        self.ring_canvas.coords(self.progress_arc, *bounds)
        self.ring_canvas.itemconfigure(self.base_circle, width=ring)
        self.ring_canvas.itemconfigure(self.progress_arc, width=ring)
        self.ring_canvas.pack_configure(
            padx=max(4, int(6 * scale)), pady=(max(2, int(3 * scale)), max(2, int(3 * scale)))
        )
        self.ring_canvas.coords(
            self.entry_window,
            size / 2,
            size / 2 - 3 * scale,
        )
        self.ring_canvas.itemconfigure(
            self.entry_window,
            width=max(40, size - int(24 * scale)),
        )

        header_font = max(7, int(9 * scale))
        icon_font = max(7, int(9 * scale))
        self.identifier_label.configure(font=("Segoe UI", header_font, "bold"))
        self.expand_btn.configure(font=("Segoe UI Symbol", icon_font))
        self.settings_btn.configure(font=("Segoe UI Symbol", icon_font))
        self.header.pack_configure(
            padx=max(6, int(6 * scale)), pady=(max(3, int(3 * scale)), 0)
        )

        task_font = max(9, int(12 * scale))
        self.task_entry.configure(font=("Segoe UI", task_font, "bold"))

        interval_font = max(7, int(9 * scale))
        self.interval_label.configure(
            font=("Segoe UI", interval_font),
            padx=max(6, int(8 * scale)),
            pady=max(2, int(3 * scale)),
        )
        self.interval_label.pack_configure(pady=(0, max(4, int(6 * scale))))

        countdown_font = max(8, int(10 * scale))
        self.countdown_label.configure(
            font=("Segoe UI", countdown_font),
            wraplength=max(100, size + int(20 * scale)),
        )
        self.countdown_label.pack_configure(pady=(0, max(4, int(6 * scale))))

        self.pause_button.configure(
            font=("Segoe UI", max(9, int(10 * scale)), "bold"),
            width=max(6, int(7 * scale)),
        )
        self.check_button.configure(
            font=("Segoe UI", max(9, int(9 * scale))),
            width=max(7, int(8 * scale)),
        )
        self.controls.pack_configure(pady=(0, max(4, int(6 * scale))))

        detail_pad = max(6, int(8 * scale))
        self.detail_frame.configure(padx=detail_pad, pady=detail_pad)
        summary_font = max(7, int(8 * scale))
        self.summary_label.configure(
            font=("Segoe UI", summary_font),
            wraplength=max(80, size - int(12 * scale)),
        )

        trend_width = max(60, size - int(12 * scale))
        trend_height = max(28, int(44 * scale))
        self.trend_canvas.config(width=trend_width, height=trend_height)

        caption_font = max(6, int(7 * scale))
        self.trend_caption.configure(font=("Segoe UI", caption_font))
        self.history_controls.pack_configure(pady=(max(6, int(6 * scale)), 0))
        history_font = max(7, int(9 * scale))
        for window, button in self.history_buttons.items():
            button.configure(font=("Segoe UI", history_font))
            button.pack_configure(padx=max(1, int(2 * scale)))
        self._refresh_history_buttons()

        share_font = max(8, int(9 * scale))
        self.export_button.configure(
            font=("Segoe UI", share_font, "bold"),
            padx=max(8, int(8 * scale)),
            pady=max(4, int(4 * scale)),
        )

        self._update_arc_extent()

    def set_due(self, value: bool) -> None:
        if self._is_due == value:
            return
        self._is_due = value
        color = ACCENT_BLUE_DUE if value else ACCENT_BLUE
        self.ring_canvas.itemconfigure(self.progress_arc, outline=color)
        border_color = ACCENT_BLUE_DUE if value else CARD_BORDER
        self.card.configure(highlightbackground=border_color, highlightcolor=border_color)
        text_color = ACCENT_BLUE if value else TEXT_SECONDARY
        self.countdown_label.configure(fg=text_color, text=self._next_ping_text())
        self.interval_label.configure(text=self._interval_text())
        self._apply_check_base_state()

    def update_progress(self) -> None:
        target_ratio = self.clock.progress_ratio()
        self._display_ratio = self._ease_ratio(self._display_ratio, target_ratio)

        extent = max(-360 * self._display_ratio, -360)
        self.ring_canvas.itemconfigure(self.progress_arc, extent=extent)
        self.pause_button.configure(text=self._pause_icon())
        self.expand_btn.configure(text=self._expand_icon())
        self.interval_label.configure(text=self._interval_text())
        self.countdown_label.configure(text=self._next_ping_text())
        self.summary_label.configure(text=self._detail_text())
        self.set_due(self.clock.due)
        self._apply_check_base_state()
        if self.clock.expanded:
            self._show_details()
        else:
            self._hide_details()
        self._update_arc_extent()

    def refresh_label(self) -> None:
        self.task_var.set(self.clock.label)

    def _show_details(self) -> None:
        if not self.detail_frame.winfo_ismapped():
            self.detail_frame.pack(fill="x", padx=16, pady=(0, 12))
        self._update_trend_caption()
        self._draw_trend()
        self._refresh_history_buttons()

    def _hide_details(self) -> None:
        if self.detail_frame.winfo_ismapped():
            self.detail_frame.pack_forget()

    def _draw_trend(self) -> None:
        canvas = getattr(self, "trend_canvas", None)
        if canvas is None:
            return
        days = self.history_var.get()
        recent = self.clock.recent_history(days)
        canvas.delete("all")
        if not recent:
            return

        try:
            width = int(canvas["width"])
            height = int(canvas["height"])
        except (ValueError, tk.TclError):
            width, height = 170, 48

        usable_height = max(height - 26, 10)
        base_line = height - 18
        max_count = max((count for _, count in recent), default=0)
        if max_count <= 0:
            max_count = 1

        num = len(recent)
        gap = 8
        bar_width = max(10.0, (width - gap * (num + 1)) / num)
        total_width = bar_width * num + gap * (num - 1)
        start_x = max(4.0, (width - total_width) / 2)

        for idx, (label, value) in enumerate(recent):
            proportion = value / max_count if max_count else 0.0
            bar_height = usable_height * proportion
            if value > 0:
                bar_height = max(bar_height, 6)
            else:
                bar_height = 2

            x0 = start_x + idx * (bar_width + gap)
            x1 = x0 + bar_width
            y1 = base_line
            y0 = y1 - bar_height
            fill = ACCENT_BLUE if idx == num - 1 else TREND_BAR

            canvas.create_rectangle(
                x0,
                y0,
                x1,
                y1,
                fill=fill,
                outline="",
            )

            label_y = max(y0 - 6, 6)
            canvas.create_text(
                (x0 + x1) / 2,
                label_y,
                text=str(value),
                fill=TEXT_SECONDARY,
                font=("Segoe UI", 8),
            )

            canvas.create_text(
                (x0 + x1) / 2,
                y1 + 8,
                text=label,
                fill=TEXT_SECONDARY,
                font=("Segoe UI", 8),
            )

    def _update_trend_caption(self) -> None:
        if hasattr(self, "trend_caption"):
            window = max(int(self.history_var.get()), 1)
            suffix = "day" if window == 1 else "days"
            self.trend_caption.configure(text=f"Past {window} {suffix}")
        self._refresh_history_buttons()

    def _ease_ratio(self, current: float, target: float) -> float:
        target = max(0.0, min(target, 1.0))
        if self.clock.due:
            return target

        delta = target - current
        if abs(delta) < 0.002:
            return target

        easing = 0.08 + min(0.25, abs(delta) * 0.6)
        return current + delta * easing

    def _update_arc_extent(self) -> None:
        extent = max(-360 * getattr(self, "_display_ratio", 0.0), -360)
        self.ring_canvas.itemconfigure(self.progress_arc, extent=extent)

    def _bind_hover(
        self,
        widget: tk.Widget,
        on_enter: Callable[[], None],
        on_leave: Callable[[], None],
    ) -> None:
        widget.bind("<Enter>", lambda _event: on_enter())
        widget.bind("<Leave>", lambda _event: on_leave())

    def _apply_check_base_state(self) -> None:
        if not hasattr(self, "check_button"):
            return
        if self._is_due or self.clock.due:
            self.check_button.configure(
                bg="#e5edff",
                fg=ACCENT_BLUE,
                relief="solid",
                bd=1,
            )
        else:
            self.check_button.configure(
                bg="#ffffff",
                fg=TEXT_SECONDARY,
                relief="groove",
                bd=1,
            )

    def _refresh_history_buttons(self) -> None:
        if not hasattr(self, "history_buttons"):
            return
        selected = self.history_var.get()
        for window, button in self.history_buttons.items():
            if window == selected:
                button.configure(
                    bg=ACCENT_BLUE,
                    fg="#ffffff",
                    relief="groove",
                    bd=0,
                )
            else:
                self._style_history_button(window)

    def _style_history_button(self, window: int) -> None:
        button = self.history_buttons.get(window)
        if not button:
            return
        button.configure(
            bg="#ffffff",
            fg=TEXT_SECONDARY,
            relief="flat",
            bd=0,
        )
