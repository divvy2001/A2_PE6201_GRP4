"""
Deterministic model backend for development and evaluation.
"""

from __future__ import annotations

from collections.abc import Sequence

from src.schemas import ModelResponse


class ScriptedBackend:
    """
    Returns predetermined model responses without calling an LLM.

    A ScriptedBackend maintains its own response index.

    Use `fresh()` to create a new backend with the same response sequence
    and the index reset to zero. This is useful when running multiple
    independent trials of the same evaluation case.
    """

    def __init__(self, responses: Sequence[str]):
        self.responses = list(responses)
        self.index = 0

    def generate(
        self,
        messages,
        *,
        model: str,
        temperature: float = 0.0,
    ) -> ModelResponse:
        """
        Return the next scripted response.

        Raises:
            RuntimeError: if all scripted responses have been consumed.
        """

        if self.index >= len(self.responses):
            raise RuntimeError(
                "SCRIPTED_BACKEND_EXHAUSTED: "
                "no response remaining"
            )

        text = self.responses[self.index]
        self.index += 1

        return ModelResponse(
            text=text,
            model=model,
            tokens_in=0,
            tokens_out=0,
            cost_usd=0.0,
            latency_ms=0.0,
        )

    def reset(self) -> None:
        """
        Reset this backend to the beginning of its response sequence.

        This is useful when the same backend instance needs to be reused
        deliberately.
        """

        self.index = 0

    def fresh(self) -> "ScriptedBackend":
        """
        Return a completely fresh backend with the same scripted responses.

        The new backend starts at index 0 and has independent state from
        this backend.
        """

        return ScriptedBackend(self.responses)
