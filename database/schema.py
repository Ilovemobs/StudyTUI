import sqlite3
import os
from pathlib import Path

DB_DIR = Path.home() / ".local" / "share" / "studytui"
DB_PATH = DB_DIR / "study.db"

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    parent_id INTEGER REFERENCES subjects(id) ON DELETE CASCADE,
    color TEXT DEFAULT '#4EC9B0',
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER REFERENCES subjects(id) ON DELETE SET NULL,
    title TEXT NOT NULL DEFAULT 'Untitled',
    content TEXT DEFAULT '',
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    color TEXT DEFAULT '#569CD6'
);

CREATE TABLE IF NOT EXISTS note_tags (
    note_id INTEGER REFERENCES notes(id) ON DELETE CASCADE,
    tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (note_id, tag_id)
);

CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER REFERENCES subjects(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    description TEXT DEFAULT '',
    status TEXT NOT NULL DEFAULT 'backlog' CHECK(status IN ('backlog','todo','in_progress','done')),
    priority INTEGER NOT NULL DEFAULT 2 CHECK(priority BETWEEN 0 AND 4),
    due_date TEXT,
    recurring_rule TEXT,
    position INTEGER NOT NULL DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS task_tags (
    task_id INTEGER REFERENCES tasks(id) ON DELETE CASCADE,
    tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (task_id, tag_id)
);

CREATE TABLE IF NOT EXISTS flashcards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER REFERENCES subjects(id) ON DELETE SET NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    ease_factor REAL NOT NULL DEFAULT 2.5,
    interval_days INTEGER NOT NULL DEFAULT 0,
    repetitions INTEGER NOT NULL DEFAULT 0,
    next_review TEXT NOT NULL DEFAULT (datetime('now')),
    last_review TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS study_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER REFERENCES subjects(id) ON DELETE SET NULL,
    start_time TEXT NOT NULL,
    end_time TEXT,
    duration_minutes INTEGER,
    notes TEXT DEFAULT '',
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER REFERENCES subjects(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    description TEXT DEFAULT '',
    date TEXT NOT NULL,
    time TEXT,
    recurring_rule TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE VIRTUAL TABLE IF NOT EXISTS notes_fts USING fts5(
    title, content, content=notes, content_rowid=id
);

CREATE TRIGGER IF NOT EXISTS notes_ai AFTER INSERT ON notes BEGIN
    INSERT INTO notes_fts(rowid, title, content) VALUES (new.id, new.title, new.content);
END;

CREATE TRIGGER IF NOT EXISTS notes_ad AFTER DELETE ON notes BEGIN
    INSERT INTO notes_fts(notes_fts, rowid, title, content) VALUES('delete', old.id, old.title, old.content);
END;

CREATE TRIGGER IF NOT EXISTS notes_au AFTER UPDATE ON notes BEGIN
    INSERT INTO notes_fts(notes_fts, rowid, title, content) VALUES('delete', old.id, old.title, old.content);
    INSERT INTO notes_fts(rowid, title, content) VALUES (new.id, new.title, new.content);
END;
"""


def get_db() -> sqlite3.Connection:
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    conn = get_db()
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    conn.close()
