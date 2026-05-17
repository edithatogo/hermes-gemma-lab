#!/usr/bin/env python3
"""
Bakeoff script for comparing multiple models on a set of prompts.
"""
import argparse
import json
import sys
from pathlib import Path

def load_prompts(filepath: Path):
    """Load prompts from a JSONL file."""
    prompts = []
    with filepath.open('r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line.strip())
            prompts.append(data.get('prompt', ''))
    return prompts

def stub_generate(prompt: str, model_name: str) -> str:
    """Stub generation function. Replace with real model inference."""
    return f"[Stub response for {model_name}] {prompt[:50]}..."

def main():
    parser = argparse.ArgumentParser(description="Run model bakeoff on prompts.")
    parser.add_argument(
        "--prompts",
        type=Path,
        required=True,
        help="Path to JSONL file containing prompts."
    )
    parser.add_argument(
        "--models",
        nargs="+",
        default=["gemma-4-e4b-it"],
        help="List of model identifiers to evaluate."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("bakeoff_results.jsonl"),
        help="Path to save results."
    )
    args = parser.parse_args()

    prompts = load_prompts(args.prompts)
    results = []
    for prompt in prompts:
        for model in args.models:
            response = stub_generate(prompt, model)
            results.append({
                "prompt": prompt,
                "model": model,
                "response": response
            })

    with args.output.open('w', encoding='utf-8') as f:
        for res in results:
            f.write(json.dumps(res) + "\n")

    print(f"Saved {len(results)} results to {args.output}")
    return 0

if __name__ == "__main__":
    sys.exit(main())