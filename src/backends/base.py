"""The single backend seam used by the manual agent loop."""

from __future__ import annotations

from typing import Protocol

from src.schemas import ModelResponse


class ModelBackend(Protocol):
    """Implemented by both Divyansh's scripted backend and the live backend."""

    def generate(
        self,
        messages: list[dict[str, str]],
        *,
        model: str,
        temperature: float = 0.0,
    ) -> ModelResponse:
        ...
