#!/usr/bin/env python3
"""Materialize v6 strict tool-call splits with free-text copy repair rows."""

from __future__ import annotations

import copy
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "expanded_splits_v5_pilot_polish"
OUT_DIR = ROOT / "expanded_splits_v6_free_text_copy"


def function(name: str, properties: dict, required: list[str], description: str = "Execute action.") -> dict:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        },
    }


def tool_system(tools: list[dict]) -> str:
    return (
        "You are a function calling AI model. Return only the final answer. "
        "Do not emit <think>, </think>, markdown, prose, or explanations. "
        "Return only tool calls inside <tool_call> tags. "
        "<tools>" + json.dumps(tools, separators=(",", ":")) + "</tools>"
    )


def tool_call(name: str, arguments: dict) -> str:
    return "<tool_call>\n" + json.dumps(
        {"name": name, "arguments": arguments},
        ensure_ascii=False,
        separators=(",", ":"),
    ) + "\n</tool_call>"


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


def free_text_rows() -> list[dict]:
    string = {"type": "string"}
    string_array = {"type": "array", "items": {"type": "string"}}
    integer = {"type": "integer"}
    boolean = {"type": "boolean"}
    return [
        {
            "id": "exp-free-text-copy-001-facilities",
            "category": "argument_correctness",
            "source": "strict_tool_call_expansion_v6_free_text_copy",
            "messages": [
                {
                    "role": "system",
                    "content": tool_system(
                        [
                            function(
                                "create_facilities_ticket",
                                {"site_id": string, "issue": string, "priority": string},
                                ["site_id", "issue", "priority"],
                            ),
                            function(
                                "notify_site_lead",
                                {"site_id": string, "lead": string, "message": string},
                                ["site_id", "lead", "message"],
                            ),
                        ]
                    ),
                },
                {
                    "role": "user",
                    "content": "Create a priority facilities ticket for site SITE-14 about lift outage, then notify Morgan that access is blocked.",
                },
                {
                    "role": "assistant",
                    "content": "\n".join(
                        [
                            tool_call(
                                "create_facilities_ticket",
                                {"site_id": "SITE-14", "issue": "lift outage", "priority": "priority"},
                            ),
                            tool_call(
                                "notify_site_lead",
                                {"site_id": "SITE-14", "lead": "Morgan", "message": "access is blocked"},
                            ),
                        ]
                    ),
                },
            ],
        },
        {
            "id": "exp-free-text-copy-002-content-review",
            "category": "argument_correctness",
            "source": "strict_tool_call_expansion_v6_free_text_copy",
            "messages": [
                {
                    "role": "system",
                    "content": tool_system(
                        [
                            function(
                                "open_content_review",
                                {"asset_id": string, "reviewers": string_array, "priority": string},
                                ["asset_id", "reviewers", "priority"],
                            ),
                            function(
                                "add_review_note",
                                {"asset_id": string, "note": string},
                                ["asset_id", "note"],
                            ),
                        ]
                    ),
                },
                {
                    "role": "user",
                    "content": "Open a priority content review for asset AS-440 with reviewers Mei and Omar, and add note draft is ready for review.",
                },
                {
                    "role": "assistant",
                    "content": "\n".join(
                        [
                            tool_call(
                                "open_content_review",
                                {"asset_id": "AS-440", "reviewers": ["Mei", "Omar"], "priority": "priority"},
                            ),
                            tool_call("add_review_note", {"asset_id": "AS-440", "note": "draft is ready for review"}),
                        ]
                    ),
                },
            ],
        },
        {
            "id": "exp-free-text-copy-003-field-service",
            "category": "argument_correctness",
            "source": "strict_tool_call_expansion_v6_free_text_copy",
            "messages": [
                {
                    "role": "system",
                    "content": tool_system(
                        [
                            function(
                                "assign_field_visit",
                                {"visit_id": string, "technician": string, "window": string},
                                ["visit_id", "technician", "window"],
                            ),
                            function(
                                "send_visit_update",
                                {"visit_id": string, "recipient": string, "message": string},
                                ["visit_id", "recipient", "message"],
                            ),
                        ]
                    ),
                },
                {
                    "role": "user",
                    "content": "Assign visit VIS-208 to Talia for the morning window, then tell the depot replacement part is on site.",
                },
                {
                    "role": "assistant",
                    "content": "\n".join(
                        [
                            tool_call(
                                "assign_field_visit",
                                {"visit_id": "VIS-208", "technician": "Talia", "window": "morning"},
                            ),
                            tool_call(
                                "send_visit_update",
                                {"visit_id": "VIS-208", "recipient": "depot", "message": "replacement part is on site"},
                            ),
                        ]
                    ),
                },
            ],
        },
        {
            "id": "exp-free-text-copy-004-compliance",
            "category": "argument_correctness",
            "source": "strict_tool_call_expansion_v6_free_text_copy",
            "messages": [
                {
                    "role": "system",
                    "content": tool_system(
                        [
                            function(
                                "create_compliance_case",
                                {"case_ref": string, "category": string, "owner": string},
                                ["case_ref", "category", "owner"],
                            ),
                            function(
                                "record_case_reason",
                                {"case_ref": string, "reason": string},
                                ["case_ref", "reason"],
                            ),
                        ]
                    ),
                },
                {
                    "role": "user",
                    "content": "Create compliance case CMP-17 in vendor_risk for owner Ada and record reason certificate expired yesterday.",
                },
                {
                    "role": "assistant",
                    "content": "\n".join(
                        [
                            tool_call(
                                "create_compliance_case",
                                {"case_ref": "CMP-17", "category": "vendor_risk", "owner": "Ada"},
                            ),
                            tool_call("record_case_reason", {"case_ref": "CMP-17", "reason": "certificate expired yesterday"}),
                        ]
                    ),
                },
            ],
        },
        {
            "id": "exp-free-text-copy-005-warehouse",
            "category": "argument_correctness",
            "source": "strict_tool_call_expansion_v6_free_text_copy",
            "messages": [
                {
                    "role": "system",
                    "content": tool_system(
                        [
                            function(
                                "start_cycle_count",
                                {"warehouse": string, "zones": string_array, "urgent": boolean},
                                ["warehouse", "zones", "urgent"],
                            ),
                            function(
                                "notify_inventory_team",
                                {"warehouse": string, "message": string},
                                ["warehouse", "message"],
                            ),
                        ]
                    ),
                },
                {
                    "role": "user",
                    "content": "Start an urgent cycle count at WH-PER-3 for zones A7 and C2, then notify inventory that variance is above threshold.",
                },
                {
                    "role": "assistant",
                    "content": "\n".join(
                        [
                            tool_call(
                                "start_cycle_count",
                                {"warehouse": "WH-PER-3", "zones": ["A7", "C2"], "urgent": True},
                            ),
                            tool_call(
                                "notify_inventory_team",
                                {"warehouse": "WH-PER-3", "message": "variance is above threshold"},
                            ),
                        ]
                    ),
                },
            ],
        },
        {
            "id": "exp-free-text-copy-006-release",
            "category": "argument_correctness",
            "source": "strict_tool_call_expansion_v6_free_text_copy",
            "messages": [
                {
                    "role": "system",
                    "content": tool_system(
                        [
                            function(
                                "create_release_note",
                                {"release_id": string, "summary": string, "audience": string},
                                ["release_id", "summary", "audience"],
                            ),
                            function(
                                "mark_release_review",
                                {"release_id": string, "state": string, "note": string},
                                ["release_id", "state", "note"],
                            ),
                        ]
                    ),
                },
                {
                    "role": "user",
                    "content": "Create release note REL-88 for customers with summary import wizard is faster, then mark review pending with note docs need final screenshots.",
                },
                {
                    "role": "assistant",
                    "content": "\n".join(
                        [
                            tool_call(
                                "create_release_note",
                                {"release_id": "REL-88", "summary": "import wizard is faster", "audience": "customers"},
                            ),
                            tool_call(
                                "mark_release_review",
                                {"release_id": "REL-88", "state": "pending", "note": "docs need final screenshots"},
                            ),
                        ]
                    ),
                },
            ],
        },
        {
            "id": "exp-free-text-copy-007-training",
            "category": "argument_correctness",
            "source": "strict_tool_call_expansion_v6_free_text_copy",
            "messages": [
                {
                    "role": "system",
                    "content": tool_system(
                        [
                            function(
                                "schedule_workshop",
                                {"workshop_id": string, "topic": string, "capacity": integer},
                                ["workshop_id", "topic", "capacity"],
                            ),
                            function(
                                "message_facilitator",
                                {"workshop_id": string, "facilitator": string, "message": string},
                                ["workshop_id", "facilitator", "message"],
                            ),
                        ]
                    ),
                },
                {
                    "role": "user",
                    "content": "Schedule workshop WS-71 on privacy basics for 24 people and message facilitator Noor that slides are in the shared drive.",
                },
                {
                    "role": "assistant",
                    "content": "\n".join(
                        [
                            tool_call("schedule_workshop", {"workshop_id": "WS-71", "topic": "privacy basics", "capacity": 24}),
                            tool_call(
                                "message_facilitator",
                                {"workshop_id": "WS-71", "facilitator": "Noor", "message": "slides are in the shared drive"},
                            ),
                        ]
                    ),
                },
            ],
        },
        {
            "id": "exp-free-text-copy-008-partner",
            "category": "argument_correctness",
            "source": "strict_tool_call_expansion_v6_free_text_copy",
            "messages": [
                {
                    "role": "system",
                    "content": tool_system(
                        [
                            function(
                                "update_partner_status",
                                {"partner_id": string, "status": string, "effective_date": string},
                                ["partner_id", "status", "effective_date"],
                            ),
                            function(
                                "add_partner_note",
                                {"partner_id": string, "note": string},
                                ["partner_id", "note"],
                            ),
                        ]
                    ),
                },
                {
                    "role": "user",
                    "content": "Update partner P-508 to provisional from 2026-07-01 and add note onboarding checklist is incomplete.",
                },
                {
                    "role": "assistant",
                    "content": "\n".join(
                        [
                            tool_call(
                                "update_partner_status",
                                {"partner_id": "P-508", "status": "provisional", "effective_date": "2026-07-01"},
                            ),
                            tool_call("add_partner_note", {"partner_id": "P-508", "note": "onboarding checklist is incomplete"}),
                        ]
                    ),
                },
            ],
        },
    ]


