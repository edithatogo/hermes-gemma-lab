#!/usr/bin/env python3
"""Materialize v4 strict tool-call splits with targeted generalization rows."""

from __future__ import annotations

import copy
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "expanded_splits_v3_no_think"
OUT_DIR = ROOT / "expanded_splits_v4_targeted"


def tool_system(tools: list[dict], *, invalid_ok: bool = False) -> str:
    prefix = (
        "You are a function calling AI model. Return only the final answer. "
        "Do not emit <think>, </think>, markdown, prose, or explanations. "
    )
    if invalid_ok:
        prefix += "Return only tool calls inside <tool_call> tags when a valid tool exists. "
    else:
        prefix += "Return only tool calls inside <tool_call> tags. "
    return prefix + "<tools>" + json.dumps(tools, separators=(",", ":")) + "</tools>"


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


def message_exact_rows() -> list[dict]:
    string = {"type": "string"}
    array_string = {"type": "array", "items": {"type": "string"}}
    return [
        {
            "id": "exp-target-message-exact-001-radiology",
            "category": "argument_correctness",
            "source": "strict_tool_call_expansion_v4_targeted",
            "messages": [
                {
                    "role": "system",
                    "content": tool_system(
                        [
                            function(
                                "create_radiology_order",
                                {
                                    "patient_id": string,
                                    "studies": array_string,
                                    "priority": string,
                                    "site": string,
                                },
                                ["patient_id", "studies", "priority", "site"],
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
                    "content": "Create an urgent radiology order for patient PT-9021 for chest xray and CT at East Clinic, then notify radiology that scan is ready for review.",
                },
                {
                    "role": "assistant",
                    "content": "\n".join(
                        [
                            tool_call(
                                "create_radiology_order",
                                {
                                    "patient_id": "PT-9021",
                                    "studies": ["chest xray", "CT"],
                                    "priority": "urgent",
                                    "site": "East Clinic",
                                },
                            ),
                            tool_call(
                                "notify_care_team",
                                {
                                    "patient_id": "PT-9021",
                                    "team": "radiology",
                                    "message": "scan is ready for review",
                                },
                            ),
                        ]
                    ),
                },
            ],
        },
        {
            "id": "exp-target-message-exact-002-pharmacy",
            "category": "argument_correctness",
            "source": "strict_tool_call_expansion_v4_targeted",
            "messages": [
                {
                    "role": "system",
                    "content": tool_system(
                        [
                            function(
                                "approve_refill_request",
                                {"patient_id": string, "medications": array_string, "days": {"type": "integer"}},
                                ["patient_id", "medications", "days"],
                            ),
                            function(
                                "notify_clinic_team",
                                {"patient_id": string, "team": string, "message": string},
                                ["patient_id", "team", "message"],
                            ),
                        ]
                    ),
                },
                {
                    "role": "user",
                    "content": "Approve a 30 day refill for patient PT-3188 for salbutamol and cetirizine, then notify pharmacy that refill is ready for pickup.",
                },
                {
                    "role": "assistant",
                    "content": "\n".join(
                        [
                            tool_call(
                                "approve_refill_request",
                                {
                                    "patient_id": "PT-3188",
                                    "medications": ["salbutamol", "cetirizine"],
                                    "days": 30,
                                },
                            ),
                            tool_call(
                                "notify_clinic_team",
                                {
                                    "patient_id": "PT-3188",
                                    "team": "pharmacy",
                                    "message": "refill is ready for pickup",
                                },
                            ),
                        ]
                    ),
                },
            ],
        },
        {
            "id": "exp-target-message-exact-003-transfer",
            "category": "argument_correctness",
            "source": "strict_tool_call_expansion_v4_targeted",
            "messages": [
                {
                    "role": "system",
                    "content": tool_system(
                        [
                            function(
                                "create_transfer_request",
                                {"case_id": string, "from_unit": string, "to_unit": string, "priority": string},
                                ["case_id", "from_unit", "to_unit", "priority"],
                            ),
                            function(
                                "notify_operations",
                                {"case_id": string, "team": string, "message": string},
                                ["case_id", "team", "message"],
                            ),
                        ]
                    ),
                },
                {
                    "role": "user",
                    "content": "Create a priority transfer request for case CASE-772 from Ward 4 to Stepdown, then notify bed-management that transfer is ready for review.",
                },
                {
                    "role": "assistant",
                    "content": "\n".join(
                        [
                            tool_call(
                                "create_transfer_request",
                                {
                                    "case_id": "CASE-772",
                                    "from_unit": "Ward 4",
                                    "to_unit": "Stepdown",
                                    "priority": "priority",
                                },
                            ),
                            tool_call(
                                "notify_operations",
                                {
                                    "case_id": "CASE-772",
                                    "team": "bed-management",
                                    "message": "transfer is ready for review",
                                },
                            ),
                        ]
                    ),
                },
            ],
        },
    ]


def object_array_rows() -> list[dict]:
    string = {"type": "string"}
    integer = {"type": "integer"}
    return [
        {
            "id": "exp-target-object-array-001-requisition",
            "category": "json_validity",
            "source": "strict_tool_call_expansion_v4_targeted",
            "messages": [
                {
                    "role": "system",
                    "content": tool_system(
                        [
                            function(
                                "create_requisition",
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
                                    "deliver_to": string,
                                    "needed_by": string,
                                },
                                ["vendor_id", "items", "deliver_to", "needed_by"],
                            )
                        ]
                    ),
                },
                {
                    "role": "user",
                    "content": "Create a requisition for vendor VEND-42 with 30 units of BOLT-7 and 8 units of NUT-3, deliver to Plant 9, needed by 2026-08-11.",
                },
                {
                    "role": "assistant",
                    "content": tool_call(
                        "create_requisition",
                        {
                            "vendor_id": "VEND-42",
                            "items": [
                                {"sku": "BOLT-7", "quantity": 30},
                                {"sku": "NUT-3", "quantity": 8},
                            ],
                            "deliver_to": "Plant 9",
                            "needed_by": "2026-08-11",
                        },
                    ),
                },
            ],
        },
        {
            "id": "exp-target-object-array-002-shipment",
            "category": "json_validity",
            "source": "strict_tool_call_expansion_v4_targeted",
            "messages": [
                {
                    "role": "system",
                    "content": tool_system(
                        [
                            function(
                                "create_shipment_plan",
                                {
                                    "route_id": string,
                                    "packages": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {"package_id": string, "weight_kg": {"type": "number"}},
                                            "required": ["package_id", "weight_kg"],
                                        },
                                    },
                                    "origin": string,
                                    "dispatch_date": string,
                                },
                                ["route_id", "packages", "origin", "dispatch_date"],
                            )
                        ]
                    ),
                },
                {
                    "role": "user",
                    "content": "Create shipment plan ROUTE-19 from PER-DC with packages PKG-1 weighing 14.5 kg and PKG-2 weighing 7.25 kg for dispatch on 2026-08-17.",
                },
                {
                    "role": "assistant",
                    "content": tool_call(
                        "create_shipment_plan",
                        {
                            "route_id": "ROUTE-19",
                            "packages": [
                                {"package_id": "PKG-1", "weight_kg": 14.5},
                                {"package_id": "PKG-2", "weight_kg": 7.25},
                            ],
                            "origin": "PER-DC",
                            "dispatch_date": "2026-08-17",
                        },
                    ),
                },
            ],
        },
        {
            "id": "exp-target-object-array-003-repair",
            "category": "multi_turn_repair",
            "source": "strict_tool_call_expansion_v4_targeted",
            "messages": [
                {
                    "role": "system",
                    "content": tool_system(
                        [
                            function(
                                "create_parts_order",
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
                    "content": "Create a parts order for supplier SUP-18 with 6 units of VALVE-2 and 3 units of SEAL-5, ship to Workshop 2, needed by 2026-08-22.",
                },
                {
                    "role": "assistant",
                    "content": tool_call(
                        "create_parts_order",
                        {
                            "supplier_id": "SUP-18",
                            "items": [{"sku": "VALVE-2", "quantity": 6}],
                        },
                    ),
                },
                {
                    "role": "user",
                    "content": "That left out SEAL-5 plus ship_to and needed_by. Re-issue only the corrected parts order tool call.",
                },
                {
                    "role": "assistant",
                    "content": tool_call(
                        "create_parts_order",
                        {
                            "supplier_id": "SUP-18",
                            "items": [
                                {"sku": "VALVE-2", "quantity": 6},
                                {"sku": "SEAL-5", "quantity": 3},
                            ],
                            "ship_to": "Workshop 2",
                            "needed_by": "2026-08-22",
                        },
                    ),
                },
            ],
        },
    ]


def targeted_rows() -> list[dict]:
    rows = message_exact_rows() + object_array_rows()
    expanded: list[dict] = []
    for row in rows:
        expanded.append(row)
        expanded.append(no_think_variant(row))
    return expanded


def main() -> int:
    train = load_jsonl(SOURCE_DIR / "train.jsonl")
    splits = {
        "train": train + targeted_rows(),
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
    print(f"total rows including valid alias: {sum(len(rows) for rows in splits.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
