"""Validation rules for a multi-action model turn."""

from __future__ import annotations

import json
import re

from src.schemas import Action, ActionBlock, SchemaValidationError


CALL_ID_PATTERN = re.compile(r"^t\d{2,}-c\d{2,}$")
WRITE_TOOLS = {"issue_decision_letter"}


def action_signature(action: Action) -> str:
    """Canonical signature used by duplicate-action guards."""
    return f"{action.tool}:{json.dumps(action.args, sort_keys=True, separators=(',', ':'))}"


def validate_action_block(block: ActionBlock) -> None:
    """Reject ambiguous batches before any tool is executed."""
    call_ids: set[str] = set()
    signatures: set[str] = set()
    for action in block.actions:
        if not CALL_ID_PATTERN.fullmatch(action.call_id):
            raise SchemaValidationError(
                f"INVALID_ARGUMENT: call_id {action.call_id!r} must match t<turn>-c<index>"
            )
        if action.call_id in call_ids:
            raise SchemaValidationError(f"DUPLICATE_ACTION: repeated call_id {action.call_id}")
        signature = action_signature(action)
        if signature in signatures:
            raise SchemaValidationError(f"DUPLICATE_ACTION: repeated tool call {action.tool}")
        call_ids.add(action.call_id)
        signatures.add(signature)

    if len(block.actions) > 1 and any(a.tool in WRITE_TOOLS for a in block.actions):
        raise SchemaValidationError(
            "INVALID_ARGUMENT: issue_decision_letter must be the only action in its block"
        )


def can_execute_in_parallel(block: ActionBlock) -> bool:
    """Only independent, read-only actions may use the parallel executor."""
    return len(block.actions) > 1 and not any(a.tool in WRITE_TOOLS for a in block.actions)
