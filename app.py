from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Header, Footer, TabbedContent, TabPane
from textual import events

from config import load_config, save_config
from database.schema import init_db, get_db
from screens.dashboard import DashboardScreen
from screens.notes import NotesScreen
from screens.tasks import TasksScreen
from screens.flashcards import FlashcardsScreen
from screens.pomodoro import PomodoroScreen
from screens.calendar import CalendarScreen
from screens.ai_chat import AIChatScreen
from screens.settings import SettingsScreen


class StudyTUI(App):
    SCREENS = {
        "dashboard": DashboardScreen,
        "notes": NotesScreen,
        "tasks": TasksScreen,
        "flashcards": FlashcardsScreen,
        "pomodoro": PomodoroScreen,
        "calendar": CalendarScreen,
        "ai_chat": AIChatScreen,
        "settings": SettingsScreen,
    }

    BINDINGS = [
        Binding("d", "switch_screen('dashboard')", "Dashboard", show=False),
        Binding("n", "switch_screen('notes')", "Notes", show=False),
        Binding("t", "switch_screen('tasks')", "Tasks", show=False),
        Binding("f", "switch_screen('flashcards')", "Flashcards", show=False),
        Binding("p", "switch_screen('pomodoro')", "Pomodoro", show=False),
        Binding("c", "switch_screen('calendar')", "Calendar", show=False),
        Binding("a", "switch_screen('ai_chat')", "AI Chat", show=False),
        Binding("s", "switch_screen('settings')", "Settings", show=False),
        Binding("q", "quit", "Quit"),
    ]

    CSS_PATH = "theme.tcss"

    def __init__(self):
        super().__init__()
        self.config = load_config()
        init_db()
        self.current_screen_name = "dashboard"

    def on_mount(self):
        self.push_screen("dashboard")

    def action_switch_screen(self, screen_name: str):
        self.current_screen_name = screen_name
        screen_cls = self.SCREENS.get(screen_name)
        if screen_cls:
            self.switch_screen(screen_cls())

    def action_quit(self):
        save_config(self.config)
        self.exit()

    def get_db(self):
        return get_db()
