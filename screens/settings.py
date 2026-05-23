from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual.widgets import Header, Label, Input, Button, Select, Checkbox, Static, Footer
from textual.binding import Binding
from config import load_config, save_config


class SettingsScreen(Screen):
    BINDINGS = [
        Binding("ctrl+s", "save", "Save"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Vertical(
                Label("AI Provider", classes="settings-section-title"),
                Select(
                    [(v, v) for v in ["none", "gemini", "deepseek"]],
                    prompt="AI Provider",
                    id="ai-provider",
                ),
                Input(placeholder="Gemini API Key", id="gemini-key"),
                Input(placeholder="DeepSeek API Key", id="deepseek-key"),
                Label("Gemini is free at aistudio.google.com (no credit card needed)", classes="text-muted"),
                id="ai-settings",
                classes="settings-section",
            ),
            Vertical(
                Label("Pomodoro", classes="settings-section-title"),
                Input(placeholder="Work minutes", id="pomodoro-work"),
                Input(placeholder="Break minutes", id="pomodoro-break"),
                Input(placeholder="Long break minutes", id="pomodoro-long"),
                Input(placeholder="Sessions before long break", id="pomodoro-sessions"),
                id="pomodoro-settings",
                classes="settings-section",
            ),
            Vertical(
                Label("Appearance", classes="settings-section-title"),
                Select(
                    [(v, v) for v in ["dark", "light"]],
                    prompt="Theme",
                    id="theme-select",
                ),
                Checkbox("Vim-style keybindings", id="vim-mode"),
                id="appearance-settings",
                classes="settings-section",
            ),
            Button("Save Settings", id="btn-save-settings", variant="primary"),
            Label("", id="settings-status"),
            id="content",
        )
        yield Footer()

    def on_mount(self):
        cfg = load_config()
        self.query_one("#gemini-key", Input).value = cfg.get("gemini_api_key", "")
        self.query_one("#deepseek-key", Input).value = cfg.get("deepseek_api_key", "")
        self.query_one("#pomodoro-work", Input).value = str(cfg.get("pomodoro_work", 25))
        self.query_one("#pomodoro-break", Input).value = str(cfg.get("pomodoro_break", 5))
        self.query_one("#pomodoro-long", Input).value = str(cfg.get("pomodoro_long_break", 15))
        self.query_one("#pomodoro-sessions", Input).value = str(cfg.get("pomodoro_sessions_before_long", 4))
        self.query_one("#theme-select", Select).value = cfg.get("theme", "dark")
        self.query_one("#vim-mode", Checkbox).value = cfg.get("vim_mode", True)
        self.query_one("#ai-provider", Select).value = cfg.get("ai_provider", "none")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "btn-save-settings":
            self.action_save()

    def action_save(self):
        try:
            cfg = load_config()
            cfg["gemini_api_key"] = self.query_one("#gemini-key", Input).value
            cfg["deepseek_api_key"] = self.query_one("#deepseek-key", Input).value
            cfg["pomodoro_work"] = int(self.query_one("#pomodoro-work", Input).value or 25)
            cfg["pomodoro_break"] = int(self.query_one("#pomodoro-break", Input).value or 5)
            cfg["pomodoro_long_break"] = int(self.query_one("#pomodoro-long", Input).value or 15)
            cfg["pomodoro_sessions_before_long"] = int(self.query_one("#pomodoro-sessions", Input).value or 4)
            cfg["theme"] = self.query_one("#theme-select", Select).value
            cfg["vim_mode"] = self.query_one("#vim-mode", Checkbox).value
            cfg["ai_provider"] = self.query_one("#ai-provider", Select).value
            save_config(cfg)
            self.query_one("#settings-status", Label).update("Settings saved!")
        except ValueError:
            self.query_one("#settings-status", Label).update("Error: check number fields")
