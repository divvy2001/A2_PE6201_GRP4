"""Tool registration for the Group 4 Problem A agent."""

from __future__ import annotations

from collections.abc import Mapping

from src.tools.base import ToolHandler, ToolSpec


class ToolRegistry:
    """Store tool metadata and handlers, then expose a loop-ready mapping."""

    def __init__(self) -> None:
        self._handlers: dict[str, ToolHandler] = {}
        self._specs: dict[str, ToolSpec] = {}

    def register(self, spec: ToolSpec, handler: ToolHandler) -> None:
        """Register one uniquely named tool and its callable handler."""
        if spec.name in self._handlers:
            raise ValueError(f"Tool already registered: {spec.name}")

        if not callable(handler):
            raise TypeError(f"Handler for {spec.name} must be callable")

        self._handlers[spec.name] = handler
        self._specs[spec.name] = spec

    def as_mapping(self) -> Mapping[str, ToolHandler]:
        """Return the name-to-handler mapping required by run_agent()."""
        return dict(self._handlers)

    def get_spec(self, tool_name: str) -> ToolSpec:
        """Return metadata for one registered tool."""
        return self._specs[tool_name]

    def all_specs(self) -> tuple[ToolSpec, ...]:
        """Return all registered tool specifications in registration order."""
        return tuple(self._specs.values())