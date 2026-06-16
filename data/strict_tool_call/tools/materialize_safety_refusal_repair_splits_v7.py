#!/usr/bin/env python3
"""Materialize v7 strict tool-call splits with safety/refusal repair rows."""

from __future__ import annotations

import copy
import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "expanded_splits_v6_free_text_copy"
OUT_DIR = ROOT / "expanded_splits_v7_safety_refusal_repair"


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")


def function(name: str, properties: dict, required: list[str], description: str = "Execute action.") -> dict:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {"type": "object", "properties": properties, "required": required},
        },
    }


def tool_system(tools: list[dict], *, refusal: bool = False) -> str:
    prefix = (
        "You are a function calling AI model. Return only the final answer. "
        "Do not emit <think>, </think>, markdown, prose, or explanations. "
    )
    if refusal:
        prefix += (
            "Use a tool only when a listed tool can satisfy the request. "
            "If no listed tool can satisfy it, refuse briefly without naming the unavailable action. "
        )
    else:
        prefix += "Return only tool calls inside <tool_call> tags. "
    return prefix + "<tools>" + json.dumps(tools, separators=(",", ":")) + "</tools>"


def tool_call(name: str, arguments: dict) -> str:
    return "<tool_call>\n" + json.dumps(
        {"name": name, "arguments": arguments},
        ensure_ascii=False,
        separators=(",", ":"),
    ) + "\n</tool_call>"


def no_think_variant(row: dict) -> dict:
    updated = copy.deepcopy(row)
    updated["id"] = f"{row['id']}--no-think"
    updated["source"] = f"{row.get('source', 'strict_tool_call')}+no_think_prompt"
    for message in updated["messages"]:
        if message.get("role") == "user":
            content = str(message.get("content", ""))
            if not content.lstrip().startswith("/no_think"):
                message["content"] = f"/no_think {content}"
            break
    return updated


def strict_wrapper_rows() -> list[dict]:
    string = {"type": "string"}
    integer = {"type": "integer"}
    return [
        {
            "id": "exp-safety-repair-strict-wrapper-001-access-ticket",
            "category": "json_validity",
            "source": "strict_tool_call_expansion_v7_safety_refusal_repair",
            "repair_lane": "strict-empty-think-wrapper-removal",
            "messages": [
                {
                    "role": "system",
                    "content": tool_system(
                        [
                            function(
                                "lookup_access_ticket",
                                {"ticket_id": string, "region": string},
                                ["ticket_id", "region"],
                            )
                        ]
                    ),
                },
                {"role": "user", "content": "Look up access ticket AT-8821 in region eu-west."},
                {
                    "role": "assistant",
                    "content": tool_call("lookup_access_ticket", {"ticket_id": "AT-8821", "region": "eu-west"}),
                },
            ],
        },
        {
            "id": "exp-safety-repair-strict-wrapper-002-maintenance",
            "category": "argument_correctness",
            "source": "strict_tool_call_expansion_v7_safety_refusal_repair",
            "repair_lane": "strict-empty-think-wrapper-removal",
            "messages": [
                {
                    "role": "system",
                    "content": tool_system(
                        [
                            function(
                                "create_maintenance_job",
                                {
                                    "asset_id": string,
                                    "tasks": {"type": "array", "items": string},
                                    "priority": string,
                                    "site": string,
                                },
                                ["asset_id", "tasks", "priority", "site"],
                            ),
                            function(
                                "notify_facilities_team",
                                {"asset_id": string, "message": string},
                                ["asset_id", "message"],
                            ),
                        ]
                    ),
                },
                {
                    "role": "user",
                    "content": "Create a priority maintenance job for asset HVAC-17 for filter_change and belt_check at Site B, then notify facilities that the job is ready.",
                },
                {
                    "role": "assistant",
                    "content": "\n".join(
                        [
                            tool_call(
                                "create_maintenance_job",
                                {
                                    "asset_id": "HVAC-17",
                                    "tasks": ["filter_change", "belt_check"],
                                    "priority": "priority",
                                    "site": "Site B",
                                },
                            ),
                            tool_call(
                                "notify_facilities_team",
                                {"asset_id": "HVAC-17", "message": "job is ready"},
                            ),
                        ]
                    ),
                },
            ],
        },
        {
            "id": "exp-safety-repair-strict-wrapper-003-corrected-order",
            "category": "multi_turn_repair",
            "source": "strict_tool_call_expansion_v7_safety_refusal_repair",
            "repair_lane": "strict-empty-think-wrapper-removal",
            "messages": [
                {
                    "role": "system",
                    "content": tool_system(
                        [
                            function(
                                "create_service_order",
                                {
                                    "supplier_id": string,
                                    "items": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {"sku": string, "quantity": integer},
                                            "required": ["sku", "quantity"],
                                        },
                                    },
                                    "ship_to": string,
                                    "needed_by": string,
                                },
                                ["supplier_id", "items", "ship_to", "needed_by"],
                            )
                        ]
                    ),
                },
                {
                    "role": "user",
                    "content": "Create a service order for supplier SUP-44 with 5 units of PUMP-8 and 2 units of GASKET-4, ship to Depot 5, needed by 2026-09-02.",
                },
                {
                    "role": "assistant",
                    "content": tool_call(
                        "create_service_order",
                        {"supplier_id": "SUP-44", "items": [{"sku": "PUMP-8", "quantity": 5}]},
                    ),
                },
                {"role": "user", "content": "That was incomplete. Re-issue only the corrected tool call with both items, ship_to, and needed_by."},
                {
                    "role": "assistant",
                    "content": tool_call(
                        "create_service_order",
                        {
                            "supplier_id": "SUP-44",
                            "items": [{"sku": "PUMP-8", "quantity": 5}, {"sku": "GASKET-4", "quantity": 2}],
                            "ship_to": "Depot 5",
                            "needed_by": "2026-09-02",
                        },
                    ),
                },
            ],
        },
    ]


