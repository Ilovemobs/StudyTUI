import json
from urllib.parse import quote

import aiohttp


GEMINI_MODELS = {
    "flash": "gemini-2.0-flash",
    "flash-lite": "gemini-2.0-flash-lite",
    "pro": "gemini-2.0-pro",
}

SYSTEM_PROMPTS = {
    "chat": "You are a helpful AI tutor. Answer questions clearly and concisely.",
    "summarize": "Summarize the following text into key points. Be concise.",
    "flashcard": "Generate flashcards from the following text. Format each as Q: <question> | A: <answer>, one per line.",
    "explain": "Explain the following concept as simply as possible.",
    "quiz": "Generate 5 practice quiz questions from the following text. Include answers.",
    "grammar": "Check the following text for grammar and style issues. Return a corrected version and brief notes.",
}


class GeminiClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        self._session = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self):
        if self._session:
            await self._session.close()
            self._session = None

    async def chat(self, prompt: str, system: str = "chat") -> str:
        url = f"{self.base_url}/gemini-2.0-flash:generateContent?key={self.api_key}"
        sys_prompt = SYSTEM_PROMPTS.get(system, SYSTEM_PROMPTS["chat"])
        full_prompt = f"{sys_prompt}\n\n{prompt}"

        session = await self._get_session()
        try:
            async with session.post(
                url,
                json={"contents": [{"parts": [{"text": full_prompt}]}]},
                timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            return parts[0].get("text", "No response text.")
                    return "No response from AI."
                text = await resp.text()
                return f"API error: {resp.status} — {text[:200]}"
        except Exception as e:
            return f"Error: {e}"

    async def generate_flashcards(self, text: str) -> list[tuple[str, str]]:
        result = await self.chat(text, system="flashcard")
        cards = []
        for line in result.strip().split("\n"):
            line = line.strip()
            if "|" in line:
                parts = line.split("|")
                q = parts[0].replace("Q:", "").replace("q:", "").strip()
                a = parts[1].replace("A:", "").replace("a:", "").strip()
                if q and a:
                    cards.append((q, a))
        return cards

    async def summarize(self, text: str) -> str:
        return await self.chat(text, system="summarize")


class AIProvider:
    def __init__(self, config: dict):
        self.config = config
        self.gemini = None
        provider = config.get("ai_provider", "none")
        key = config.get("gemini_api_key", "")
        if provider == "gemini" and key:
            self.gemini = GeminiClient(key)

    def is_available(self) -> bool:
        return self.gemini is not None

    async def chat(self, prompt: str) -> str:
        if self.gemini:
            return await self.gemini.chat(prompt)
        return "AI not configured. Add a Gemini API key in Settings."

    async def generate_flashcards(self, text: str) -> list[tuple[str, str]]:
        if self.gemini:
            return await self.gemini.generate_flashcards(text)
        return []

    async def summarize(self, text: str) -> str:
        if self.gemini:
            return await self.gemini.summarize(text)
        return "AI not configured."

    async def close(self):
        if self.gemini:
            await self.gemini.close()
