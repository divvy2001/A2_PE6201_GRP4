"""Shared tool contracts for Problem A."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from src.schemas import ToolResult


@dataclass(frozen=True)
class ToolSpec:
    """Metadata describing one tool that the agent may call."""

    name: str
    signature: str
    what: str
    input_contract: str
    return_contract: str
    fails_when: tuple[str, ...]
    irreversible: bool

    def __post_init__(self) -> None:
        required_text = {
            "name": self.name,
            "signature": self.signature,
            "what": self.what,
            "input_contract": self.input_contract,
            "return_contract": self.return_contract,
        }

        for field_name, value in required_text.items():
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"ToolSpec.{field_name} must be a non-empty string")


ToolHandler = Callable[..., ToolResult]