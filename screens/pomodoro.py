import time
from datetime import datetime

from textual.app import ComposeResult, Timer
from textual.containers import Container, Horizontal
from textual.screen import Screen
from textual.widgets import Header, Label, Button, ProgressBar, Footer
from textual.binding import Binding
from database.schema import get_db


class PomodoroScreen(Screen):
    BINDINGS = [
        Binding("space", "toggle", "Start/Stop"),
        Binding("r", "reset", "Reset"),
    ]

    MODES = ["work", "break", "long_break"]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Label("Work", id="pomodoro-mode"),
            Label("25:00", id="timer-display"),
            ProgressBar(total=25 * 60, id="timer-progress", show_percentage=False),
            Horizontal(
                Button("Start", id="btn-toggle", variant="primary"),
                Button("Reset", id="btn-reset", variant="warning"),
            ),
            Label("Session: 0  |  Today: 0m", id="pomodoro-status"),
            id="content",
        )
        yield Footer()

    def on_mount(self):
        cfg = self.app.config if hasattr(self.app, "config") else {}
        self.work_mins = int(cfg.get("pomodoro_work", 25))
        self.break_mins = int(cfg.get("pomodoro_break", 5))
        self.long_break_mins = int(cfg.get("pomodoro_long_break", 15))
        self.sessions_before_long = int(cfg.get("pomodoro_sessions_before_long", 4))
        self.running = False
        self.mode = "work"
        self.time_left = self.work_mins * 60
        self.session_count = 0
        self.current_session_start = None
        self.update_timer = None
        self.update_display()
        self.update_status()

    def update_display(self):
        mins = self.time_left // 60
        secs = self.time_left % 60
        self.query_one("#timer-display", Label).update(f"{mins:02d}:{secs:02d}")
        total = {"work": self.work_mins * 60, "break": self.break_mins * 60, "long_break": self.long_break_mins * 60}
        self.query_one("#timer-progress", ProgressBar).total = total.get(self.mode, 25 * 60)
        self.query_one("#timer-progress", ProgressBar).progress = total.get(self.mode, 25 * 60) - self.time_left
        self.query_one("#pomodoro-mode", Label).update(self.mode.replace("_", " ").title())

    def action_toggle(self):
        if self.running:
            self.running = False
            self.query_one("#btn-toggle", Button).label = "Resume"
            if self.update_timer:
                self.update_timer.pause()
        else:
            if not self.running and self.time_left > 0:
                self.running = True
                self.query_one("#btn-toggle", Button).label = "Pause"
                self.update_timer = self.set_interval(1, self.tick)
                if self.current_session_start is None and self.mode == "work":
                    self.current_session_start = datetime.now()

    def tick(self):
        if self.time_left > 0:
            self.time_left -= 1
            self.update_display()
        else:
            self.complete_phase()

    def complete_phase(self):
        if self.update_timer:
            self.update_timer.pause()
        self.running = False
        self.query_one("#btn-toggle", Button).label = "Start"

        if self.mode == "work":
            self.log_session()
            self.session_count += 1
            if self.session_count % self.sessions_before_long == 0:
                self.mode = "long_break"
                self.time_left = self.long_break_mins * 60
            else:
                self.mode = "break"
                self.time_left = self.break_mins * 60
        else:
            self.mode = "work"
            self.time_left = self.work_mins * 60
            self.current_session_start = None

        self.update_display()
        self.update_status()

    def log_session(self):
        if self.current_session_start:
            duration = int((datetime.now() - self.current_session_start).total_seconds() // 60)
            db = get_db()
            db.execute(
                "INSERT INTO study_sessions (start_time, end_time, duration_minutes) VALUES (?, ?, ?)",
                (self.current_session_start.isoformat(), datetime.now().isoformat(), max(duration, 1)),
            )
            db.commit()
            db.close()

    def update_status(self):
        db = get_db()
        cur = db.execute("SELECT IFNULL(SUM(duration_minutes), 0) as total FROM study_sessions WHERE date(start_time) = date('now')")
        today = cur.fetchone()["total"]
        db.close()
        self.query_one("#pomodoro-status", Label).update(f"Session: {self.session_count}  |  Today: {today}m")

    def action_reset(self):
        if hasattr(self, "update_timer") and self.update_timer:
            self.update_timer.pause()
        self.running = False
        self.mode = "work"
        self.time_left = self.work_mins * 60
        self.current_session_start = None
        self.query_one("#btn-toggle", Button).label = "Start"
        self.update_display()
