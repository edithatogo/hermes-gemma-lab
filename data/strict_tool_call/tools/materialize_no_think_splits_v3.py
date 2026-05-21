#!/usr/bin/env python3
"""Materialize v3 splits with /no_think-prefixed training examples."""

from __future__ import annotations

import copy
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "expanded_splits_v2"
OUT_DIR = ROOT / "expanded_splits_v3_no_think"


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
    updated["category"] = row.get("category", "strict_tool_call")
    for message in updated["messages"]:
        if message.get("role") == "user":
            content = str(message.get("content", ""))
            if not content.lstrip().startswith("/no_think"):
                message["content"] = f"/no_think {content}"
            break
    return updated


def main() -> int:
    train = load_jsonl(SOURCE_DIR / "train.jsonl")
    augmented_train = train + [no_think_variant(row) for row in train]
    splits = {
        "train": augmented_train,
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
