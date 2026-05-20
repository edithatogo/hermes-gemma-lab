#!/usr/bin/env python3
"""
Build Hermes-style dataset from raw conversations.
"""
import argparse
import hashlib
import json
import os
import random
import sys
from pathlib import Path
from typing import Dict, List, Tuple

def hash_conversation(conversation: List[Dict]) -> str:
    """Compute a hash of the conversation for deduplication."""
    # We'll convert the conversation to a stable string representation
    # and then hash it.
    # We sort by the content of each message? No, we keep order.
    # We'll just join the role and content in a fixed format.
    text = ""
    for msg in conversation:
        # Ensure we have role and content
        role = msg.get("role", "")
        content = msg.get("content", "")
        text += f"{role}:{content}\n"
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def validate_conversation(conv: Dict) -> Tuple[bool, List[Dict]]:
    """Validate and normalize a conversation object.
    Returns (is_valid, normalized_conversation)"""
    # Accept 'messages' or 'conversation' key, or a bare list.
    if isinstance(conv, dict):
        messages = conv.get("messages") or conv.get("conversation")
        if messages is None:
            return False, []
        conv_id = conv.get("id")
    elif isinstance(conv, list):
        messages = conv
        conv_id = None
    else:
        return False, []

    # Validate each message
    normalized = []
    for msg in messages:
        if not isinstance(msg, dict):
            return False, []
        role = msg.get("role")
        content = msg.get("content")
        if role not in ("system", "user", "assistant"):
            return False, []
        if not isinstance(content, str):
            return False, []
        normalized.append({"role": role, "content": content})

    # We require at least one user and one assistant turn? Actually, we can have system only?
    # For training, we want at least one user and one assistant.
    # But let's just require at least two turns and that the last is from assistant? Not necessarily.
    # We'll set a minimum number of turns.
    if len(normalized) < 2:
        return False, []

    # Return the normalized conversation and the original id if we had one.
    return True, normalized

def main():
    parser = argparse.ArgumentParser(description="Build Hermes-style dataset.")
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("data/raw"),
        help="Directory containing raw JSONL files."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/splits"),
        help="Directory to write train/val/test splits."
    )
    parser.add_argument(
        "--train-split",
        type=float,
        default=0.8,
        help="Proportion of data to use for training."
    )
    parser.add_argument(
        "--val-split",
        type=float,
        default=0.1,
        help="Proportion of data to use for validation."
    )
    parser.add_argument(
        "--test-split",
        type=float,
        default=0.1,
        help="Proportion of data to use for test."
    )
    parser.add_argument(
        "--min-turns",
        type=int,
        default=2,
        help="Minimum number of turns in a conversation."
    )
    parser.add_argument(
        "--max-turns",
        type=int,
        default=100,
        help="Maximum number of turns in a conversation."
    )
    parser.add_argument(
        "--dedup",
        action="store_true",
        help="Enable deduplication based on conversation hash."
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for shuffling."
    )
    args = parser.parse_args()

    # Validate splits
    total = args.train_split + args.val_split + args.test_split
    if abs(total - 1.0) > 1e-9:
        sys.exit("Error: train+val+test splits must sum to 1.0")

    # Collect all conversations
    conversations = []  # each element: (conv_id, conversation)
    seen_hashes = set()
    raw_files = list(args.input_dir.glob("*.jsonl"))
    if not raw_files:
        sys.exit(f"No JSONL files found in {args.input_dir}")

    for file_path in raw_files:
        with file_path.open("r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                except json.JSONDecodeError as e:
                    print(f"Warning: Skipping invalid JSON in {file_path}:{line_num}: {e}")
                    continue

                valid, conv = validate_conversation(data)
                if not valid:
                    print(f"Warning: Skipping invalid conversation in {file_path}:{line_num}")
                    continue

                # Check turn count
                if not (args.min_turns <= len(conv) <= args.max_turns):
                    print(f"Warning: Skipping conversation with {len(conv)} turns (not in [{args.min_turns}, {args.max_turns}])")
                    continue

                # Deduplication
                if args.dedup:
                    h = hash_conversation(conv)
                    if h in seen_hashes:
                        continue
                    seen_hashes.add(h)

                # We don't have an id from the original data if it was a list.
                # We'll generate one based on the hash if needed.
                conv_id = data.get("id") if isinstance(data, dict) and "id" in data else None
                if conv_id is None:
                    conv_id = hash_conversation(conv)[:16]  # short hash

                conversations.append((conv_id, conv))

    if not conversations:
        sys.exit("No valid conversations found after filtering.")

    # Shuffle
    random.seed(args.seed)
    random.shuffle(conversations)

    # Split
    n_total = len(conversations)
    n_train = int(n_total * args.train_split)
    n_val = int(n_total * args.val_split)
    # The rest goes to test
    n_test = n_total - n_train - n_val

    splits = {
        "train": conversations[:n_train],
        "val": conversations[n_train:n_train + n_val],
        "test": conversations[n_train + n_val:],
    }

    # Write output
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for split_name, split_data in splits.items():
        out_file = args.output_dir / f"{split_name}.jsonl"
        with out_file.open("w", encoding="utf-8") as f:
            for conv_id, conv in split_data:
                # We output a JSON object with id and conversation
                out_obj = {
                    "id": conv_id,
                    "messages": conv
                }
                f.write(json.dumps(out_obj) + "\n")
        print(f"Wrote {len(split_data)} conversations to {out_file}")

    # mlx-lm expects valid.jsonl, while this repo historically used val.jsonl.
    valid_file = args.output_dir / "valid.jsonl"
    val_file = args.output_dir / "val.jsonl"
    valid_file.write_text(val_file.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"Wrote validation alias to {valid_file}")

    # Print summary
    print("\n=== Dataset Summary ===")
    print(f"Total conversations: {n_total}")
    print(f"Train: {len(splits['train'])} ({len(splits['train'])/n_total:.1%})")
    print(f"Val: {len(splits['val'])} ({len(splits['val'])/n_total:.1%})")
    print(f"Test: {len(splits['test'])} ({len(splits['test'])/n_total:.1%})")
    print(f"Deduplication enabled: {args.dedup}")
    print(f"Unique conversation hashes: {len(seen_hashes) if args.dedup else 'N/A'}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
