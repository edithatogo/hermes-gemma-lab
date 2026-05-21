#!/usr/bin/env python3
"""Build strict format-guard examples for Qwen tool-call tuning."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "raw" / "expansion_seed_v2.jsonl"


def tool(name: str, properties: dict, required: list[str]) -> dict:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": f"Execute {name.replace('_', ' ')}.",
            "parameters": {"type": "object", "properties": properties, "required": required},
        },
    }


def system(tools: list[dict], invalid: bool = False) -> dict:
    valid_clause = " when a valid tool exists" if invalid else ""
    return {
        "role": "system",
        "content": (
            "You are a function calling AI model. Return only the final answer. "
            "Do not emit <think>, </think>, markdown, prose, or explanations. "
            f"Return only tool calls inside <tool_call> tags{valid_clause}. "
            f"<tools>{json.dumps(tools, separators=(',', ':'))}</tools>"
        ),
    }


def call(name: str, arguments: dict) -> str:
    return "<tool_call>\n" + json.dumps({"name": name, "arguments": arguments}, separators=(",", ":")) + "\n</tool_call>"


S = {"type": "string"}
I = {"type": "integer"}
B = {"type": "boolean"}
STRINGS = {"type": "array", "items": {"type": "string"}}


def example(example_id: str, category: str, tools: list[dict], turns: list[dict], invalid: bool = False) -> dict:
    return {
        "id": example_id,
        "category": category,
        "source": "strict_tool_call_expansion_v2_format_guard",
        "messages": [system(tools, invalid=invalid), *turns],
    }


EXAMPLES = [
    example(
        "exp-format-guard-001-contract",
        "format_guard",
        [tool("open_contract_review", {"contract_id": S, "queue": S, "urgent": B}, ["contract_id", "queue", "urgent"])],
        [
            {"role": "user", "content": "Open an urgent legal review for contract CTR-884 in the vendor queue. Return no thinking tags."},
            {"role": "assistant", "content": call("open_contract_review", {"contract_id": "CTR-884", "queue": "vendor", "urgent": True})},
        ],
    ),
    example(
        "exp-format-guard-002-device",
        "format_guard",
        [tool("lock_device", {"device_id": S, "reason": S}, ["device_id", "reason"])],
        [
            {"role": "user", "content": "Lock device DEV-41 because it failed attestation. Output only the tool call."},
            {"role": "assistant", "content": call("lock_device", {"device_id": "DEV-41", "reason": "failed attestation"})},
        ],
    ),
    example(
        "exp-format-guard-003-access",
        "format_guard",
        [tool("grant_repository_access", {"repo": S, "user": S, "role": S}, ["repo", "user", "role"])],
        [
            {"role": "user", "content": "Grant alex@example.test maintainer access to repo hermes-runtime. No prose."},
            {"role": "assistant", "content": call("grant_repository_access", {"repo": "hermes-runtime", "user": "alex@example.test", "role": "maintainer"})},
        ],
    ),
    example(
        "exp-format-guard-004-alert",
        "format_guard",
        [tool("acknowledge_alert", {"alert_id": S, "owner": S}, ["alert_id", "owner"])],
        [
            {"role": "user", "content": "Acknowledge alert ALT-602 for owner nora@example.test. Do not wrap the answer."},
            {"role": "assistant", "content": call("acknowledge_alert", {"alert_id": "ALT-602", "owner": "nora@example.test"})},
        ],
    ),
    example(
        "exp-format-guard-005-two-call",
        "format_guard",
        [
            tool("create_change_ticket", {"service": S, "summary": S}, ["service", "summary"]),
            tool("schedule_change_window", {"service": S, "start_time": S, "duration_minutes": I}, ["service", "start_time", "duration_minutes"]),
        ],
        [
            {"role": "user", "content": "Create a change ticket for billing-api summary patch TLS cert, then schedule billing-api at 2026-07-12T21:00:00+10:00 for 30 minutes."},
            {"role": "assistant", "content": call("create_change_ticket", {"service": "billing-api", "summary": "patch TLS cert"}) + "\n" + call("schedule_change_window", {"service": "billing-api", "start_time": "2026-07-12T21:00:00+10:00", "duration_minutes": 30})},
        ],
    ),
    example(
        "exp-format-guard-006-batch",
        "format_guard",
        [tool("tag_assets", {"asset_ids": STRINGS, "tag": S}, ["asset_ids", "tag"])],
        [
            {"role": "user", "content": "Tag assets A-1, A-2, and A-3 with inspection_due. Return exactly one tool call."},
            {"role": "assistant", "content": call("tag_assets", {"asset_ids": ["A-1", "A-2", "A-3"], "tag": "inspection_due"})},
        ],
    ),
    example(
        "exp-format-guard-007-repair",
        "format_guard",
        [tool("update_runbook_step", {"runbook_id": S, "step": I, "text": S}, ["runbook_id", "step", "text"])],
        [
            {"role": "user", "content": "Update step 4 in runbook RB-19 to say verify rollback snapshot."},
            {"role": "assistant", "content": "<tool_call>{\"name\":\"update_runbook_step\",\"arguments\":{\"runbook_id\":\"RB-19\",\"step\":4}}</tool_call>"},
            {"role": "user", "content": "That omitted the text. Re-issue only the corrected tool call, without thinking tags."},
            {"role": "assistant", "content": call("update_runbook_step", {"runbook_id": "RB-19", "step": 4, "text": "verify rollback snapshot"})},
        ],
    ),
    example(
        "exp-format-guard-008-invalid",
        "format_guard",
        [tool("lookup_access_request", {"request_id": S}, ["request_id"])],
        [
            {"role": "user", "content": "Use approve_access_request for request AR-904."},
            {"role": "assistant", "content": "I cannot call approve_access_request because that tool is not available."},
        ],
        invalid=True,
    ),
]


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as handle:
        for row in EXAMPLES:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
    print(f"wrote {len(EXAMPLES)} rows to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
