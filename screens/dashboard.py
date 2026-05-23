from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Header, Label, Static, Button, DataTable
from database.schema import get_db


class DashboardPanel(Vertical):
    def __init__(self, title: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.panel_title = title
        self.add_class("dashboard-panel")

    def compose(self):
        yield Label(self.panel_title, classes="dashboard-panel-title")
        yield Static("", id=f"panel-{self.panel_title.lower().replace(' ', '-')}")


class DashboardScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Horizontal(
                DashboardPanel("Quick Stats"),
                DashboardPanel("Due Tasks"),
                DashboardPanel("Recent Notes"),
                id="dashboard-panels",
            ),
            id="content",
        )
        yield Label("", id="status-bar")

    def on_mount(self):
        self.refresh_stats()

    def refresh_stats(self):
        db = get_db()
        cur = db.execute("SELECT COUNT(*) as cnt FROM tasks WHERE status != 'done'")
        pending = cur.fetchone()["cnt"]
        cur = db.execute("SELECT COUNT(*) as cnt FROM flashcards WHERE next_review <= datetime('now')")
        due_flashcards = cur.fetchone()["cnt"]
        cur = db.execute("SELECT COUNT(*) as cnt FROM notes")
        notes_count = cur.fetchone()["cnt"]
        cur = db.execute(
            "SELECT IFNULL(SUM(duration_minutes), 0) as total FROM study_sessions WHERE date(start_time) = date('now')"
        )
        today_mins = cur.fetchone()["total"]

        stats = (
            f"Pending Tasks: {pending}\n"
            f"Due Flashcards: {due_flashcards}\n"
            f"Total Notes: {notes_count}\n"
            f"Studied Today: {today_mins}m"
        )
        self.query_one("#panel-quick-stats", Static).update(stats)

        cur = db.execute(
            "SELECT title, priority, due_date FROM tasks WHERE status != 'done' AND due_date IS NOT NULL ORDER BY due_date LIMIT 10"
        )
        tasks_panel = self.query_one("#panel-due-tasks", Static)
        if rows := cur.fetchall():
            lines = [f"{'!'*r['priority']} {r['title']} (due: {r['due_date']})" for r in rows]
            tasks_panel.update("\n".join(lines))
        else:
            tasks_panel.update("No pending tasks!")

        cur = db.execute("SELECT title, updated_at FROM notes ORDER BY updated_at DESC LIMIT 10")
        notes_panel = self.query_one("#panel-recent-notes", Static)
        if rows := cur.fetchall():
            lines = [f"  {r['title']} — {r['updated_at']}" for r in rows]
            notes_panel.update("\n".join(lines))
        else:
            notes_panel.update("No notes yet!")
        db.close()
