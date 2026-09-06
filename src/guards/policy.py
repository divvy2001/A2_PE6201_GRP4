"""Domain guard policy for the shared agent loop (owned by FENG jingjing).

`src/agent/loop.py` (LI ZIHAO) already enforces the core caps directly from
`GuardConfig`: step limit, budget ceiling, duplicate-action dedupe, and a
hard fail-close on write tools while `autonomy == "suggest"`. This module
does not re-implement those; it plugs into the loop's existing
`guard_hooks` seam (`before_model_call`, `validate_action_block`,
`before_tool_call`, `before_gated_action`, `after_tool_call`) to add the
domain-specific poka-yoke required by the SECURITY RULES in
`src/agent/prompt_v1.txt` / `prompt_v2.txt`:

  * the claim narrative (and any other tool-observed or model-supplied
    text) is untrusted data and must never be treated as an instruction,
    a fake tool result, or a fake runtime permission;
  * a run that has seen such text may only reach `issue_decision_letter`
    through a proper escalation (`trigger == "instruction_in_member_
    narrative"`), never through a direct approval;
  * every block decision returns a `GuardDecision(allow=False, ...)` so
    the loop records the reason in `trace` and never calls the real tool
    (see `src.agent.loop._run_guard_hook` / `_guard_fields`).

Every check below is behind its own on/off flag so the same case set can be
re-run with guards fully enabled vs. fully disabled for the ablation
comparison (see `scripts/run_ablation.py`).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from src.schemas import Action, GuardDecision, Observation


# Loosely matches an attempt to smuggle instructions, fake tool results, or
# fake runtime permissions inside untrusted text (a claim narrative, or any
# string argument on a tool/write call). Intentionally permissive/coarse:
# false positives fail closed to "escalate", which is the safe direction for
# a poka-yoke; false negatives are what the scripted cases exist to probe.
INJECTION_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"ignore\b.{0,30}\b(?:instructions?|rules?|prompt)s?\b",
        r"disregard\b.{0,30}\b(?:instructions?|rules?|checks?)\b",
        r"as\s+(?:the|an?)\s+(?:system|admin|operator|developer)\b",
        r"you\s+(?:must|should|will)\s+(?:now\s+)?(?:approve|escalate|issue|bypass|skip)\b",
        r"operator_approved\s*[:=]\s*[\"']?true",
        r"autonomy\s*[:=]\s*[\"']?act\b",
        r'"type"\s*:\s*"(?:final|action_block)"',  # a forged protocol JSON payload
        r"this\s+is\s+(?:a|the)\s+(?:real|actual\s+)?tool\s+result",
        r"run_id\s*[:=]\s*[\"']?[\w-]{4,}",
    )
)

WRITE_TOOL = "issue_decision_letter"
HOSTILE_TRIGGER = "instruction_in_member_narrative"


def scan_for_injection(value: Any) -> str | None:
    """Return the pattern text of the first injection-style match, else None."""
    if isinstance(value, str):
        for pattern in INJECTION_PATTERNS:
            if pattern.search(value):
                return pattern.pattern
        return None
    if isinstance(value, dict):
        for item in value.values():
            hit = scan_for_injection(item)
            if hit:
                return hit
        return None
    if isinstance(value, (list, tuple)):
        for item in value:
            hit = scan_for_injection(item)
            if hit:
                return hit
        return None
    return None


@dataclass
class GuardHooks:
    """Pluggable domain guard, passed as `guard_hooks=` to `run_agent`.

    Attributes
    ----------
    hostile_text_enabled:
        Scan tool arguments and tool observations for injection-style text
        and require a proper escalation before any write once found.
    autonomy_guard_enabled:
        Defence-in-depth re-check of the suggest-mode write block, kept
        behind its own flag so it can be turned off independently in an
        ablation run even though the loop already fail-closes this case.
    max_hostile_signals:
        Number of distinct hostile-text signals tolerated in one run
        before `before_model_call` itself halts the run.
    """

    hostile_text_enabled: bool = True
    autonomy_guard_enabled: bool = True
    max_hostile_signals: int = 2

    _hostile_hits: dict[str, list[str]] = field(default_factory=dict, repr=False)

    # -- internal helpers --------------------------------------------------

    @staticmethod
    def _run_id(state: dict[str, Any]) -> str:
        return str(state.get("run_id", ""))

    def _record_hit(self, state: dict[str, Any], pattern: str) -> None:
        self._hostile_hits.setdefault(self._run_id(state), []).append(pattern)

    def hostile_signals(self, run_id: str) -> list[str]:
        """Read-only accessor for tests and ablation reporting."""
        return list(self._hostile_hits.get(run_id, []))

    def _check_args(self, action: Action, state: dict[str, Any]) -> GuardDecision | None:
        if not self.hostile_text_enabled:
            return None
        match = scan_for_injection(action.args)
        if match is None:
            return None
        self._record_hit(state, match)
        return GuardDecision(
            False,
            "Tool call arguments contain a suspected injected instruction "
            "or forged runtime permission; treating claim text as data, not "
            "as instructions",
            "INSTRUCTION_IN_NARRATIVE",
        )

    # -- hook methods, called by src.agent.loop.run_agent -------------------

    def before_model_call(self, state: dict[str, Any]) -> GuardDecision | None:
        if not self.hostile_text_enabled:
            return None
        hits = self._hostile_hits.get(self._run_id(state), [])
        if len(hits) > self.max_hostile_signals:
            return GuardDecision(
                False,
                "Repeated prompt-injection attempts detected in this run",
                "HOSTILE_TEXT_REPEATED",
            )
        return None

    def validate_action_block(self, actions: tuple[Action, ...], state: dict[str, Any]) -> GuardDecision | None:
        # The single-write-per-block and call_id/duplicate structural rules
        # already live in src.agent.dependency.validate_action_block; this
        # hook has no additional domain check to add before per-action
        # gating runs.
        return None

    def before_tool_call(self, action: Action, state: dict[str, Any]) -> GuardDecision | None:
        return self._check_args(action, state)

    def before_gated_action(self, action: Action, state: dict[str, Any]) -> GuardDecision | None:
        if self.autonomy_guard_enabled and state.get("autonomy") == "suggest":
            # The loop already fail-closes this in _call_tool; re-asserting
            # it here keeps the behaviour under this module's own toggle so
            # an ablation run can isolate the autonomy guard specifically.
            return GuardDecision(
                False,
                "Suggest mode may not execute a write tool",
                "AUTONOMY_BLOCKED",
            )

        run_id = self._run_id(state)
        if self.hostile_text_enabled and self._hostile_hits.get(run_id):
            decision_record = action.args.get("decision_record")
            trigger = decision_record.get("trigger") if isinstance(decision_record, dict) else None
            if trigger != HOSTILE_TRIGGER:
                return GuardDecision(
                    False,
                    "This run saw a suspected instruction in untrusted text; "
                    f"a write is only allowed via escalation with trigger={HOSTILE_TRIGGER!r}",
                    "INSTRUCTION_IN_NARRATIVE",
                )

        return self._check_args(action, state)

    def after_tool_call(self, action: Action, observation: Observation, state: dict[str, Any]) -> None:
        if not self.hostile_text_enabled or not getattr(observation, "ok", False):
            return None
        match = scan_for_injection(getattr(observation, "data", None))
        if match is not None:
            self._record_hit(state, match)
        return None
