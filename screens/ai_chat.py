from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.screen import Screen
from textual.widgets import Header, Label, Input, Button, Static, Footer
from textual.binding import Binding
from textual.widgets import RichLog

from ai.provider import AIProvider


class AIChatScreen(Screen):
    BINDINGS = [
        Binding("ctrl+s", "send", "Send"),
        Binding("escape", "clear", "Clear Chat"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Label("AI Assistant (Gemini)", id="ai-header"),
            RichLog(id="ai-messages", highlight=True, markup=True, wrap=True),
            Horizontal(
                Input(placeholder="Ask AI something...", id="ai-input"),
                Button("Send", id="btn-ai-send", variant="primary"),
                id="ai-input-row",
            ),
            Label("", id="ai-status"),
            id="content",
        )
        yield Footer()

    def on_mount(self):
        self.add_message("system", "AI Assistant ready. Configure a Gemini API key in Settings (s key).")
        self.provider = None

    def add_message(self, role: str, content: str):
        log = self.query_one("#ai-messages", RichLog)
        prefix = "You" if role == "user" else "AI" if role == "assistant" else "System"
        style = "bold #4EC9B0" if role == "assistant" else "bold #E2B714" if role == "user" else "bold #888888"
        log.write(f"[{style}]{prefix}:[/] {content}")

    def action_send(self):
        inp = self.query_one("#ai-input", Input)
        text = inp.value.strip()
        if not text:
            return
        inp.value = ""
        self.add_message("user", text)
        self.query_one("#ai-status", Label).update("Thinking...")
        self.run_worker(self._do_query(text))

    async def _do_query(self, prompt: str):
        cfg = self.app.config if hasattr(self.app, "config") else {}
        api_key = cfg.get("gemini_api_key", "")
        provider_name = cfg.get("ai_provider", "none")

        if provider_name == "gemini" and api_key:
            from ai.provider import GeminiClient
            client = GeminiClient(api_key)
            result = await client.chat(prompt)
            await client.close()
        else:
            result = "No AI provider configured. Press 's' to open Settings and add a Gemini API key (free at aistudio.google.com)."

        self.handle_result(result)

    def handle_result(self, text: str):
        self.add_message("assistant", text)
        self.query_one("#ai-status", Label).update("")

    def action_clear(self):
        self.query_one("#ai-messages", RichLog).clear()
        self.add_message("system", "Chat cleared.")
