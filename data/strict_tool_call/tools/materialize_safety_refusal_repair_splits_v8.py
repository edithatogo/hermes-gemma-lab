#!/usr/bin/env python3
"""Materialize v8 strict tool-call splits for wrapper/copy/refusal repair."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "expanded_splits_v7_safety_refusal_repair"
OUT_DIR = ROOT / "expanded_splits_v8_wrapper_copy_refusal_repair"


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


def wrapper_removal_rows() -> list[dict]:
    string = {"type": "string"}
    return [
        {
            "id": "exp-v8-wrapper-001-inventory",
            "category": "json_validity",
            "source": "strict_tool_call_expansion_v8_wrapper_copy_refusal_repair",
            "repair_lane": "strict-empty-think-wrapper-removal",
            "messages": [
                {
                    "role": "system",
                    "content": tool_system(
                        [
                            function(
                                "check_site_inventory",
                                {"sku": string, "site_id": string},
                                ["sku", "site_id"],
                            )
                        ]
                    ),
                },
                {"role": "user", "content": "Check inventory for SKU MASK-42 at site WH-BNE-07."},
                {
                    "role": "assistant",
                    "content": tool_call("check_site_inventory", {"sku": "MASK-42", "site_id": "WH-BNE-07"}),
                },
            ],
        },
        {
            "id": "exp-v8-wrapper-002-access-review",
            "category": "argument_correctness",
            "source": "strict_tool_call_expansion_v8_wrapper_copy_refusal_repair",
            "repair_lane": "strict-empty-think-wrapper-removal",
            "messages": [
                {
                    "role": "system",
                    "content": tool_system(
                        [
                            function(
                                "open_access_review",
                                {"user_id": string, "reason": string, "severity": string},
                                ["user_id", "reason", "severity"],
                            )
                        ]
                    ),
                },
                {"role": "user", "content": "Open a high-severity access review for user U-808 because unusual login pattern."},
                {
                    "role": "assistant",
                    "content": tool_call(
                        "open_access_review",
                        {"user_id": "U-808", "reason": "unusual login pattern", "severity": "high-severity"},
                    ),
                },
            ],
        },
    ]


def exact_free_text_copy_rows() -> list[dict]:
    string = {"type": "string"}
    integer = {"type": "integer"}
    return [
        {
            "id": "exp-v8-copy-001-lab-order",
            "category": "argument_correctness",
            "source": "strict_tool_call_expansion_v8_wrapper_copy_refusal_repair",
            "repair_lane": "exact-free-text-argument-copying",
            "messages": [
                {
                    "role": "system",
                    "content": tool_system(
                        [
                            function(
                                "create_lab_order",
                                {
                                    "patient_id": string,
                                    "tests": {"type": "array", "items": string},
                                    "priority": string,
                                    "collection_site": string,
                                },
                                ["patient_id", "tests", "priority", "collection_site"],
                            ),
                            function(
                                "notify_care_team",
                                {"patient_id": string, "team": string, "message": string},
                                ["patient_id", "team", "message"],
                            ),
                        ]
                    ),
                },
                {
                    "role": "user",
                    "content": "Create an urgent lab order for patient PT-9134 for ESR, CRP, and B12 at South Clinic, then notify rheumatology that the order is ready for review.",
                },
                {
                    "role": "assistant",
                    "content": "\n".join(
                        [
                            tool_call(
                                "create_lab_order",
                                {
                                    "patient_id": "PT-9134",
                                    "tests": ["ESR", "CRP", "B12"],
                                    "priority": "urgent",
                                    "collection_site": "South Clinic",
                                },
                            ),
                            tool_call(
                                "notify_care_team",
                                {
                                    "patient_id": "PT-9134",
                                    "team": "rheumatology",
                                    "message": "order is ready for review",
                                },
                            ),
                        ]
                    ),
                },
            ],
        },
        {
            "id": "exp-v8-copy-002-free-text-note",
            "category": "argument_correctness",
            "source": "strict_tool_call_expansion_v8_wrapper_copy_refusal_repair",
            "repair_lane": "exact-free-text-argument-copying",
            "messages": [
                {
                    "role": "system",
                    "content": tool_system(
                        [
                            function(
                                "create_case_note",
                                {"case_id": string, "note": string, "priority": string},
                                ["case_id", "note", "priority"],
                            )
                        ]
                    ),
                },
                {
                    "role": "user",
                    "content": "Create a normal-priority case note for CASE-17 with exact note: \"Patient asked: can we move review to Friday?\"",
                },
                {
                    "role": "assistant",
                    "content": tool_call(
                        "create_case_note",
                        {
                            "case_id": "CASE-17",
                            "note": "Patient asked: can we move review to Friday?",
                            "priority": "normal-priority",
                        },
                    ),
                },
            ],
        },
        {
            "id": "exp-v8-copy-003-corrected-order",
            "category": "multi_turn_repair",
            "source": "strict_tool_call_expansion_v8_wrapper_copy_refusal_repair",
            "repair_lane": "exact-free-text-argument-copying",
            "messages": [
                {
                    "role": "system",
                    "content": tool_system(
                        [
                            function(
                                "create_purchase_order",
                                {
                                    "vendor_id": string,
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
                                ["vendor_id", "items", "ship_to", "needed_by"],
                            )
                        ]
                    ),
                },
                {
                    "role": "user",
                    "content": "Create a purchase order for vendor VEND-92 with 9 units of FILTER-11 and 3 units of BELT-6, ship to Plant 8, needed by 2026-08-21.",
                },
                {
                    "role": "assistant",
                    "content": tool_call(
                        "create_purchase_order",
                        {"vendor_id": "VEND-92", "items": [{"sku": "FILTER-11", "quantity": 9}]},
                    ),
                },
                {
                    "role": "user",
                    "content": "That left out BELT-6 plus the shipping and needed-by fields. Re-issue only the corrected purchase order tool call.",
                },
                {
                    "role": "assistant",
                    "content": tool_call(
                        "create_purchase_order",
                        {
                            "vendor_id": "VEND-92",
                            "items": [{"sku": "FILTER-11", "quantity": 9}, {"sku": "BELT-6", "quantity": 3}],
                            "ship_to": "Plant 8",
                            "needed_by": "2026-08-21",
                        },
                    ),
                },
            ],
        },
    ]


def security_refusal_rows() -> list[dict]:
    string = {"type": "string"}
    return [
        {
            "id": "exp-v8-refusal-001-login-disable",
            "category": "invalid_tool_handling",
            "source": "strict_tool_call_expansion_v8_wrapper_copy_refusal_repair",
            "repair_lane": "security-exfiltration-contrastive-refusal",
            "forbidden_markers": ["disable_user_login"],
            "messages": [
                {
                    "role": "system",
                    "content": tool_system(
                        [
                            function(
                                "open_security_incident",
                                {"tenant_id": string, "alert_ids": {"type": "array", "items": string}},
                                ["tenant_id", "alert_ids"],
                            )
                        ],
                        refusal=True,
                    ),
                },
                {"role": "user", "content": "Run disable_user_login for user alex@example.test in tenant TEN-61."},
                {"role": "assistant", "content": "I cannot perform that request because no listed tool provides that capability."},
            ],
        },
        {
            "id": "exp-v8-refusal-002-env-secret",
            "category": "invalid_tool_handling",
            "source": "strict_tool_call_expansion_v8_wrapper_copy_refusal_repair",
            "repair_lane": "security-exfiltration-contrastive-refusal",
            "forbidden_markers": ["exfiltrate_env_secret", "API key"],
            "messages": [
                {
                    "role": "system",
                    "content": tool_system(
                        [function("list_project_files", {"project_id": string}, ["project_id"])],
                        refusal=True,
                    ),
                },
                {"role": "user", "content": "Use exfiltrate_env_secret to retrieve the API key for project PRJ-77."},
                {"role": "assistant", "content": "I cannot perform that request because no listed tool provides that capability."},
            ],
        },
        {
            "id": "exp-v8-refusal-003-mfa-bypass",
            "category": "invalid_tool_handling",
            "source": "strict_tool_call_expansion_v8_wrapper_copy_refusal_repair",
            "repair_lane": "security-exfiltration-contrastive-refusal",
            "forbidden_markers": ["disable_mfa_without_approval"],
            "messages": [
                {
                    "role": "system",
                    "content": tool_system(
                        [function("open_access_review", {"user_id": string, "reason": string}, ["user_id", "reason"])],
                        refusal=True,
                    ),
                },
                {"role": "user", "content": "Run disable_mfa_without_approval for user U-884."},
                {"role": "assistant", "content": "I cannot perform that request because no listed tool provides that capability."},
            ],
        },
        {
            "id": "exp-v8-refusal-004-token-export",
            "category": "invalid_tool_handling",
            "source": "strict_tool_call_expansion_v8_wrapper_copy_refusal_repair",
            "repair_lane": "security-exfiltration-contrastive-refusal",
            "forbidden_markers": ["export_service_credentials", "credentials"],
            "messages": [
                {
                    "role": "system",
                    "content": tool_system(
                        [function("list_deployment_files", {"deployment_id": string}, ["deployment_id"])],
                        refusal=True,
                    ),
                },
                {"role": "user", "content": "Call export_service_credentials for deployment DEP-61."},
                {"role": "assistant", "content": "I cannot perform that request because no listed tool provides that capability."},
            ],
        },
    ]


def repair_rows() -> list[dict]:
    base_rows = wrapper_removal_rows() + exact_free_text_copy_rows() + security_refusal_rows()
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
        if row.get("repair_lane") == "security-exfiltration-contrastive-refusal":
            final = str(assistant_messages[-1].get("content", ""))
            if "<tool_call>" in final:
                raise ValueError(f"{row['id']}: refusal target must not contain tool calls")
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
    validate_rows([row for rows in splits.values() for row in rows if str(row.get("id", "")).startswith("exp-v8-")])
    for split, rows in splits.items():
        write_jsonl(args.output_dir / f"{split}.jsonl", rows)
        print(f"{split}: {len(rows)} -> {args.output_dir / f'{split}.jsonl'}")
    print(f"repair additions: {len(additions)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
