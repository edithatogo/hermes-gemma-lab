#!/usr/bin/env python3
"""Materialize deterministic expanded strict tool-call train/val/test splits."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW_FILES = [
    ROOT / "raw" / "seed.jsonl",
    ROOT / "raw" / "expansion_seed_v1.jsonl",
]
OUT_DIR = ROOT / "expanded_splits_v1"


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


def main() -> int:
    rows: list[dict] = []
    for path in RAW_FILES:
        rows.extend(load_jsonl(path))
    rows = sorted(rows, key=lambda item: str(item["id"]))

    ids = [str(row["id"]) for row in rows]
    duplicates = sorted({row_id for row_id in ids if ids.count(row_id) > 1})
    if duplicates:
        raise ValueError(f"duplicate ids: {duplicates}")

    train_end = int(len(rows) * 0.8)
    val_end = train_end + max(1, int(len(rows) * 0.1))
    splits = {
        "train": rows[:train_end],
        "val": rows[train_end:val_end],
        "valid": rows[train_end:val_end],
        "test": rows[val_end:],
    }
    for split, split_rows in splits.items():
        write_jsonl(OUT_DIR / f"{split}.jsonl", split_rows)
        print(f"{split}: {len(split_rows)} -> {OUT_DIR / f'{split}.jsonl'}")
    print(f"total: {len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
