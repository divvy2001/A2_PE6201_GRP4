"""Deterministic model backend for development and evaluation."""

from __future__ import annotations

from collections.abc import Sequence

from src.schemas import ModelResponse


class ScriptedBackend:
    """Returns predetermined model responses without calling an LLM."""

    def __init__(self, responses: Sequence[str]):
        self.responses = list(responses)
        self.index = 0

    def generate(
        self,
        messages: list[dict[str, str]],
        *,
        model: str,
        temperature: float = 0.0,
    ) -> ModelResponse:
        """Return the next scripted response."""

        if self.index >= len(self.responses):
            raise RuntimeError(
                "SCRIPTED_BACKEND_EXHAUSTED: no response remaining"
            )

        text = self.responses[self.index]
        self.index += 1

        return ModelResponse(
            text=text,
            model=model,
            tokens_in=0,
            tokens_out=0,
            latency_ms=0.0,
            cost_usd=0.0,
        )