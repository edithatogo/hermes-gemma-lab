#!/usr/bin/env python3
"""
Side-by-side comparison of base model vs fine-tuned model on the same prompts.
Generates a self-contained HTML report.

Usage:
  python3 scripts/compare.py \
    --base-model google/gemma-4-E4B-it \
    --ft-model google/gemma-4-E4B-it \
    --ft-adapter experiments/gemma4-e4b/lora_adapter \
    --prompts eval/prompts.jsonl \
    --output eval/comparison.html
"""
import argparse
import json
import sys
import time
from pathlib import Path

def generate(model, tokenizer, prompt, max_tokens=256):
    from mlx_lm import generate as mlx_generate
    t0 = time.time()
    response = mlx_generate(model, tokenizer, prompt=prompt, max_tokens=max_tokens, verbose=False)
    elapsed = time.time() - t0
    return response.strip(), elapsed

def main():
    parser = argparse.ArgumentParser(description="Side-by-side model comparison")
    parser.add_argument("--base-model", required=True)
    parser.add_argument("--ft-model", required=True)
    parser.add_argument("--ft-adapter", help="LoRA adapter for fine-tuned model")
    parser.add_argument("--prompts", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("eval/comparison.html"))
    parser.add_argument("--max-tokens", type=int, default=256)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.dry_run:
        print(f"Base model:  {args.base_model}")
        print(f"FT model:    {args.ft_model}")
        print(f"FT adapter:  {args.ft_adapter or '(none)'}")
        print(f"Prompts:     {args.prompts}")
        print(f"Output:      {args.output}")
        return 0

    from mlx_lm import load

    # Load prompts
    prompts = []
    with args.prompts.open() as f:
        for line in f:
            data = json.loads(line.strip())
            msgs = data.get("messages", [])
            user_msgs = [m["content"] for m in msgs if m["role"] == "user"]
            prompts.append({
                "text": user_msgs[-1] if user_msgs else data.get("prompt", ""),
                "category": data.get("category", "general"),
            })
    print(f"Loaded {len(prompts)} prompts")

    # Load base model
    print(f"\nLoading base model: {args.base_model}")
    t0 = time.time()
    base_model, base_tokenizer = load(args.base_model)
    print(f"  Loaded in {time.time()-t0:.1f}s")

    # Load fine-tuned model
    print(f"Loading fine-tuned model: {args.ft_model}")
    t0 = time.time()
    ft_model, ft_tokenizer = load(args.ft_model, adapter_path=args.ft_adapter)
    print(f"  Loaded in {time.time()-t0:.1f}s")

    # Generate responses
    results = []
    for i, p in enumerate(prompts):
        text = p["text"]
        cat = p["category"]
        print(f"  [{i+1}/{len(prompts)}] {cat}...")

        base_resp, base_lat = generate(base_model, base_tokenizer, text, args.max_tokens)
        ft_resp, ft_lat = generate(ft_model, ft_tokenizer, text, args.max_tokens)

        results.append({
            "category": cat,
            "prompt": text,
            "base": {"response": base_resp, "latency": base_lat, "words": len(base_resp.split())},
            "ft": {"response": ft_resp, "latency": ft_lat, "words": len(ft_resp.split())},
        })

    # Generate HTML report
    html = """<html><head><meta charset='utf-8'>
<title>Model Comparison: Base vs Fine-Tuned</title>
<style>
  body{font-family:-apple-system,BlinkMacSystemFont,sans-serif;max-width:1400px;margin:auto;padding:20px;background:#fafafa}
  h1{color:#222;border-bottom:3px solid #333;padding-bottom:10px}
  .card{background:white;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.1);margin:20px 0;overflow:hidden}
  .card-header{background:#333;color:white;padding:12px 20px;font-weight:600}
  .card-body{display:grid;grid-template-columns:1fr 1fr;gap:0}
  .col{padding:20px}
  .col-base{border-right:1px solid #eee;background:#fff8f0}
  .col-ft{background:#f0fff4}
  .col h3{margin:0 0 10px 0;font-size:14px;text-transform:uppercase;letter-spacing:1px;color:#666}
  .response{white-space:pre-wrap;font-size:14px;line-height:1.6;font-family:monospace}
  .meta{font-size:12px;color:#999;margin-top:10px}
  .prompt-text{background:#f5f5f5;padding:10px 20px;font-style:italic;color:#555;border-bottom:1px solid #eee}
  .badge{display:inline-block;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600;margin-left:8px}
  .badge-base{background:#ffe0b2;color:#e65100}
  .badge-ft{background:#c8e6c9;color:#1b5e20}
</style></head><body>
<h1>Model Comparison: Base vs Fine-Tuned</h1>
<p>""" + args.base_model + """ vs """ + args.ft_model + """ | """ + str(len(results)) + """ prompts</p>
"""
    for r in results:
        html += f"""
<div class='card'>
  <div class='card-header'>[{r['category']}]</div>
  <div class='prompt-text'>{r['prompt']}</div>
  <div class='card-body'>
    <div class='col col-base'>
      <h3>Base Model <span class='badge badge-base'>{r['base']['words']}w · {r['base']['latency']:.1f}s</span></h3>
      <div class='response'>{r['base']['response']}</div>
    </div>
    <div class='col col-ft'>
      <h3>Fine-Tuned <span class='badge badge-ft'>{r['ft']['words']}w · {r['ft']['latency']:.1f}s</span></h3>
      <div class='response'>{r['ft']['response']}</div>
    </div>
  </div>
</div>
"""
    html += "</body></html>"

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(html)
    print(f"\nComparison report saved to {args.output}")

    # Summary
    base_avg_lat = sum(r["base"]["latency"] for r in results) / len(results)
    ft_avg_lat = sum(r["ft"]["latency"] for r in results) / len(results)
    base_avg_w = sum(r["base"]["words"] for r in results) / len(results)
    ft_avg_w = sum(r["ft"]["words"] for r in results) / len(results)
    print(f"\n  Base model:      avg {base_avg_w:.0f} words, {base_avg_lat:.2f}s")
    print(f"  Fine-tuned:      avg {ft_avg_w:.0f} words, {ft_avg_lat:.2f}s")

    return 0

if __name__ == "__main__":
    sys.exit(main())