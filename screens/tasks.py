from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Header, Label, Button, Input, TextArea, ListView, ListItem, Static, Footer
from textual.binding import Binding
from textual.message import Message
from database.schema import get_db

STATUSES = ["backlog", "todo", "in_progress", "done"]
STATUS_LABELS = {"backlog": "Backlog", "todo": "To Do", "in_progress": "In Progress", "done": "Done"}
STATUS_COLORS = {"backlog": "", "todo": "#E2B714", "in_progress": "#569CD6", "done": "#4EC9B0"}

KW = 1  # approximate em width


class KanbanCard(Static):
    def __init__(self, task_id: int, title: str, priority: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.task_id = task_id
        self.task_title = title
        self.task_priority = priority
        self.add_class(f"-priority-{priority}")
        self.update(f"{'!' * (4 - priority) if priority < 4 else ' '} {title}")


class KanbanColumn(Vertical):
    def __init__(self, status: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.column_status = status
        self.add_class("kanban-column")

    def compose(self):
        yield Label(STATUS_LABELS[self.column_status], classes="kanban-column-title")
        yield Container(id=f"cards-{self.column_status}")

    def refresh_tasks(self):
        container = self.query_one(f"#cards-{self.column_status}", Container)
        container.remove_children()
        db = get_db()
        cur = db.execute(
            "SELECT id, title, priority FROM tasks WHERE status = ? ORDER BY position, created_at",
            (self.column_status,),
        )
        for row in cur.fetchall():
            container.mount(KanbanCard(row["id"], row["title"], row["priority"]))
        db.close()


class TasksScreen(Screen):
    BINDINGS = [
        Binding("n", "new_task", "New Task"),
        Binding("delete", "delete_task", "Delete"),
        Binding("left", "move_left", "Move Left"),
        Binding("right", "move_right", "Move Right"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Horizontal(
                KanbanColumn("backlog"),
                KanbanColumn("todo"),
                KanbanColumn("in_progress"),
                KanbanColumn("done"),
                id="kanban-container",
            ),
            id="content",
        )
        yield Footer()

    def on_mount(self):
        for col in self.query(KanbanColumn):
            col.refresh_tasks()

    def move_task(self, task_id: int, new_status: str):
        db = get_db()
        db.execute("UPDATE tasks SET status = ?, updated_at = datetime('now') WHERE id = ?",
                   (new_status, task_id))
        db.commit()
        db.close()
        for col in self.query(KanbanColumn):
            col.refresh_tasks()

    def action_new_task(self):
        db = get_db()
        cur = db.execute("INSERT INTO tasks (title, status, priority, position) VALUES (?, ?, ?, ?)",
                         ("New Task", "backlog", 2, 0))
        db.commit()
        db.close()
        for col in self.query(KanbanColumn):
            col.refresh_tasks()

    def action_delete_task(self):
        focused = self.focused
        if isinstance(focused, KanbanCard):
            db = get_db()
            db.execute("DELETE FROM tasks WHERE id = ?", (focused.task_id,))
            db.commit()
            db.close()
            for col in self.query(KanbanColumn):
                col.refresh_tasks()

    def action_move_left(self):
        focused = self.focused
        if isinstance(focused, KanbanCard):
            db = get_db()
            cur = db.execute("SELECT status FROM tasks WHERE id = ?", (focused.task_id,))
            row = cur.fetchone()
            if row:
                idx = STATUSES.index(row["status"])
                if idx > 0:
                    self.move_task(focused.task_id, STATUSES[idx - 1])
            db.close()

    def action_move_right(self):
        focused = self.focused
        if isinstance(focused, KanbanCard):
            db = get_db()
            cur = db.execute("SELECT status FROM tasks WHERE id = ?", (focused.task_id,))
            row = cur.fetchone()
            if row:
                idx = STATUSES.index(row["status"])
                if idx < len(STATUSES) - 1:
                    self.move_task(focused.task_id, STATUSES[idx + 1])
            db.close()
