"""Utilities for loading versioned agent prompts."""

from pathlib import Path


PROMPT_DIR = Path(__file__).resolve().parent


def load_prompt(version: str) -> str:
    """Load a versioned system prompt."""

    prompt_path = PROMPT_DIR / f"prompt_{version}.txt"

    if not prompt_path.exists():
        raise FileNotFoundError(
            f"Prompt file not found for version '{version}': {prompt_path}"
        )

    prompt = prompt_path.read_text(encoding="utf-8").strip()

    if not prompt:
        raise ValueError(f"Prompt file is empty: {prompt_path}")

    return prompt
