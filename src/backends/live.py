"""Live LLM backend using an OpenAI-compatible API such as OpenRouter."""

from __future__ import annotations

import os
import time

from openai import OpenAI

from src.schemas import ModelResponse


class LiveBackend:
    """Calls a live LLM and converts its response to ModelResponse."""

    def __init__(
        self,
        *,
        base_url: str | None = None,
        api_key: str | None = None,
        price_in: float = 0.0,
        price_out: float = 0.0,
    ) -> None:
        self.base_url = base_url or os.environ.get(
            "OPENROUTER_BASE_URL",
            "https://openrouter.ai/api/v1",
        )
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")

        if not self.api_key:
            raise ValueError(
                "OPENROUTER_API_KEY is not set. "
                "Set the environment variable before running live mode."
            )

        self.price_in = price_in
        self.price_out = price_out

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )

    def generate(
        self,
        messages: list[dict[str, str]],
        *,
        model: str,
        temperature: float = 0.0,
    ) -> ModelResponse:
        """Generate one live model response for the current ReAct turn."""

        start_time = time.perf_counter()

        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
        )

        latency_ms = (time.perf_counter() - start_time) * 1000

        text = response.choices[0].message.content or ""

        usage = response.usage
        tokens_in = usage.prompt_tokens if usage else 0
        tokens_out = usage.completion_tokens if usage else 0

        cost_usd = (
            (tokens_in / 1_000_000) * self.price_in
            + (tokens_out / 1_000_000) * self.price_out
        )

        return ModelResponse(
            text=text,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            model=model,
            latency_ms=latency_ms,
            raw_id=response.id,
            cost_usd=cost_usd,
        )