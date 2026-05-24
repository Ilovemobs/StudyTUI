# StudyTUI

**A terminal-based study tracker with AI features** — notes, tasks, flashcards, pomodoro, calendar, and Gemini AI assistant. All in your terminal.

```
╔══════════════════════════════════════════════════════════╗
║  StudyTUI                         🎯 3 tasks due       ║
║  ┌────────────────────────────────────────────────────┐ ║
║  │  Dashboard   25:00  📝 12 notes  🃏 5 flashcards  │ ║
║  │  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐              │ ║
║  │  │Backlog│ │ ToDo │ │In Pro│ │ Done │              │ ║
║  │  │ Task4 │ │Task1 │ │Task2 │ │Task3 │              │ ║
║  │  └──────┘ └──────┘ └──────┘ └──────┘              │ ║
║  └────────────────────────────────────────────────────┘ ║
║  [d]ash [n]otes [t]asks [f]lash [p]omo [c]al [a]i [s]et ║
╚══════════════════════════════════════════════════════════╝
```

---

## Features

### 📝 Notes
- **Markdown editor** with syntax highlighting
- **Tree hierarchy** — organize notes under subjects with nesting
- **Full-text search** — instant search across all notes via SQLite FTS5
- **Export to Markdown** — save any note to `~/Downloads/`
- **Tags** — categorize and filter notes

### ✅ Tasks (Kanban)
- **4-column Kanban board** — Backlog, To Do, In Progress, Done
- **Priority levels** P0–P4 with color-coded borders
- **Due dates** with overdue highlighting
- **Keyboard-driven** — move tasks left/right between columns
- **Recurring tasks** support (configurable)

### 🃏 Flashcards
- **Spaced repetition** using the SM-2 algorithm (same as Anki)
- 4 rating levels: Again (1) / Hard (2) / Good (3) / Easy (4)
- Automatic scheduling — cards due for review appear in order
- **AI-powered generation** — paste notes, get flashcards automatically
- Subject categorization

### ⏱️ Pomodoro Timer
- Configurable work/break intervals (default: 25/5/15)
- **Automatic study logging** — sessions recorded to database
- Visual progress bar
- Daily study time tracking
- Background running while navigating other screens

### 📅 Calendar
- **Month grid view** with event markers
- Shows task due dates and scheduled events
- Navigate between months
- Day detail panel with task list

### 🤖 AI Assistant (Gemini)
- **Chat** — ask questions about your study material
- **Summarize** — condense notes into key points
- **Flashcard generator** — auto-create Q&A cards from text
- **Quiz generator** — AI creates practice questions from your notes
- **Explain concepts** — get simplified explanations
- **Grammar check** — improve your writing
- Free tier: **1,500 requests/day** via Google AI Studio (no credit card)

### ⚙️ Settings
- AI provider configuration (Gemini / DeepSeek)
- Pomodoro timing customization
- Dark/Light theme
- Vim-style keybindings toggle
- Config file at `~/.config/studytui/config.json`

---

## Installation

### From source (The only one)
```bash
git clone https://github.com/ayushp/studytui
cd studytui
pip install -e .
studytui
```


