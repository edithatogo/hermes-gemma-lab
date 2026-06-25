#!/usr/bin/env python3
"""Materialize v11 strict tool-call splits with BFCL selected-slice repair rows."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BASE_DIR = ROOT / "expanded_splits_v10_customer_delete_refusal_marker_repair"
OUT_DIR = ROOT / "expanded_splits_v11_bfcl_selected_repair"
SCORE_ROOT = Path(
    "/Volumes/PortableSSD/hermes-evals/standard-benchmarks/bfcl/"
    "qwen3-v4-peft-official-bfcl-text-prefix-selected-20260624/"
    "scores/Qwen_Qwen3-4B-Instruct-2507-FC/non_live"
)
REPAIR_PREFIX = "bfcl-v11-"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")


def load_json_documents(path: Path) -> list[Any]:
    text = path.read_text(encoding="utf-8")
    decoder = json.JSONDecoder()
    index = 0
    docs: list[Any] = []
    while index < len(text):
        while index < len(text) and text[index].isspace():
            index += 1
        if index >= len(text):
            break
        obj, index = decoder.raw_decode(text, index)
        docs.append(obj)
    return docs


def normalize_schema(schema: dict[str, Any]) -> dict[str, Any]:
    updated = dict(schema)
    if updated.get("type") == "dict":
        updated["type"] = "object"
    return updated


def tool_system(functions: list[dict[str, Any]], category: str) -> str:
    tools = []
    for fn in functions:
        parameters = normalize_schema(dict(fn.get("parameters", {})))
        tools.append(
            {
                "type": "function",
                "function": {
                    "name": fn["name"],
                    "description": fn.get("description", "Execute the requested function."),
                    "parameters": parameters,
                },
            }
        )
    extra = " For parallel requests, emit one <tool_call> block for each requested action in request order."
    if category != "parallel":
        extra = ""
    return (
        "You are a function calling AI model. Return only the final answer. "
        "Do not emit <think>, </think>, markdown, prose, or explanations. "
        "Return only tool calls inside <tool_call> tags."
        f"{extra} <tools>"
        + json.dumps(tools, ensure_ascii=False, separators=(",", ":"))
        + "</tools>"
    )


def choose_argument(value: Any) -> Any:
    if isinstance(value, list) and len(value) == 1:
        return value[0]
    return value


def answer_to_call(answer: dict[str, Any]) -> dict[str, Any]:
    if len(answer) != 1:
        raise ValueError(f"expected one function per BFCL answer object, got {answer!r}")
    name, arguments = next(iter(answer.items()))
    if not isinstance(arguments, dict):
        raise ValueError(f"{name}: expected argument object")
    return {
        "name": name,
        "arguments": {str(key): choose_argument(value) for key, value in arguments.items()},
    }


def render_tool_calls(possible_answer: list[dict[str, Any]]) -> str:
    chunks = []
    for answer in possible_answer:
        payload = answer_to_call(answer)
        chunks.append(
            "<tool_call>\n"
            + json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
            + "\n</tool_call>"
        )
    return "\n".join(chunks)


def question_text(prompt: dict[str, Any]) -> str:
    question = prompt.get("question")
    if not isinstance(question, list) or not question:
        raise ValueError(f"{prompt.get('id')}: missing question")
    first_turn = question[0]
    if not isinstance(first_turn, list) or not first_turn:
        raise ValueError(f"{prompt.get('id')}: malformed question")
    content = first_turn[0].get("content")
    if not isinstance(content, str):
        raise ValueError(f"{prompt.get('id')}: missing user content")
    return content


def repair_row(score_row: dict[str, Any]) -> dict[str, Any]:
    prompt = score_row["prompt"]
    category = str(score_row["test_category"])
    possible_answer = score_row["possible_answer"]
    if not isinstance(possible_answer, list) or not possible_answer:
        raise ValueError(f"{score_row['id']}: missing possible_answer")
    return {
        "id": f"{REPAIR_PREFIX}{score_row['id']}",
        "category": f"bfcl_selected_{category}",
        "source": "bfcl_selected_slice_20260624",
        "repair_lane": "bfcl-selected-visible-tool-call",
        "targets_residual_ids": [str(score_row["id"])],
        "messages": [
            {"role": "system", "content": tool_system(prompt["function"], category)},
            {"role": "user", "content": question_text(prompt)},
            {"role": "assistant", "content": render_tool_calls(possible_answer)},
        ],
    }


def build_repair_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for category in ("simple_python", "multiple", "parallel"):
        docs = load_json_documents(SCORE_ROOT / f"BFCL_v4_{category}_score.json")
        detail_rows = [doc for doc in docs if isinstance(doc, dict) and "id" in doc]
        for row in detail_rows:
            if row.get("valid") is True:
                continue
            rows.append(repair_row(row))
    return sorted(rows, key=lambda item: str(item["id"]))


def materialize(output_dir: Path = OUT_DIR) -> dict[str, int]:
    base_train = load_jsonl(BASE_DIR / "train.jsonl")
    repair_rows = build_repair_rows()
    train = base_train + repair_rows
    write_jsonl(output_dir / "train.jsonl", train)
    for split in ("val", "valid", "test"):
        write_jsonl(output_dir / f"{split}.jsonl", load_jsonl(BASE_DIR / f"{split}.jsonl"))
    return {
        "base_train_rows": len(base_train),
        "repair_rows": len(repair_rows),
        "train_rows": len(train),
        "val_rows": len(load_jsonl(output_dir / "val.jsonl")),
        "test_rows": len(load_jsonl(output_dir / "test.jsonl")),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=OUT_DIR)
    args = parser.parse_args()
    summary = materialize(args.output_dir)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