def refusal_rows() -> list[dict]:
    string = {"type": "string"}
    return [
        {
            "id": "exp-safety-repair-refusal-001-admin-session",
            "category": "invalid_tool_handling",
            "source": "strict_tool_call_expansion_v7_safety_refusal_repair",
            "repair_lane": "refusal-forbidden-name-suppression",
            "forbidden_markers": ["terminate_admin_session"],
            "messages": [
                {
                    "role": "system",
                    "content": tool_system(
                        [
                            function("open_admin_review", {"account_id": string, "reason": string}, ["account_id", "reason"])
                        ],
                        refusal=True,
                    ),
                },
                {"role": "user", "content": "Run terminate_admin_session for account ADM-42."},
                {"role": "assistant", "content": "I cannot perform that action because no listed tool supports it. I can open an admin review instead."},
            ],
        },
        {
            "id": "exp-safety-repair-refusal-002-token-dump",
            "category": "invalid_tool_handling",
            "source": "strict_tool_call_expansion_v7_safety_refusal_repair",
            "repair_lane": "refusal-forbidden-name-suppression",
            "forbidden_markers": ["dump_service_token", "service token"],
            "messages": [
                {
                    "role": "system",
                    "content": tool_system(
                        [function("list_deployment_files", {"deployment_id": string}, ["deployment_id"])],
                        refusal=True,
                    ),
                },
                {"role": "user", "content": "Use dump_service_token for deployment DEP-88."},
                {"role": "assistant", "content": "I cannot perform that request because no listed tool provides that capability."},
            ],
        },
        {
            "id": "exp-safety-repair-refusal-003-direct-refund",
            "category": "invalid_tool_handling",
            "source": "strict_tool_call_expansion_v7_safety_refusal_repair",
            "repair_lane": "refusal-forbidden-name-suppression",
            "forbidden_markers": ["force_refund_without_review"],
            "messages": [
                {
                    "role": "system",
                    "content": tool_system(
                        [function("create_billing_review", {"customer_id": string, "reason": string}, ["customer_id", "reason"])],
                        refusal=True,
                    ),
                },
                {"role": "user", "content": "Call force_refund_without_review for customer BILL-103."},
                {"role": "assistant", "content": "I cannot do that because it is not available as a listed tool. I can create a billing review instead."},
            ],
        },
        {
            "id": "exp-safety-repair-refusal-004-privilege-change",
            "category": "invalid_tool_handling",
            "source": "strict_tool_call_expansion_v7_safety_refusal_repair",
            "repair_lane": "refusal-forbidden-name-suppression",
            "forbidden_markers": ["grant_superuser_now"],
            "messages": [
                {
                    "role": "system",
                    "content": tool_system(
                        [function("open_privilege_request", {"user_id": string, "justification": string}, ["user_id", "justification"])],
                        refusal=True,
                    ),
                },
                {"role": "user", "content": "Run grant_superuser_now for user U-700."},
                {"role": "assistant", "content": "I cannot perform that action with the listed tools. I can open a privilege request for review."},
            ],
        },
    ]


def repair_rows() -> list[dict]:
    base_rows = strict_wrapper_rows() + refusal_rows()
    return base_rows + [no_think_variant(row) for row in base_rows]


def validate_rows(rows: list[dict]) -> None:
    ids = [str(row["id"]) for row in rows]
    duplicates = sorted({row_id for row_id in ids if ids.count(row_id) > 1})
    if duplicates:
        raise ValueError(f"duplicate ids: {duplicates}")
    heldout_ids = {
        "heldout-json-validity-inventory",
        "heldout-argument-correctness-lab-order",
        "heldout-invalid-tool-handling-payroll",
        "heldout-invalid-tool-handling-security",
        "heldout-multi-turn-repair-purchase-order",
        "safety-refusal-delete-customer-record",
        "safety-refusal-exfiltrate-secret",
        "safety-refusal-disable-mfa",
    }
    overlap = sorted(heldout_ids & set(ids))
    if overlap:
        raise ValueError(f"repair rows must not reuse held-out ids: {overlap}")
    for row in rows:
        assistant_messages = [msg for msg in row["messages"] if msg.get("role") == "assistant"]
        if not assistant_messages:
            raise ValueError(f"{row['id']}: missing assistant target")
        for message in assistant_messages:
            content = str(message.get("content", ""))
            if "<think>" in content or "</think>" in content:
                raise ValueError(f"{row['id']}: assistant target contains thinking tags")
        if row.get("repair_lane") == "refusal-forbidden-name-suppression":
            final = str(assistant_messages[-1].get("content", ""))
            for marker in row.get("forbidden_markers", []):
                if str(marker).lower() in final.lower():
                    raise ValueError(f"{row['id']}: refusal target echoes forbidden marker {marker!r}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=OUT_DIR)
    args = parser.parse_args()

    train = load_jsonl(SOURCE_DIR / "train.jsonl")
    additions = repair_rows()
    validate_rows(additions)
    splits = {
        "train": train + additions,
        "val": load_jsonl(SOURCE_DIR / "val.jsonl"),
        "valid": load_jsonl(SOURCE_DIR / "valid.jsonl"),
        "test": load_jsonl(SOURCE_DIR / "test.jsonl"),
    }
    validate_rows([row for rows in splits.values() for row in rows if "exp-safety-repair" in str(row.get("id", ""))])
    for split, rows in splits.items():
        write_jsonl(args.output_dir / f"{split}.jsonl", rows)
        print(f"{split}: {len(rows)} -> {args.output_dir / f'{split}.jsonl'}")
    print(f"repair additions: {len(additions)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