### Dependencies
- Python ≥ 3.10
- [Textual](https://textual.textualize.io) — modern TUI framework
- [aiohttp](https://docs.aiohttp.org) — async HTTP for AI API calls
- SQLite — local database (bundled with Python)

---

## Quick Start

```bash
studytui
```

### AI Setup (optional, free)
1. Press `s` to open **Settings**
2. Go to [Google AI Studio](https://aistudio.google.com)
3. Click **Get API Key** → Create API key (no credit card required)
4. Paste the key into the **Gemini API Key** field
5. Set **AI Provider** to `gemini`
6. Press `Ctrl+S` to save
7. Press `a` to open **AI Chat** and start asking questions

---

## Keybindings

| Key | Screen / Action |
|-----|----------------|
| `d` | Dashboard |
| `n` | Notes |
| `t` | Tasks (Kanban) |
| `f` | Flashcards |
| `p` | Pomodoro |
| `c` | Calendar |
| `a` | AI Chat |
| `s` | Settings |
| `q` | Quit |

### Notes
| Key | Action |
|-----|--------|
| `n` | New note |
| `Ctrl+S` | Save note |
| `e` | Export as Markdown |
| `Delete` | Delete note |
| `/` | Search notes |

### Tasks
| Key | Action |
|-----|--------|
| `n` | New task |
| `Left` | Move to previous column |
| `Right` | Move to next column |
| `Delete` | Delete task |

### Flashcards
| Key | Action |
|-----|--------|
| `Space` | Flip card (show answer) |
| `1` | Rate: Again (forgot) |
| `2` | Rate: Hard |
| `3` | Rate: Good |
| `4` | Rate: Easy |
| `n` | Create new card |

### Pomodoro
| Key | Action |
|-----|--------|
| `Space` | Start / Pause timer |
| `r` | Reset timer |

### Calendar
| Key | Action |
|-----|--------|
| `n` | Next month |
| `p` | Previous month |
| `t` | Jump to today |

---

## Architecture

```
studytui/
├── main.py              # Entry point
├── app.py               # App class + screen routing + keybindings
├── config.py            # ~/.config/studytui/config.json management
├── theme.tcss           # Textual CSS theme (dark/light)
├── database/
│   └── schema.py        # SQLite schema (8 tables + FTS5 + triggers)
├── screens/
│   ├── dashboard.py     # Home screen with study summary
│   ├── notes.py         # Markdown notes with tree sidebar
│   ├── tasks.py         # Kanban board (4 columns)
│   ├── flashcards.py    # SM-2 spaced repetition review
│   ├── pomodoro.py      # Timer + auto-logging
│   ├── calendar.py      # Month calendar with events
│   ├── ai_chat.py       # Gemini AI chat interface
│   └── settings.py      # Config editor
├── ai/
│   └── provider.py      # Gemini async client (aiohttp)
├── utils/
│   └── markdown.py      # Markdown stripping helpers
└── widgets/             # Custom widget mixins
```

### Data Model

| Table | Purpose |
|-------|---------|
| `subjects` | Course/subject hierarchy (nested via parent_id) |
| `notes` | Markdown notes linked to subjects |
| `tags` | Tags with colors |
| `note_tags` | Many-to-many notes ↔ tags |
| `tasks` | Kanban tasks with priority, due dates, recurring |
| `task_tags` | Many-to-many tasks ↔ tags |
| `flashcards` | Q&A cards with SM-2 scheduling fields |
| `study_sessions` | Auto-logged pomodoro/study time |
| `events` | Calendar events |
| `notes_fts` | Full-text search index (SQLite FTS5) |

### Storage

- **Database**: `~/.local/share/studytui/study.db` (SQLite, WAL mode)
- **Config**: `~/.config/studytui/config.json`
- **Exports**: `~/Downloads/*.md` (markdown export)

---

## AI Providers

| Provider | Cost | Free Tier | Setup |
|----------|------|-----------|-------|
| **Gemini** (default) | $0 | 1,500 req/day, 15 RPM | No credit card needed |
| **DeepSeek** | $0.14/M tokens | 5M tokens on signup | Requires account |

---

## Data Privacy

- **All data stored locally** on your machine
- No cloud sync, no telemetry, no analytics
- AI API calls go directly to your configured provider
- You control the API key — revoke any time

---

## Development

```bash
git clone https://github.com/ayushp/studytui
cd studytui
pip install -e ".[dev]"
# Run tests
python3 -c "from app import StudyTUI; print('OK')"
```

To run the headless test suite:
```bash
python3 -c "
import asyncio
from app import StudyTUI
async def test():
    async with StudyTUI().run_test() as p:
        await p.press('n')  # Notes
        await p.press('t')  # Tasks
        await p.press('f')  # Flashcards
        await p.press('p')  # Pomodoro
        await p.press('c')  # Calendar
        await p.press('a')  # AI Chat
        await p.press('s')  # Settings
        print('All screens OK')
asyncio.run(test())
"
```

---

## License

Apache 2.0

---

*Built with [Textual](https://textual.textualize.io) — the Python TUI framework.*
