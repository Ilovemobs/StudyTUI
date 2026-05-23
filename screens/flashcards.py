import random
from datetime import datetime, timedelta

from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.screen import Screen
from textual.widgets import Header, Label, Button, Static, Footer
from textual.binding import Binding
from database.schema import get_db


class FlashcardsScreen(Screen):
    BINDINGS = [
        Binding("space", "flip", "Flip"),
        Binding("1", "rate_1", "Again"),
        Binding("2", "rate_2", "Hard"),
        Binding("3", "rate_3", "Good"),
        Binding("4", "rate_4", "Easy"),
        Binding("n", "new_card", "New Card"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Label("", id="flashcard-subject"),
            Vertical(
                Label("", id="flashcard-question", classes="flashcard-question"),
                Label("", id="flashcard-answer", classes="flashcard-answer"),
                id="flashcard-card",
                classes="flashcard-card",
            ),
            Horizontal(
                Button("Again (1)", id="btn-again", variant="error"),
                Button("Hard (2)", id="btn-hard", variant="warning"),
                Button("Good (3)", id="btn-good", variant="primary"),
                Button("Easy (4)", id="btn-easy", variant="success"),
            ),
            Label("", id="flashcard-status"),
            id="content",
        )
        yield Footer()

    def on_mount(self):
        self.cards = []
        self.current_index = -1
        self.flipped = False
        self.load_cards()

    def load_cards(self):
        db = get_db()
        cur = db.execute(
            "SELECT id, question, answer, subject_id FROM flashcards WHERE next_review <= datetime('now') ORDER BY next_review LIMIT 50"
        )
        self.cards = [dict(r) for r in cur.fetchall()]
        db.close()
        random.shuffle(self.cards)
        self.current_index = 0 if self.cards else -1
        self.show_card()

    def show_card(self):
        if not self.cards or self.current_index < 0 or self.current_index >= len(self.cards):
            self.query_one("#flashcard-question", Label).update("No cards to review!")
            self.query_one("#flashcard-answer", Label).update("")
            self.query_one("#flashcard-status", Label).update("All caught up!")
            return
        card = self.cards[self.current_index]
        self.query_one("#flashcard-question", Label).update(card["question"])
        self.query_one("#flashcard-answer", Label).update("")
        self.query_one("#flashcard-status", Label).update(
            f"Card {self.current_index + 1} of {len(self.cards)}"
        )
        self.flipped = False

    def action_flip(self):
        if self.cards and 0 <= self.current_index < len(self.cards):
            card = self.cards[self.current_index]
            self.query_one("#flashcard-answer", Label).update(card["answer"])
            self.flipped = True

    def rate_card(self, quality: int):
        if not self.flipped or not self.cards or self.current_index < 0:
            return
        card = self.cards[self.current_index]
        self.apply_sm2(card["id"], quality)
        self.current_index += 1
        self.show_card()

    def apply_sm2(self, card_id: int, quality: int):
        db = get_db()
        cur = db.execute(
            "SELECT ease_factor, interval_days, repetitions FROM flashcards WHERE id = ?",
            (card_id,),
        )
        row = cur.fetchone()
        if not row:
            db.close()
            return

        ef, interval, reps = row["ease_factor"], row["interval_days"], row["repetitions"]

        if quality < 3:
            reps = 0
            interval = 0
        else:
            if reps == 0:
                interval = 1
            elif reps == 1:
                interval = 6
            else:
                interval = round(interval * ef)
            reps += 1

        ef = max(1.3, ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))

        next_review = (datetime.now() + timedelta(days=interval)).strftime("%Y-%m-%d %H:%M:%S")

        db.execute(
            "UPDATE flashcards SET ease_factor=?, interval_days=?, repetitions=?, next_review=?, last_review=datetime('now') WHERE id=?",
            (ef, interval, reps, next_review, card_id),
        )
        db.commit()
        db.close()

    def action_rate_1(self):
        self.rate_card(1)

    def action_rate_2(self):
        self.rate_card(2)

    def action_rate_3(self):
        self.rate_card(3)

    def action_rate_4(self):
        self.rate_card(4)

    def action_new_card(self):
        db = get_db()
        cur = db.execute("INSERT INTO flashcards (question, answer) VALUES (?, ?)",
                         ("New Question", "New Answer"))
        db.commit()
        card_id = cur.lastrowid
        db.close()
        self.load_cards()
