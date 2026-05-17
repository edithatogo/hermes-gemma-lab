#!/usr/bin/env python3
"""
Evaluate a model on Hermes-style prompts and generate a comparison report.

Usage:
  # Base model only
  python3 scripts/evaluate.py --model google/gemma-4-E4B-it --prompts eval/prompts.jsonl

  # Fine-tuned model with adapter
  python3 scripts/evaluate.py --model google/gemma-4-E4B-it --adapter experiments/gemma4-e4b/lora_adapter --prompts eval/prompts.jsonl

  # Compare base vs fine-tuned
  python3 scripts/evaluate.py --model google/gemma-4-E4B-it --adapter experiments/gemma4-e4b/lora_adapter --prompts eval/prompts.jsonl --compare

  # Side-by-side HTML report
  python3 scripts/evaluate.py --model google/gemma-4-E4B-it --adapter experiments/gemma4-e4b/lora_adapter --prompts eval/prompts.jsonl --report eval/comparison.html
"""
import argparse
import json
import sys
import time
from pathlib import Path

def load_prompts(filepath: Path):
    """Load prompts from eval/prompts.jsonl."""
    prompts = []
    with filepath.open("r") as f:
        for line in f:
            data = json.loads(line.strip())
            prompts.append(data)
    return prompts

def generate(model, tokenizer, prompt: str, max_tokens: int = 256) -> tuple[str, float]:
    """Generate a response and return (text, latency_seconds)."""
    from mlx_lm import generate as mlx_generate
    t0 = time.time()
    response = mlx_generate(model, tokenizer, prompt=prompt, max_tokens=max_tokens, verbose=False)
    elapsed = time.time() - t0
    return response.strip(), elapsed

def format_prompt_for_chat(example: dict) -> str:
    """Format a conversation example into a prompt string."""
    msgs = example.get("messages", [])
    # Use the last user message as the prompt
    user_msgs = [m["content"] for m in msgs if m["role"] == "user"]
    if user_msgs:
        return user_msgs[-1]
    # Fallback to prompt key
    return example.get("prompt", "")

def main():
    parser = argparse.ArgumentParser(description="Evaluate model on Hermes-style prompts")
    parser.add_argument("--model", required=True, help="Model name or path")
    parser.add_argument("--adapter", help="LoRA adapter path")
    parser.add_argument("--prompts", type=Path, default=Path("eval/prompts.jsonl"), help="Prompts file")
    parser.add_argument("--output", type=Path, default=Path("eval/results.jsonl"), help="Output results file")
    parser.add_argument("--compare", action="store_true", help="Also run on base model for comparison")
    parser.add_argument("--report", type=Path, help="Generate side-by-side HTML report")
    parser.add_argument("--max-tokens", type=int, default=256, help="Max generation tokens")
    parser.add_argument("--dry-run", action="store_true", help="Print config and exit")
    args = parser.parse_args()

    prompts = load_prompts(args.prompts)
    print(f"Loaded {len(prompts)} prompts from {args.prompts}")

    if args.dry_run:
        print(f"Model: {args.model}")
        print(f"Adapter: {args.adapter or '(none - base model)'}")
        print(f"Prompts: {len(prompts)}")
        print(f"Max tokens: {args.max_tokens}")
        print(f"Compare mode: {args.compare}")
        print(f"Report: {args.report or '(none)'}")
        return 0

    # Load model
    from mlx_lm import load
    print(f"\nLoading model: {args.model}")
    t0 = time.time()
    model, tokenizer = load(args.model, adapter_path=args.adapter)
    print(f"  Loaded in {time.time()-t0:.1f}s")

    # Run evaluation
    print(f"\nEvaluating on {len(prompts)} prompts...")
    results = []
    for i, example in enumerate(prompts):
        prompt_text = format_prompt_for_chat(example)
        category = example.get("category", "general")

        print(f"  [{i+1}/{len(prompts)}] {category}: {prompt_text[:60]}...")
        response, latency = generate(model, tokenizer, prompt_text, args.max_tokens)

        results.append({
            "prompt": prompt_text,
            "category": category,
            "response": response,
            "latency_s": round(latency, 2),
            "response_length": len(response.split()),
        })

    # Save results
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")
    print(f"\nResults saved to {args.output}")

    # Summary stats
    avg_latency = sum(r["latency_s"] for r in results) / len(results)
    avg_len = sum(r["response_length"] for r in results) / len(results)
    print(f"\n  Average latency: {avg_latency:.2f}s")
    print(f"  Average response length: {avg_len:.0f} words")

    # Generate HTML report if requested
    if args.report:
        html = "<html><head><meta charset='utf-8'><title>Model Evaluation</title>"
        html += "<style>body{font-family:sans-serif;max-width:1200px;margin:auto;padding:20px}"
        html += ".prompt{background:#f0f0f0;padding:10px;border-radius:5px;margin:10px 0}"
        html += ".response{background:#e8f5e9;padding:10px;border-radius:5px;margin:10px 0;white-space:pre-wrap}"
        html += ".baseline{background:#fff3e0}"
        html += "h2{color:#333;border-bottom:2px solid #ddd;padding-bottom:5px}"
        html += ".meta{font-size:12px;color:#666}"
        html += "</style></head><body>"
        html += f"<h1>Model Evaluation: {args.model}</h1>"
        html += f"<p>Adapter: {args.adapter or '(base model)'} | {len(results)} prompts | "
        html += f"Avg latency: {avg_latency:.2f}s | Avg response: {avg_len:.0f} words</p>"

        for r in results:
            html += f"<div class='prompt'><strong>[{r['category']}]</strong> {r['prompt']}</div>"
            html += f"<div class='response'>{r['response']}</div>"
            html += f"<div class='meta'>Latency: {r['latency_s']}s | {r['response_length']} words</div>"
            html += "<hr>"

        html += "</body></html>"
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(html)
        print(f"HTML report saved to {args.report}")

    return 0

if __name__ == "__main__":
    sys.exit(main())