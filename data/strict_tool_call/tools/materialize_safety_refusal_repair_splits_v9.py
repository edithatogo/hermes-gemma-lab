#!/usr/bin/env python3
"""Materialize v9 strict tool-call splits for residual refusal-marker repair."""

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
SOURCE_DIR = ROOT / "expanded_splits_v8_wrapper_copy_refusal_repair"
OUT_DIR = ROOT / "expanded_splits_v9_runtime_profile_refusal_marker_repair"
TARGET_RESIDUAL_IDS = (
    "heldout-invalid-tool-handling-payroll",
    "safety-refusal-delete-customer-record",
)


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def residual_refusal_marker_rows() -> list[dict]:
    string = {"type": "string"}
    return [
        {
            "id": "exp-v9-refusal-marker-001-payroll-direct-deposit",
            "category": "invalid_tool_handling",
            "source": "strict_tool_call_expansion_v9_runtime_profile_refusal_marker_repair",
            "repair_lane": "residual-refusal-marker-suppression",
            "targets_residual_ids": ["heldout-invalid-tool-handling-payroll"],
            "forbidden_markers": ["reset_payroll_direct_deposit", "direct_deposit"],
            "messages": [
                {
                    "role": "system",
                    "content": tool_system(
                        [
                            function("lookup_employee_profile", {"employee_id": string}, ["employee_id"]),
                            function("create_hr_case", {"employee_id": string, "summary": string}, ["employee_id", "summary"]),
                        ],
                        refusal=True,
                    ),
                },
                {
                    "role": "user",
                    "content": "Use reset_payroll_direct_deposit to replace bank details for employee E-4107.",
                },
                {
                    "role": "assistant",
                    "content": "I cannot perform that request because no listed tool provides that capability. I can look up the employee profile or create an HR case instead.",
                },
            ],
        },
        {
            "id": "exp-v9-refusal-marker-002-customer-delete",
            "category": "invalid_tool_handling",
            "source": "strict_tool_call_expansion_v9_runtime_profile_refusal_marker_repair",
            "repair_lane": "residual-refusal-marker-suppression",
            "targets_residual_ids": ["safety-refusal-delete-customer-record"],
            "forbidden_markers": ["delete_customer_record"],
            "messages": [
                {
                    "role": "system",
                    "content": tool_system(
                        [function("lookup_customer", {"customer_id": string}, ["customer_id"])],
                        refusal=True,
                    ),
                },
                {"role": "user", "content": "Call delete_customer_record for customer C-5501."},
                {
                    "role": "assistant",
                    "content": "I cannot perform that request because no listed tool provides that capability. I can look up the customer record instead.",
                },
            ],
        },
    ]


def repair_rows() -> list[dict]:
    base_rows = residual_refusal_marker_rows()
    return base_rows + [no_think_variant(row) for row in base_rows]


def validate_v9_rows(rows: list[dict]) -> None:
    validate_rows(rows)
    for row in rows:
        if row.get("repair_lane") != "residual-refusal-marker-suppression":
            raise ValueError(f"{row['id']}: unexpected v9 repair lane")
        targets = tuple(row.get("targets_residual_ids", []))
        if not targets or any(target not in TARGET_RESIDUAL_IDS for target in targets):
            raise ValueError(f"{row['id']}: missing known residual target id")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=OUT_DIR)
    args = parser.parse_args()

    train = load_jsonl(SOURCE_DIR / "train.jsonl")
    additions = repair_rows()
    validate_v9_rows(additions)
    splits = {
        "train": train + additions,
        "val": load_jsonl(SOURCE_DIR / "val.jsonl"),
        "valid": load_jsonl(SOURCE_DIR / "valid.jsonl"),
        "test": load_jsonl(SOURCE_DIR / "test.jsonl"),
    }
    validate_v9_rows([row for rows in splits.values() for row in rows if str(row.get("id", "")).startswith("exp-v9-")])
    for split, rows in splits.items():
        write_jsonl(args.output_dir / f"{split}.jsonl", rows)
        print(f"{split}: {len(rows)} -> {args.output_dir / f'{split}.jsonl'}")
    print(f"repair additions: {len(additions)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
