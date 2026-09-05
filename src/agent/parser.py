"""Strict parser for one ActionBlock or one Final JSON object."""

from __future__ import annotations

import json
from typing import TypeAlias

from src.schemas import Action, ActionBlock, FinalDecision, SchemaValidationError


ParsedStep: TypeAlias = ActionBlock | FinalDecision


class StepParseError(ValueError):
    """Raised when a model turn is not one valid protocol object."""


def _remove_code_fence(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```") and stripped.endswith("```"):
        lines = stripped.splitlines()
        if len(lines) >= 3:
            return "\n".join(lines[1:-1]).strip()
    return stripped


def parse_step(text: str) -> ParsedStep:
    """Parse a model response while rejecting prose and ambiguous shapes."""
    try:
        payload = json.loads(_remove_code_fence(text))
    except (json.JSONDecodeError, TypeError) as error:
        raise StepParseError(f"PARSE_ERROR: response is not one JSON object: {error}") from error

    if not isinstance(payload, dict):
        raise StepParseError("PARSE_ERROR: top-level value must be an object")

    try:
        if payload.get("type") == "action_block":
            raw_actions = payload.get("actions")
            if not isinstance(raw_actions, list):
                raise SchemaValidationError("actions must be a list")
            summary = payload.get("reasoning_summary", "")
            if not isinstance(summary, str):
                raise SchemaValidationError("reasoning_summary must be a string")
            return ActionBlock(summary, tuple(Action.from_dict(item) for item in raw_actions))

        if payload.get("type") == "final":
            return FinalDecision.from_dict(payload.get("final"))
    except SchemaValidationError as error:
        raise StepParseError(f"PARSE_ERROR: {error}") from error

    raise StepParseError("PARSE_ERROR: type must be 'action_block' or 'final'")
