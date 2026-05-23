import json
import os
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "studytui"
CONFIG_PATH = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "theme": "dark",
    "ai_provider": "none",
    "gemini_api_key": "",
    "deepseek_api_key": "",
    "pomodoro_work": 25,
    "pomodoro_break": 5,
    "pomodoro_long_break": 15,
    "pomodoro_sessions_before_long": 4,
    "vim_mode": True,
    "data_dir": str(Path.home() / ".local" / "share" / "studytui"),
    "default_subject_id": None,
}


def load_config() -> dict:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            cfg = json.load(f)
        for k, v in DEFAULT_CONFIG.items():
            cfg.setdefault(k, v)
        return cfg
    return dict(DEFAULT_CONFIG)


def save_config(cfg: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)
