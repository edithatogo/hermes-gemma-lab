#!/usr/bin/env python3
"""Download Hermes datasets directly from Hugging Face raw files."""
import argparse
import json
import os
from pathlib import Path

import requests

REPO_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = REPO_DIR / "data/raw"

def download_raw_file(url, output_path, label="file"):
    """Download a raw file from HuggingFace."""
    print(f"  Downloading {label}...")
    r = requests.get(url, stream=True, timeout=600)
    r.raise_for_status()
    with open(output_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    size_mb = output_path.stat().st_size / 1e6
    print(f"    {size_mb:.1f} MB downloaded")
    return output_path

def convert_conversations(line, source_label=""):
    """Convert a JSON line from a Hermes dataset to our messages format.

    Handles multiple input formats:
      - conversations[] with {from, value} (Hermes-3 / ShareGPT)
      - messages[] with {role, content} (standard chat format)
      - {conversation, system, ...} (instruction format)
    """
    if isinstance(line, str):
        data = json.loads(line)
    else:
        data = line

    # Format 1: conversations[] with {from, value} (Hermes native)
    if "conversations" in data:
        conv = data["conversations"]
        messages = []
        for turn in conv:
            role = turn.get("from", "")
            value = turn.get("value", "")
            if role == "human":
                messages.append({"role": "user", "content": value})
            elif role in ("gpt", "assistant"):
                messages.append({"role": "assistant", "content": value})
            elif role == "system":
                messages.append({"role": "system", "content": value})
        if messages:
            return {"messages": messages}

    # Format 2: messages[] with {role, content} (standard)
    if "messages" in data:
        msgs = data["messages"]
        if isinstance(msgs, list) and len(msgs) > 0 and isinstance(msgs[0], dict):
            if "role" in msgs[0] and "content" in msgs[0]:
                return {"messages": msgs}

    # Format 3: conversation[] with {role, content}
    if "conversation" in data:
        return {"messages": data["conversation"]}

    return None

def download_hermes3_dataset(output_path, max_lines=500):
    """Download Hermes-3-Dataset JSONL from HuggingFace."""
    url = "https://huggingface.co/datasets/NousResearch/Hermes-3-Dataset/resolve/main/hermes-3-dataset.jsonl"
    print(f"\n=== Downloading Hermes-3-Dataset ===")

    # Stream and convert in one pass
    r = requests.get(url, stream=True, timeout=600)
    r.raise_for_status()

    written = 0
    with open(output_path, "w") as f:
        for i, line in enumerate(r.iter_lines()):
            if not line:
                continue
            if max_lines and i >= max_lines:
                break
            if i % 1000 == 0:
                print(f"  Processing line {i}...")

            try:
                converted = convert_conversations(line.decode("utf-8"))
                if converted:
                    converted["id"] = f"hermes3-{written}"
                    f.write(json.dumps(converted) + "\n")
                    written += 1
            except json.JSONDecodeError:
                continue

    print(f"  Written {written} conversations")
    return written

def download_raw_json(url, output_path, max_items=200):
    """Download a raw JSON file and extract conversations."""
    print(f"\n  Downloading raw JSON...")
    r = requests.get(url, timeout=600)
    r.raise_for_status()
    data = r.json()

    if isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        # Try common keys for the data array
        items = data.get("data", data.get("conversations", data.get("examples", [])))
        if not isinstance(items, list):
            items = [data]
    else:
        items = [data]

    written = 0
    with open(output_path, "w") as f:
        for i, item in enumerate(items):
            if max_items and i >= max_items:
                break
            converted = convert_conversations(json.dumps(item))
            if converted:
                converted["id"] = f"hermes-fc-{written}"
                f.write(json.dumps(converted) + "\n")
                written += 1

    print(f"  Written {written} conversations")
    return written

PROFILES = {
    "smoke": {"hermes3": 500, "fc_single": 100, "fc_multi": 100, "json_agentic": 50, "json_single": 50},
    "pilot": {"hermes3": 10000, "fc_single": 2000, "fc_multi": 2000, "json_agentic": 1000, "json_single": 1000},
    "full": {"hermes3": 100000, "fc_single": 10000, "fc_multi": 10000, "json_agentic": 5000, "json_single": 5000},
}

def main():
    parser = argparse.ArgumentParser(description="Download Hermes training data.")
    parser.add_argument("--profile", choices=PROFILES, default="smoke")
    parser.add_argument("--hermes3-lines", type=int, help="Override Hermes-3 line cap. Use 0 for no cap.")
    args = parser.parse_args()
    profile = PROFILES[args.profile].copy()
    if args.hermes3_lines is not None:
        profile["hermes3"] = args.hermes3_lines or None

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    total = 0

    # 1. Hermes-3-Dataset (raw JSONL)
    total += download_hermes3_dataset(
        RAW_DIR / "hermes3_dataset.jsonl",
        max_lines=profile["hermes3"]
    )

    # 2. hermes-function-calling-v1 (multiple JSON files)
    fc_dir = RAW_DIR / "_hermes_fc"
    fc_dir.mkdir(parents=True, exist_ok=True)

    for json_file, max_n in [
        ("func-calling-singleturn.json", profile["fc_single"]),
        ("func-calling.json", profile["fc_multi"]),
        ("json-mode-agentic.json", profile["json_agentic"]),
        ("json-mode-singleturn.json", profile["json_single"]),
    ]:
        url = f"https://huggingface.co/datasets/NousResearch/hermes-function-calling-v1/resolve/main/{json_file}"
        total += download_raw_json(url, fc_dir / json_file, max_items=max_n)

    print(f"\n=== Total: {total} conversations across all datasets ===")

    # Run the build_dataset pipeline
    print("\n=== Running dataset pipeline ===")
    ret = os.system(f"cd {REPO_DIR} && python3 scripts/build_dataset.py --input-dir {RAW_DIR} --output-dir {REPO_DIR/'data/splits'} --dedup")

    if ret == 0:
        print("\n=== Split sizes ===")
        for split in ["train", "val", "test"]:
            path = REPO_DIR / "data/splits" / f"{split}.jsonl"
            if path.exists():
                with open(path) as f:
                    lines = sum(1 for _ in f)
                print(f"  {split}: {lines} conversations")
    else:
        print(f"Dataset pipeline failed with exit code {ret}")

if __name__ == "__main__":
    main()
