from PySide6.QtCore import QObject, Signal, QTimer, Property

class ClockUnit(QObject):
    # Signals
    ticked = Signal(float)  # Emits progress (0.0 to 1.0)
    finished = Signal()     # Emits when timer completes
    paused_changed = Signal(bool) # Emits when paused state changes
    
    def __init__(self, identifier: str, label: str, interval_minutes: int, parent=None):
        super().__init__(parent)
        self._identifier = identifier
        self._label = label
        self._interval_minutes = interval_minutes
        self._elapsed_seconds = 0.0
        self._paused = True
        self._due = False
        
        # Internal Timer
        self._timer = QTimer(self)
        self._timer.setInterval(100) # 100ms precision
        self._timer.timeout.connect(self._on_tick)

    @Property(str, constant=True)
    def identifier(self):
        return self._identifier

    @Property(str)
    def label(self):
        return self._label
    
    @label.setter
    def label(self, value):
        self._label = value

    @Property(float)
    def progress(self):
        total_seconds = self._interval_minutes * 60
        if total_seconds == 0: return 0.0
        return min(self._elapsed_seconds / total_seconds, 1.0)

    @Property(str)
    def time_text(self):
        total_seconds = self._interval_minutes * 60
        remaining = max(0, total_seconds - self._elapsed_seconds)
        m = int(remaining // 60)
        s = int(remaining % 60)
        return f"{m:02d}:{s:02d}"

    def start(self):
        if self._paused and not self._due:
            self._paused = False
            self._timer.start()
            self.paused_changed.emit(False)

    def pause(self):
        if not self._paused:
            self._paused = True
            self._timer.stop()
            self.paused_changed.emit(True)

    def reset(self):
        self.pause()
        self._elapsed_seconds = 0.0
        self._due = False
        self.ticked.emit(0.0)

    def toggle(self):
        if self._paused:
            self.start()
        else:
            self.pause()

    def update_interval(self, minutes: int):
        self.pause()
        self._interval_minutes = minutes
        self.reset()
        # Force UI update
        self.ticked.emit(0.0)

    def _on_tick(self):
        # Add 0.1s
        self._elapsed_seconds += 0.1
        
        total_seconds = self._interval_minutes * 60
        if self._elapsed_seconds >= total_seconds:
            self._elapsed_seconds = total_seconds
            self._due = True
            self.pause()
            self.finished.emit()
            self.ticked.emit(1.0)
        else:
            self.ticked.emit(self.progress)

    def to_dict(self):
        return {
            "identifier": self._identifier,
            "label": self._label,
            "interval_minutes": self._interval_minutes,
            "elapsed_seconds": self._elapsed_seconds,
            "paused": self._paused,
            "due": self._due
        }

    @classmethod
    def from_dict(cls, data):
        clock = cls(
            identifier=data.get("identifier", "C1"),
            label=data.get("label", "New Clock"),
            interval_minutes=data.get("interval_minutes", 25)
        )
        clock._elapsed_seconds = data.get("elapsed_seconds", 0.0)
        clock._paused = data.get("paused", True)
        clock._due = data.get("due", False)
        return clock
