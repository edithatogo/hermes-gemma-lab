# Qwen3 4B Smoke Evaluation Summary

Date: 2026-05-21

## Run

- Base model: `Qwen/Qwen3-4B-MLX-4bit`
- Adapter: `experiments/qwen3-4b-smoke/lora_adapter`
- Training config: `scripts/train_config.qwen3-4b.smoke.yaml`
- Prompt set: `eval/prompts.jsonl`
- Prompt count: 100
- Max generation tokens: 128
- Storage environment: `HERMES_STORAGE_ROOT=/Volumes/PortableSSD`, `HF_HOME=/Volumes/PortableSSD/huggingface`, `HF_HUB_CACHE=/Volumes/PortableSSD/huggingface/hub`, `TMPDIR=/Volumes/PortableSSD/tmp`
- Hugging Face auth: SSD-backed `HF_HOME` logged in as `edithatogo`

## Training Result

- Iterations: 10
- Trained tokens: 2,889
- Final train loss: 3.544
- Final validation loss: 2.386
- Peak memory: 3.944 GB
- Training elapsed time: 20.0 seconds after model download
- Adapter weights: `experiments/qwen3-4b-smoke/lora_adapter/adapters.safetensors`

## Evaluation Commands

```bash
source scripts/env.sh
cd gemma4
../.venv/bin/python scripts/evaluate.py \
  --model Qwen/Qwen3-4B-MLX-4bit \
  --prompts eval/prompts.jsonl \
  --output eval/qwen3-4b-base-results.jsonl \
  --report eval/qwen3-4b-base-report.html \
  --max-tokens 128

../.venv/bin/python scripts/evaluate.py \
  --model Qwen/Qwen3-4B-MLX-4bit \
  --adapter experiments/qwen3-4b-smoke/lora_adapter \
  --prompts eval/prompts.jsonl \
  --output eval/qwen3-4b-smoke-adapter-results.jsonl \
  --report eval/qwen3-4b-smoke-adapter-report.html \
  --max-tokens 128
```

## Metrics

| Model | Prompts | Avg Latency | Avg Response Length | Empty Responses |
|---|---:|---:|---:|---:|
| Base | 100 | 2.151s | 94.70 words | 0 |
| Smoke adapter | 100 | 2.397s | 92.64 words | 0 |

Category-level average response lengths:

| Category | Base Words | Adapter Words |
|---|---:|---:|
| tool_use | 81.40 | 78.64 |
| code | 95.50 | 93.85 |
| long_context | 101.93 | 100.07 |
| reasoning | 100.07 | 99.93 |
| safety | 105.20 | 102.90 |
| factual | 103.00 | 102.00 |
| formatting | 82.60 | 74.40 |

## Response Gate

Both base and smoke adapter pass `scripts/eval_response_gate.py --strict`. Unlike the LFM2.5 full-smoke adapter, the Qwen3 smoke adapter does not collapse to empty or near-empty outputs.

## Decision

This is a valid local smoke proof for Qwen3 4B on the M1/32 GB Mac lane. It is not a quality claim because it trained for only 2,889 tokens. The next Qwen recipe should use the same response gate, then expand training tokens only after a short early-eval checkpoint remains stable.
