"""Main application bootstrap for Kenshō."""

from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Dict, List, Optional

from .models import ClockUnit, SECONDS_PER_MINUTE
from .notifications import notify_clock_due
from .storage import load_app_state, save_app_state
from .ui.clock_card import ClockCard
from .ui.settings_dialog import ClockSettingsDialog

DEFAULT_GEOMETRY = "220x280+120+120"
WINDOW_STATE_KEY = "window"
ACCENT_BLUE = "#4e7bff"
TICK_INTERVAL_MS = 250


class KenshoApp:
    """Tkinter front-end controller."""

    def __init__(self) -> None:
        self.state: Dict[str, Dict[str, str]] = load_app_state()
        self.root = tk.Tk()
        self.root.title("Kenshō")
        self.root.configure(bg="#f3f2f0")
        self.root.resizable(True, True)
        self.root.attributes("-topmost", True)

        # The toolwindow attribute reduces the title bar footprint on Windows,
        # keeping the widget compact without removing basic window controls.
        try:
            self.root.wm_attributes("-toolwindow", True)
        except tk.TclError:
            # Not all platforms support this attribute.
            pass

        # Restore geometry if available
        geometry = (
            self.state.get(WINDOW_STATE_KEY, {}).get("geometry") or DEFAULT_GEOMETRY
        )
        self.root.geometry(geometry)
        self.root.minsize(150, 160)

        self._geometry_dirty = False
        self._throttle_job: Optional[str] = None

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.bind("<Configure>", self._on_configure)

        # Placeholder container for upcoming clock cards
        self.content = tk.Frame(self.root, bg="#f3f2f0", padx=10, pady=10)
        self.content.pack(fill="both", expand=True)

        self.card_container = tk.Frame(self.content, bg="#f3f2f0")
        self.card_container.pack(fill="both", expand=True)

        self.clock_units: List[ClockUnit] = []
        self.clock_cards: List[ClockCard] = []
        self._add_button_visible = True

        self.add_card_button = tk.Button(
            self.card_container,
            text="+",
            font=("Segoe UI", 18, "bold"),
            width=2,
            bg="#ffffff",
            fg=ACCENT_BLUE,
            bd=1,
            relief="ridge",
            command=self.add_clock,
            cursor="hand2",
        )
        self.add_card_button.pack(side="left", padx=6, pady=6, fill="y")

        self._ticker_job: Optional[str] = None
        self._settings_dialog: Optional[ClockSettingsDialog] = None
        self._layout_mode: Optional[str] = None
        self._layout_job: Optional[str] = None

        self._load_clocks()
        self._start_ticker()

    def _on_configure(self, event: tk.Event) -> None:
        """Throttle saves when the user resizes or moves the window."""
        if event.widget is not self.root:
            return

        self._geometry_dirty = True

        if self._throttle_job is not None:
            self.root.after_cancel(self._throttle_job)

        # Save after the user stops moving/resizing for 300ms.
        self._throttle_job = self.root.after(300, self._persist_geometry)
        self._schedule_layout()

    def _persist_geometry(self) -> None:
        if not self._geometry_dirty:
            return
        self._geometry_dirty = False
        geometry = self.root.winfo_geometry()
        self.state.setdefault(WINDOW_STATE_KEY, {})["geometry"] = geometry
        save_app_state(self.state)
        self._throttle_job = None
        self._schedule_layout()

    def on_close(self) -> None:
        """Persist window state and destroy the root window."""
        self._persist_geometry()
        self._persist_clocks()
        if self._settings_dialog is not None:
            # Ensure dialog is destroyed before shutting down.
            self._settings_dialog.close()
        self.root.destroy()

    def run(self) -> None:
        """Start the Tkinter main loop."""
        self.root.mainloop()

    # --- Clock management -------------------------------------------------

    def _load_clocks(self) -> None:
        saved_clocks = self.state.get("clocks", [])
        if saved_clocks:
            for payload in saved_clocks:
                clock = ClockUnit.from_dict(payload)
                if not clock.identifier:
                    clock.identifier = self._generate_identifier(len(self.clock_units))
                self._append_clock(clock)
        else:
            default_clock = ClockUnit(
                identifier="C1", label="Presence Session", interval_minutes=10
            )
            self._append_clock(default_clock)
        self._refresh_identifier_labels()
        self._update_add_button_visibility()
        self._schedule_layout()

    def _schedule_layout(self) -> None:
        if self._layout_job is not None:
            return
        self._layout_job = self.root.after(40, self._apply_layout)

    def _apply_layout(self) -> None:
        self._layout_job = None
        container_width = self.card_container.winfo_width()
        if container_width <= 1:
            container_width = self.root.winfo_width()

        layout = "column" if container_width < 420 else "row"
        if len(self.clock_cards) > 2 and container_width < 640:
            layout = "column"

        gap = 12
        base_width = getattr(ClockCard, "BASE_WIDTH", 200)
        min_scale = getattr(ClockCard, "MIN_SCALE", 0.5)
        max_scale = getattr(ClockCard, "MAX_SCALE", 1.2)
        btn_scale = 1.0

        if layout == "column":
            available_width = max(100, container_width - 16)
            scale = max(
                min_scale,
                min(max_scale, available_width / base_width),
            )
            btn_scale = scale
        else:
            cards_count = max(1, len(self.clock_cards))
            visible_slots = cards_count + (1 if self._add_button_visible else 0)
            available = max(
                120, container_width - gap * max(visible_slots - 1, 0)
            )
            button_allowance = 48 if self._add_button_visible else 0
            available_for_cards = max(80, available - button_allowance)
            per_card = max(80, available_for_cards / cards_count)
            scale = max(
                min_scale,
                min(max_scale, per_card / base_width),
            )
            btn_scale = scale

        for card in self.clock_cards:
            card.update_scale(scale)

        for widget in self.card_container.pack_slaves():
            widget.pack_forget()

        self._layout_mode = layout
        if layout == "column":
            for card in self.clock_cards:
                card.pack(side="top", fill="x", padx=6, pady=6)
            if self._add_button_visible:
                self.add_card_button.pack(side="top", padx=6, pady=6, fill="x")
            else:
                self.add_card_button.pack_forget()
        else:
            for card in self.clock_cards:
                card.pack(side="left", padx=6, pady=6)
            if self._add_button_visible:
                self.add_card_button.pack(side="left", padx=6, pady=6, fill="y")
            else:
                self.add_card_button.pack_forget()

        btn_font = max(9, int(14 * btn_scale))
        self.add_card_button.configure(font=("Segoe UI", btn_font, "bold"))

    def _append_clock(self, clock: ClockUnit) -> None:
        self.clock_units.append(clock)
        card = ClockCard(
            self.card_container,
            clock,
            on_check_in=self._handle_clock_check_in,
            on_toggle_pause=self._toggle_clock_pause,
            on_label_change=self._on_clock_label_change,
            on_toggle_expand=self._toggle_clock_expand,
            on_share=lambda c=clock: self._share_clock(c),
            on_history_window_change=self._change_history_window,
            on_open_settings=self._open_settings_for_clock,
            identifier_label=clock.identifier or self._generate_identifier(
                len(self.clock_units) - 1
            ),
        )
        self.clock_cards.append(card)
        self._update_add_button_visibility()
        card.update_progress()
        self._schedule_layout()

    def add_clock(self) -> None:
        if len(self.clock_units) >= 4:
            return
        new_index = len(self.clock_units)
        identifier = self._generate_identifier(new_index)
        clock = ClockUnit(identifier=identifier, label="Mindful Session", interval_minutes=10)
        self._append_clock(clock)
        self._persist_clocks()
        self._refresh_identifier_labels()

    def _generate_identifier(self, index: int) -> str:
        return f"C{index + 1}"

    def _refresh_identifier_labels(self) -> None:
        for idx, (clock, card) in enumerate(zip(self.clock_units, self.clock_cards)):
            identifier = self._generate_identifier(idx)
            clock.identifier = identifier
            card.identifier_label.configure(text=identifier)

    # --- Timer loop -------------------------------------------------------

    def _start_ticker(self) -> None:
        self._ticker_job = self.root.after(TICK_INTERVAL_MS, self._on_tick)

    def _on_tick(self) -> None:
        delta_seconds = TICK_INTERVAL_MS / 1000.0

        for clock, card in zip(self.clock_units, self.clock_cards):
            clock.ensure_today()
            if not clock.due:
                completed = clock.tick(delta_seconds)
                if completed:
                    clock.paused = True
                    card.set_due(True)
                    notify_clock_due(clock.label, clock.sound_id)
            card.update_progress()

        self._ticker_job = self.root.after(TICK_INTERVAL_MS, self._on_tick)

    # --- Callbacks --------------------------------------------------------

    def _on_clock_label_change(self, clock: ClockUnit, new_label: str) -> None:
        clock.label = new_label
        self._persist_clocks()

    def _toggle_clock_pause(self, clock: ClockUnit) -> None:
        clock.toggle_pause()
        for existing_clock, card in zip(self.clock_units, self.clock_cards):
            if existing_clock is clock:
                card.update_progress()
                break
        self._persist_clocks()

    def _toggle_clock_expand(self, clock: ClockUnit, card: ClockCard) -> None:
        clock.expanded = not clock.expanded
        card.update_progress()
        self._persist_clocks()

    def _change_history_window(
        self, clock: ClockUnit, card: ClockCard, window: int
    ) -> None:
        clock.set_history_window(window)
        card.history_var.set(clock.history_window)
        card.update_progress()
        card._refresh_history_buttons()
        self._persist_clocks()

    def _handle_clock_check_in(self, clock: ClockUnit) -> None:
        clock.reset()
        for existing_clock, card in zip(self.clock_units, self.clock_cards):
            if existing_clock is clock:
                card.update_progress()
                break
        self._persist_clocks()

    def _share_clock(self, clock: ClockUnit) -> None:
        records = clock.history_records()
        if not records:
            messagebox.showinfo(
                "Share Kenshō Clock",
                "No check-ins recorded yet. Once you begin checking in, you can share your rhythm.",
                parent=self.root,
            )
            return

        csv_lines = ["date,clock,check_ins"]
        for iso_date, count in records:
            csv_lines.append(f"{iso_date},{clock.label.replace(',', ' ')},{count}")
        csv_text = "\n".join(csv_lines)

        initial_name = f"{clock.identifier}_{clock.label.replace(' ', '_')}.csv"
        path = filedialog.asksaveasfilename(
            parent=self.root,
            title="Export Kenshō History",
            defaultextension=".csv",
            initialfile=initial_name,
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
        )

        if not path:
            try:
                self.root.clipboard_clear()
                self.root.clipboard_append(csv_text)
                messagebox.showinfo(
                    "Share Kenshō Clock",
                    "Export cancelled. A CSV snapshot has been copied to your clipboard instead.",
                    parent=self.root,
                )
            except tk.TclError:
                messagebox.showwarning(
                    "Share Kenshō Clock",
                    "Export cancelled and clipboard is unavailable.",
                    parent=self.root,
                )
            return

        try:
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(csv_text)
            messagebox.showinfo(
                "Share Kenshō Clock",
                f"Saved check-in history for “{clock.label}” to:\n{path}",
                parent=self.root,
            )
        except OSError as exc:
            messagebox.showerror(
                "Share Kenshō Clock",
                f"Could not save the file.\n\n{exc}",
                parent=self.root,
            )

    # --- Persistence ------------------------------------------------------

    def _persist_clocks(self) -> None:
        self.state["clocks"] = [clock.serialize() for clock in self.clock_units]
        save_app_state(self.state)

    # --- Settings dialog --------------------------------------------------

    def _open_settings_for_clock(self, clock: ClockUnit, card: ClockCard) -> None:
        if self._settings_dialog is not None:
            self._settings_dialog.close()
        allow_delete = len(self.clock_units) > 1

        def handle_delete() -> None:
            if not messagebox.askyesno(
                "Delete Clock",
                f"Remove '{clock.label}' from Kenshō?",
                parent=self.root,
            ):
                return
            self._remove_clock(clock, card)
            if self._settings_dialog is not None:
                self._settings_dialog.close()

        self._settings_dialog = ClockSettingsDialog(
            self.root,
            initial_minutes=max(clock.interval_minutes, 1),
            initial_sound=clock.sound_id,
            on_apply=lambda minutes, sound: self._apply_clock_settings(
                clock, card, minutes, sound
            ),
            on_close=self._on_settings_dialog_closed,
            allow_delete=allow_delete,
            on_delete=handle_delete,
        )

    def _on_settings_dialog_closed(self) -> None:
        self._settings_dialog = None

    def _apply_clock_settings(
        self, clock: ClockUnit, card: ClockCard, minutes: int, sound_id: str
    ) -> None:
        clock.interval_minutes = minutes
        clock.sound_id = sound_id
        interval_seconds = max(minutes * SECONDS_PER_MINUTE, 1)
        clock.elapsed_seconds = min(clock.elapsed_seconds, interval_seconds)
        clock.due = clock.elapsed_seconds >= interval_seconds
        card.update_progress()
        self._persist_clocks()

    def _update_add_button_visibility(self) -> None:
        self._add_button_visible = len(self.clock_units) < 4
        if not self._add_button_visible:
            self.add_card_button.pack_forget()
        self._schedule_layout()

    def _remove_clock(self, clock: ClockUnit, card: ClockCard) -> None:
        try:
            index = self.clock_units.index(clock)
        except ValueError:
            return

        card.destroy()
        del self.clock_units[index]
        del self.clock_cards[index]

        if not self.clock_units:
            fallback = ClockUnit(
                identifier="C1", label="Presence Session", interval_minutes=10
            )
            self._append_clock(fallback)

        self._refresh_identifier_labels()
        self._update_add_button_visibility()
        self._persist_clocks()


def main() -> None:
    app = KenshoApp()
    app.run()


if __name__ == "__main__":
    main()