def main() -> int:
    train = load_jsonl(SOURCE_DIR / "train.jsonl")
    repair_rows = free_text_rows()
    expanded_repair_rows: list[dict] = []
    for row in repair_rows:
        expanded_repair_rows.append(row)
        expanded_repair_rows.append(no_think_variant(row))

    splits = {
        "train": train + expanded_repair_rows,
        "val": load_jsonl(SOURCE_DIR / "val.jsonl"),
        "valid": load_jsonl(SOURCE_DIR / "valid.jsonl"),
        "test": load_jsonl(SOURCE_DIR / "test.jsonl"),
    }
    ids = [str(row["id"]) for rows in splits.values() for row in rows]
    duplicates = sorted({row_id for row_id in ids if ids.count(row_id) > 1})
    expected_alias_duplicates = {str(row["id"]) for row in splits["val"]}
    unexpected = [row_id for row_id in duplicates if row_id not in expected_alias_duplicates]
    if unexpected:
        raise ValueError(f"unexpected duplicate ids: {unexpected}")
    for split, rows in splits.items():
        write_jsonl(OUT_DIR / f"{split}.jsonl", rows)
        print(f"{split}: {len(rows)} -> {OUT_DIR / f'{split}.jsonl'}")
    print(f"free_text_copy_rows: {len(repair_rows)}")
    print(f"total rows including valid alias: {sum(len(rows) for rows in splits.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
