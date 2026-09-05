"""Shared, provider-neutral contracts for the Group 4 agent.

These dataclasses are intentionally standard-library only so notebooks, scripted
tests and live backends all exchange the same shapes without extra dependencies.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal


SCHEMA_VERSION = "1.0"
Decision = Literal["approve_in_principle", "request_document", "escalate"]
RunStatus = Literal["completed", "halted", "failed"]


class SchemaValidationError(ValueError):
    """Raised when an object does not satisfy the frozen public contract."""


@dataclass(frozen=True)
class ErrorDetail:
    code: str
    message: str


@dataclass(frozen=True)
class ToolResult:
    ok: bool
    data: Any = None
    error: ErrorDetail | None = None

    def __post_init__(self) -> None:
        if self.ok and self.error is not None:
            raise SchemaValidationError("A successful ToolResult cannot contain error")
        if not self.ok and self.error is None:
            raise SchemaValidationError("A failed ToolResult requires error")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ModelResponse:
    text: str
    tokens_in: int
    tokens_out: int
    model: str
    latency_ms: float | None = None
    raw_id: str | None = None
    # Optional extension needed by the loop's budget ceiling. A backend that does
    # not know the price may leave it at zero; the cost module can enrich it later.
    cost_usd: float = 0.0

    def __post_init__(self) -> None:
        if not isinstance(self.text, str) or not self.text.strip():
            raise SchemaValidationError("ModelResponse.text must be non-empty")
        if self.tokens_in < 0 or self.tokens_out < 0 or self.cost_usd < 0:
            raise SchemaValidationError("Token counts and cost must be non-negative")


@dataclass(frozen=True)
class Action:
    call_id: str
    tool: str
    args: dict[str, Any]

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "Action":
        if not isinstance(value, dict):
            raise SchemaValidationError("Each action must be an object")
        call_id, tool, args = value.get("call_id"), value.get("tool"), value.get("args")
        if not isinstance(call_id, str) or not call_id.strip():
            raise SchemaValidationError("Action.call_id must be a non-empty string")
        if not isinstance(tool, str) or not tool.strip():
            raise SchemaValidationError("Action.tool must be a non-empty string")
        if not isinstance(args, dict):
            raise SchemaValidationError("Action.args must be an object")
        return cls(call_id=call_id, tool=tool, args=args)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ActionBlock:
    reasoning_summary: str
    actions: tuple[Action, ...]

    def __post_init__(self) -> None:
        if not self.actions:
            raise SchemaValidationError("ActionBlock.actions cannot be empty")

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "action_block",
            "reasoning_summary": self.reasoning_summary,
            "actions": [action.to_dict() for action in self.actions],
        }


@dataclass(frozen=True)
class Observation:
    call_id: str
    tool: str
    ok: bool
    data: Any = None
    error: ErrorDetail | None = None

    def __post_init__(self) -> None:
        if self.ok and self.error is not None:
            raise SchemaValidationError("A successful Observation cannot contain error")
        if not self.ok and self.error is None:
            raise SchemaValidationError("A failed Observation requires error")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class FinalDecision:
    decision: Decision
    trigger: str | None
    missing: str | None
    escalate_to: str | None
    line_dispositions: tuple[dict[str, Any], ...]
    approved_total: float
    refused_total: float
    evidence: tuple[str, ...]

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "FinalDecision":
        if not isinstance(value, dict):
            raise SchemaValidationError("final must be an object")
        decision = value.get("decision")
        if decision not in {"approve_in_principle", "request_document", "escalate"}:
            raise SchemaValidationError(f"Unsupported final decision: {decision!r}")
        trigger = value.get("trigger")
        missing = value.get("missing")
        escalate_to = value.get("escalate_to")
        dispositions = value.get("line_dispositions", [])
        evidence = value.get("evidence", [])
        approved = value.get("approved_total", 0)
        refused = value.get("refused_total", 0)
        if decision == "escalate" and (not trigger or not escalate_to):
            raise SchemaValidationError("escalate requires trigger and escalate_to")
        if decision == "request_document" and not missing:
            raise SchemaValidationError("request_document requires missing")
        if not isinstance(dispositions, list) or not all(isinstance(x, dict) for x in dispositions):
            raise SchemaValidationError("line_dispositions must be a list of objects")
        if not isinstance(evidence, list) or not all(isinstance(x, str) for x in evidence):
            raise SchemaValidationError("evidence must be a list of strings")
        if isinstance(approved, bool) or not isinstance(approved, (int, float)) or approved < 0:
            raise SchemaValidationError("approved_total must be a non-negative number")
        if isinstance(refused, bool) or not isinstance(refused, (int, float)) or refused < 0:
            raise SchemaValidationError("refused_total must be a non-negative number")
        return cls(
            decision=decision,
            trigger=trigger,
            missing=missing,
            escalate_to=escalate_to,
            line_dispositions=tuple(dispositions),
            approved_total=float(approved),
            refused_total=float(refused),
            evidence=tuple(dict.fromkeys(evidence)),
        )

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["line_dispositions"] = list(self.line_dispositions)
        value["evidence"] = list(self.evidence)
        return value


@dataclass(frozen=True)
class TraceEvent:
    seq: int
    turn: int
    event_type: str
    payload: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class GuardDecision:
    allow: bool
    reason: str | None = None
    cap_fired: str | None = None


@dataclass(frozen=True)
class GuardConfig:
    step_limit_enabled: bool = True
    budget_enabled: bool = True
    dedupe_enabled: bool = True
    autonomy_enabled: bool = True


@dataclass
class RunResult:
    schema_version: str
    run_id: str
    case_id: str
    backend: str
    model: str
    prompt_version: Literal["v1", "v2"]
    mode: Literal["sequential", "parallel"]
    autonomy: Literal["suggest", "confirm", "act"]
    trial: int
    status: RunStatus
    final: FinalDecision | None
    error: dict[str, Any] | None
    turns: int
    tool_calls: int
    tokens_in: int
    tokens_out: int
    cost_usd: float
    latency_ms: float | None
    caps_fired: list[str] = field(default_factory=list)
    tool_trace: list[dict[str, Any]] = field(default_factory=list)
    trace: list[TraceEvent] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            **asdict(self),
            "final": self.final.to_dict() if self.final else None,
            "trace": [event.to_dict() for event in self.trace],
        }
