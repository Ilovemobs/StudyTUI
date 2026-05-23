from datetime import datetime, date, timedelta
from calendar import monthcalendar

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Header, Label, Button, DataTable, Footer
from textual.binding import Binding
from database.schema import get_db


class CalendarScreen(Screen):
    BINDINGS = [
        Binding("n", "next_month", "Next"),
        Binding("p", "prev_month", "Prev"),
        Binding("t", "today", "Today"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Horizontal(
                Button("<", id="btn-prev-month", variant="default"),
                Label("", id="calendar-title"),
                Button(">", id="btn-next-month", variant="default"),
            ),
            DataTable(id="calendar-table"),
            Container(
                Label("Selected: ", id="calendar-day-info"),
                DataTable(id="calendar-day-tasks", show_header=False),
                id="calendar-day-panel",
            ),
            id="content",
        )
        yield Footer()

    def on_mount(self):
        self.current_date = date.today()
        self.selected_date = None
        self.render_month()

    def render_month(self):
        self.query_one("#calendar-title", Label).update(self.current_date.strftime("%B %Y"))

        cal = monthcalendar(self.current_date.year, self.current_date.month)
        table = self.query_one("#calendar-table", DataTable)
        table.clear()

        table.add_columns("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")

        db = get_db()
        month_str = self.current_date.strftime("%Y-%m")
        cur = db.execute(
            "SELECT date, title FROM events WHERE date LIKE ? ORDER BY date",
            (f"{month_str}%",),
        )
        events = {}
        for r in cur.fetchall():
            events.setdefault(r["date"], []).append(r["title"])
        cur = db.execute(
            "SELECT due_date, title FROM tasks WHERE due_date LIKE ? AND status != 'done' ORDER BY due_date",
            (f"{month_str}%",),
        )
        for r in cur.fetchall():
            events.setdefault(r["due_date"], []).append(f"[Task] {r['title']}")
        db.close()

        for week in cal:
            row = []
            for day_num in week:
                if day_num == 0:
                    row.append("")
                else:
                    d = self.current_date.replace(day=day_num)
                    ds = d.strftime("%Y-%m-%d")
                    marker = " •" if ds in events else ""
                    fmt = f"[bold]{day_num}{marker}[/]" if d == date.today() else f"{day_num}{marker}"
                    row.append(fmt)
            table.add_row(*row)

        if self.selected_date:
            self.show_day_details(self.selected_date)

    def show_day_details(self, dt: date):
        ds = dt.strftime("%Y-%m-%d")
        self.query_one("#calendar-day-info", Label).update(f"Selected: {ds}")
        detail_table = self.query_one("#calendar-day-tasks", DataTable)
        detail_table.clear()
        detail_table.add_columns("Item")

        db = get_db()
        cur = db.execute("SELECT title FROM events WHERE date = ? ORDER BY time", (ds,))
        for r in cur.fetchall():
            detail_table.add_row(r["title"])
        cur = db.execute(
            "SELECT title FROM tasks WHERE due_date = ? AND status != 'done'",
            (ds,),
        )
        for r in cur.fetchall():
            detail_table.add_row(f"[Task] {r['title']}")
        if not detail_table.row_count:
            detail_table.add_row("Nothing scheduled")
        db.close()

    def action_next_month(self):
        y = self.current_date.year + (self.current_date.month // 12)
        m = (self.current_date.month % 12) + 1
        self.current_date = self.current_date.replace(year=y, month=m)
        self.render_month()

    def action_prev_month(self):
        m = self.current_date.month - 1
        y = self.current_date.year
        if m == 0:
            m = 12
            y -= 1
        self.current_date = self.current_date.replace(year=y, month=m)
        self.render_month()

    def action_today(self):
        self.current_date = date.today()
        self.selected_date = date.today()
        self.render_month()
