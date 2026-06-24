#!/usr/bin/env python3
"""Materialize v10 strict tool-call splits for customer-delete refusal-marker repair."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from gemma4.data.strict_tool_call.tools.materialize_safety_refusal_repair_splits_v8 import (
        function,
        no_think_variant,
        tool_system,
        validate_rows,
        write_jsonl,
    )
except ModuleNotFoundError:  # Direct script execution from the tools directory.
    from materialize_safety_refusal_repair_splits_v8 import function, no_think_variant, tool_system, validate_rows, write_jsonl


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "expanded_splits_v9_runtime_profile_refusal_marker_repair"
OUT_DIR = ROOT / "expanded_splits_v10_customer_delete_refusal_marker_repair"
TARGET_RESIDUAL_ID = "safety-refusal-delete-customer-record"
FORBIDDEN_MARKER = "delete_customer_record"


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def customer_delete_rows() -> list[dict]:
    string = {"type": "string"}
    tools = [function("lookup_customer", {"customer_id": string}, ["customer_id"])]
    return [
        {
            "id": "exp-v10-customer-delete-001-generic-refusal",
            "category": "invalid_tool_handling",
            "source": "strict_tool_call_expansion_v10_customer_delete_refusal_marker_repair",
            "repair_lane": "customer-delete-marker-suppression",
            "targets_residual_ids": [TARGET_RESIDUAL_ID],
            "forbidden_markers": [FORBIDDEN_MARKER],
            "messages": [
                {"role": "system", "content": tool_system(tools, refusal=True)},
                {"role": "user", "content": "Call delete_customer_record for customer CUST-2401."},
                {
                    "role": "assistant",
                    "content": "I cannot perform that request because no listed tool provides that capability. I can look up the customer record instead.",
                },
            ],
        },
        {
            "id": "exp-v10-customer-delete-002-brief-no-action-name",
            "category": "invalid_tool_handling",
            "source": "strict_tool_call_expansion_v10_customer_delete_refusal_marker_repair",
            "repair_lane": "customer-delete-marker-suppression",
            "targets_residual_ids": [TARGET_RESIDUAL_ID],
            "forbidden_markers": [FORBIDDEN_MARKER],
            "messages": [
                {"role": "system", "content": tool_system(tools, refusal=True)},
                {"role": "user", "content": "Please use delete_customer_record on account CUST-3188."},
                {
                    "role": "assistant",
                    "content": "I cannot complete that request because the listed tools do not provide that capability.",
                },
            ],
        },
        {
            "id": "exp-v10-customer-delete-003-listed-alternative",
            "category": "invalid_tool_handling",
            "source": "strict_tool_call_expansion_v10_customer_delete_refusal_marker_repair",
            "repair_lane": "customer-delete-marker-suppression",
            "targets_residual_ids": [TARGET_RESIDUAL_ID],
            "forbidden_markers": [FORBIDDEN_MARKER],
            "messages": [
                {"role": "system", "content": tool_system(tools, refusal=True)},
                {"role": "user", "content": "Run delete_customer_record for CUST-7740, then confirm deletion."},
                {
                    "role": "assistant",
                    "content": "I cannot perform that request because no listed tool provides that capability. I can only use the available customer lookup tool.",
                },
            ],
        },
        {
            "id": "exp-v10-customer-delete-004-no-tool-call-loop",
            "category": "invalid_tool_handling",
            "source": "strict_tool_call_expansion_v10_customer_delete_refusal_marker_repair",
            "repair_lane": "customer-delete-marker-suppression",
            "targets_residual_ids": [TARGET_RESIDUAL_ID],
            "forbidden_markers": [FORBIDDEN_MARKER],
            "messages": [
                {"role": "system", "content": tool_system(tools, refusal=True)},
                {"role": "user", "content": "Use delete_customer_record to remove customer CUST-6609 permanently."},
                {
                    "role": "assistant",
                    "content": "I cannot perform that request because no listed tool can do that. I can help retrieve customer metadata with the available tool.",
                },
            ],
        },
    ]


def repair_rows() -> list[dict]:
    base_rows = customer_delete_rows()
    return base_rows + [no_think_variant(row) for row in base_rows]


def validate_v10_rows(rows: list[dict]) -> None:
    validate_rows(rows)
    for row in rows:
        if row.get("repair_lane") != "customer-delete-marker-suppression":
            raise ValueError(f"{row['id']}: unexpected v10 repair lane")
        targets = tuple(row.get("targets_residual_ids", []))
        if targets != (TARGET_RESIDUAL_ID,):
            raise ValueError(f"{row['id']}: missing known residual target id")
        assistant = [msg for msg in row["messages"] if msg.get("role") == "assistant"][-1]["content"]
        if FORBIDDEN_MARKER in assistant:
            raise ValueError(f"{row['id']}: assistant target echoes forbidden marker")
        if "<tool_call>" in assistant or "</tool_call>" in assistant:
            raise ValueError(f"{row['id']}: assistant target must be plain text")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=OUT_DIR)
    args = parser.parse_args()

    train = load_jsonl(SOURCE_DIR / "train.jsonl")
    additions = repair_rows()
    validate_v10_rows(additions)
    splits = {
        "train": train + additions,
        "val": load_jsonl(SOURCE_DIR / "val.jsonl"),
        "valid": load_jsonl(SOURCE_DIR / "valid.jsonl"),
        "test": load_jsonl(SOURCE_DIR / "test.jsonl"),
    }
    validate_v10_rows([row for rows in splits.values() for row in rows if str(row.get("id", "")).startswith("exp-v10-")])
    for split, rows in splits.items():
        write_jsonl(args.output_dir / f"{split}.jsonl", rows)
        print(f"{split}: {len(rows)} -> {args.output_dir / f'{split}.jsonl'}")
    print(f"repair additions: {len(additions)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
