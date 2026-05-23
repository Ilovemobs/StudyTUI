from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import Screen
from textual.widgets import Header, Label, Tree, TextArea, Button, Input, Footer
from textual.message import Message
from textual.binding import Binding
from database.schema import get_db
from utils.markdown import markdown_to_text


class NotesScreen(Screen):
    BINDINGS = [
        Binding("n", "new_note", "New Note"),
        Binding("delete", "delete_note", "Delete Note"),
        Binding("/", "focus_search", "Search"),
        Binding("ctrl+s", "save_note", "Save"),
        Binding("e", "export_note", "Export MD"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Tree("Subjects", id="note-tree"),
            Container(
                Input(placeholder="Search notes...", id="note-search"),
                Horizontal(
                    Button("New Note", id="btn-new-note", variant="primary"),
                    Button("Save", id="btn-save-note", variant="success"),
                    Button("Export MD", id="btn-export-note"),
                    Button("Delete", id="btn-del-note", variant="error"),
                ),
                TextArea(id="note-editor"),
                Label("", id="note-status"),
                id="note-editor-container",
            ),
            id="content",
        )
        yield Footer()

    def on_mount(self):
        self.load_subjects()

    def load_subjects(self):
        tree = self.query_one("#note-tree", Tree)
        tree.root.remove_children()
        db = get_db()

        def add_children(parent, parent_id):
            cur = db.execute("SELECT id, name FROM subjects WHERE parent_id IS ? ORDER BY name", (parent_id,))
            for row in cur.fetchall():
                node = parent.add(row["name"], data={"id": row["id"], "type": "subject"})
                cur2 = db.execute(
                    "SELECT id, title FROM notes WHERE subject_id = ? ORDER BY updated_at DESC",
                    (row["id"],),
                )
                for note in cur2.fetchall():
                    node.add_leaf(note["title"], data={"id": note["id"], "type": "note"})

        add_children(tree.root, None)
        db.close()

    def on_tree_node_selected(self, event: Tree.NodeSelected):
        data = event.node.data
        if data and data.get("type") == "note":
            self.load_note(data["id"])

    def load_note(self, note_id: int):
        db = get_db()
        cur = db.execute("SELECT id, title, content FROM notes WHERE id = ?", (note_id,))
        row = cur.fetchone()
        db.close()
        if row:
            editor = self.query_one("#note-editor", TextArea)
            editor.text = row["content"]
            editor.data = {"note_id": row["id"]}
            self.query_one("#note-status", Label).update(f"Editing: {row['title']}")

    def action_new_note(self):
        db = get_db()
        cur = db.execute("INSERT INTO notes (title, content) VALUES (?, ?)", ("Untitled", ""))
        note_id = cur.lastrowid
        db.commit()
        db.close()
        self.load_subjects()
        self.load_note(note_id)

    def action_delete_note(self):
        editor = self.query_one("#note-editor", TextArea)
        if note_id := editor.data.get("note_id"):
            db = get_db()
            db.execute("DELETE FROM notes WHERE id = ?", (note_id,))
            db.commit()
            db.close()
            editor.text = ""
            editor.data = {}
            self.query_one("#note-status", Label).update("Note deleted")
            self.load_subjects()

    def action_save_note(self):
        editor = self.query_one("#note-editor", TextArea)
        note_id = editor.data.get("note_id")
        if note_id:
            db = get_db()
            db.execute("UPDATE notes SET content = ?, updated_at = datetime('now') WHERE id = ?",
                       (editor.text, note_id))
            db.commit()
            db.close()
            self.query_one("#note-status", Label).update("Saved!")

    def action_export_note(self):
        editor = self.query_one("#note-editor", TextArea)
        note_id = editor.data.get("note_id")
        if not note_id:
            return
        db = get_db()
        cur = db.execute("SELECT title, content FROM notes WHERE id = ?", (note_id,))
        row = cur.fetchone()
        db.close()
        if row:
            import os
            export_dir = Path.home() / "Downloads"
            export_dir.mkdir(parents=True, exist_ok=True)
            safe_title = row["title"].replace(" ", "_").replace("/", "_")
            path = export_dir / f"{safe_title}.md"
            with open(path, "w") as f:
                f.write(f"# {row['title']}\n\n{row['content']}")
            self.query_one("#note-status", Label).update(f"Exported to {path}")

    def action_focus_search(self):
        self.query_one("#note-search", Input).focus()
