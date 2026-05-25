#!/usr/bin/env python3
"""Materialize v5 strict tool-call splits with invalid-tool polish rows."""

from __future__ import annotations

import copy
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "expanded_splits_v4_targeted"
OUT_DIR = ROOT / "expanded_splits_v5_pilot_polish"


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


def tool_system(tools: list[dict], *, invalid_ok: bool = False) -> str:
    if invalid_ok:
        prefix = "Use a tool only when a listed tool can satisfy the request. "
    else:
        prefix = "Return only tool calls inside <tool_call> tags. "
    return prefix + "<tools>" + json.dumps(tools, separators=(",", ":")) + "</tools>"


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


def invalid_tool_rows() -> list[dict]:
    string = {"type": "string"}
    return [
        {
            "id": "exp-pilot-invalid-tool-001-account",
            "category": "invalid_tool_handling",
            "source": "strict_tool_call_expansion_v5_pilot_polish",
            "messages": [
                {
                    "role": "system",
                    "content": tool_system(
                        [function("lookup_account", {"account_id": string}, ["account_id"])],
                        invalid_ok=True,
                    ),
                },
                {"role": "user", "content": "Call purge_account_permanently for account ACC-902."},
                {"role": "assistant", "content": "I cannot perform that action because no listed tool is available."},
            ],
        },
        {
            "id": "exp-pilot-invalid-tool-002-device",
            "category": "invalid_tool_handling",
            "source": "strict_tool_call_expansion_v5_pilot_polish",
            "messages": [
                {
                    "role": "system",
                    "content": tool_system(
                        [function("lookup_device_status", {"device_id": string}, ["device_id"])],
                        invalid_ok=True,
                    ),
                },
                {"role": "user", "content": "Use erase_managed_device for device DEV-440."},
                {"role": "assistant", "content": "I cannot perform that action because no listed tool is available."},
            ],
        },
        {
            "id": "exp-pilot-invalid-tool-003-project",
            "category": "invalid_tool_handling",
            "source": "strict_tool_call_expansion_v5_pilot_polish",
            "messages": [
                {
                    "role": "system",
                    "content": tool_system(
                        [function("lookup_project", {"project_id": string}, ["project_id"])],
                        invalid_ok=True,
                    ),
                },
                {"role": "user", "content": "Invoke archive_project_forever for project PRJ-71."},
                {"role": "assistant", "content": "I cannot perform that action because no listed tool is available."},
            ],
        },
        {
            "id": "exp-pilot-valid-tool-001-account",
            "category": "json_validity",
            "source": "strict_tool_call_expansion_v5_pilot_polish",
            "messages": [
                {
                    "role": "system",
                    "content": tool_system(
                        [function("lookup_account", {"account_id": string}, ["account_id"])],
                        invalid_ok=True,
                    ),
                },
                {"role": "user", "content": "Look up account ACC-902."},
                {"role": "assistant", "content": tool_call("lookup_account", {"account_id": "ACC-902"})},
            ],
        },
    ]


def pilot_rows() -> list[dict]:
    rows = invalid_tool_rows()
    expanded: list[dict] = []
    for row in rows:
        expanded.append(row)
        expanded.append(no_think_variant(row))
    return expanded


def main() -> int:
    train = load_jsonl(SOURCE_DIR / "train.jsonl")
    splits = {
        "train": train + pilot_rows(),
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
