"""Prompt-version-aware tool mappings for the shared agent loop.

The production Problem A handlers expose the v2 contracts.  Prompt v1 is an
evaluation treatment whose pre-authorisation response intentionally contains
less guidance, so that difference is implemented here rather than in the data
or tool layer.
"""

from __future__ import annotations

from collections.abc import Mapping

from src.schemas import ToolResult
from src.tools.base import ToolHandler
from src.tools.problem_a import TOOLS


def _adapt_preauthorisation_for_v1(handler: ToolHandler) -> ToolHandler:
    """Wrap the v2 handler with the v1 ``records`` return shape."""

    def v1_get_preauthorisation(*args: object, **kwargs: object) -> ToolResult:
        result = handler(*args, **kwargs)

        # Validation and lookup failures are shared across both versions.
        if not result.ok:
            return result

        data = result.data
        if not isinstance(data, dict):
            return result

        records: list[dict[str, object]] = []
        if data.get("found") is True:
            records.append(
                {
                    "preauth_id": data.get("preauth_id"),
                    "valid_from": data.get("valid_from"),
                    "valid_to": data.get("valid_to"),
                }
            )

        return ToolResult(ok=True, data={"records": records})

    return v1_get_preauthorisation


def get_versioned_tool_registry(
    prompt_version: str,
    base_registry: Mapping[str, ToolHandler] | None = None,
) -> dict[str, ToolHandler]:
    """Return a loop-ready registry matching the selected prompt contract.

    A copy is always returned, so selecting v1 never mutates the shared
    ``TOOLS`` mapping or a caller-provided registry.
    """

    if prompt_version not in {"v1", "v2"}:
        raise ValueError("prompt_version must be 'v1' or 'v2'")

    registry = dict(TOOLS if base_registry is None else base_registry)

    if prompt_version == "v1":
        handler = registry.get("get_preauthorisation")
        if handler is None:
            raise ValueError(
                "v1 requires a get_preauthorisation handler in the tool registry"
            )
        registry["get_preauthorisation"] = _adapt_preauthorisation_for_v1(handler)

    return registry
