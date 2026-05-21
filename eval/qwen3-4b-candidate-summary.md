# Qwen3 4B Candidate Evaluation Summary

Date: 2026-05-22

## Run

- Base model: `Qwen/Qwen3-4B-MLX-4bit`
- Adapter: `experiments/qwen3-4b-candidate/lora_adapter`
- Training config: `scripts/train_config.qwen3-4b.candidate.yaml`
- Prompt set: `eval/prompts.jsonl`
- Prompt count: 100
- Max generation tokens: 128
- Storage environment: `HERMES_STORAGE_ROOT=/Volumes/PortableSSD`, `HF_HOME=/Volumes/PortableSSD/huggingface`, `HF_HUB_CACHE=/Volumes/PortableSSD/huggingface/hub`, `TMPDIR=/Volumes/PortableSSD/tmp`

## Training Result

- Iterations: 60
- Trained tokens: 25,094
- Final train loss: 0.947
- Final validation loss: 2.248
- Peak memory: 3.962 GB
- Training elapsed time: 192.1 seconds after model load
- Adapter weights: `experiments/qwen3-4b-candidate/lora_adapter/adapters.safetensors`
- Checkpoint cadence: every 5 steps

## Evaluation Commands

```bash
source ../scripts/env.sh
../.venv/bin/python scripts/evaluate.py \
  --model Qwen/Qwen3-4B-MLX-4bit \
  --adapter experiments/qwen3-4b-candidate/lora_adapter \
  --prompts eval/prompts.jsonl \
  --output eval/qwen3-4b-candidate-results.jsonl \
  --report eval/qwen3-4b-candidate-report.html \
  --max-tokens 128

source scripts/env.sh
./.venv/bin/python scripts/eval_response_gate.py \
  gemma4/eval/qwen3-4b-candidate-results.jsonl \
  --strict
```

## Hermes-Local Metrics

| Model | Prompts | Avg Latency | Avg Response Length | Empty Responses |
|---|---:|---:|---:|---:|
| Base smoke reference | 100 | 2.151s | 94.70 words | 0 |
| Smoke adapter reference | 100 | 2.397s | 92.64 words | 0 |
| Candidate adapter | 100 | 2.49s | 91.60 words | 0 |

Category-level average response lengths for the candidate:

| Category | Candidate Words |
|---|---:|
| tool_use | 84.00 |
| code | 90.60 |
| long_context | 99.00 |
| reasoning | 103.80 |
| safety | 78.40 |
| factual | 105.40 |
| formatting | 73.60 |

## Response Gate

The candidate adapter passes `scripts/eval_response_gate.py --strict`. It did not collapse to empty or near-empty responses.

## Tool-Call Benchmark

```bash
source scripts/env.sh
./.venv/bin/python scripts/run_tool_call_benchmark.py \
  --model Qwen/Qwen3-4B-MLX-4bit \
  --adapter gemma4/experiments/qwen3-4b-candidate/lora_adapter \
  --suite benchmarks/tool_call_local/suite.json \
  --user-prefix /no_think \
  --run-id qwen3-4b-candidate-toolcall-nothink-20260522
```

| Model | Cases | Pass Rate | JSON Validity | Argument Accuracy | Invalid-Tool Handling | Multi-Turn Repair |
|---|---:|---:|---:|---:|---:|---:|
| Base `/no_think` | 6 | 0.167 | 0.000 | 0.200 | 1.000 | 0.000 |
| Candidate `/no_think` | 6 | 0.167 | 0.000 | 0.000 | 1.000 | 0.000 |

Raw tool-call outputs are under:

- `/Volumes/PortableSSD/hermes-evals/tool-call-benchmark/qwen3-4b-base-toolcall-nothink-20260522`
- `/Volumes/PortableSSD/hermes-evals/tool-call-benchmark/qwen3-4b-candidate-toolcall-nothink-20260522`

## Decision

This is a useful local candidate-training proof, but it is not a publishable Hermes tool-calling adapter. It improves the amount of training over the 2,889-token smoke run and remains stable on response-collapse checks, but the current data/config does not teach the strict `<tool_call>{"name": ..., "arguments": ...}</tool_call>` shape. The next training dataset should add explicit tool-call target examples and the tool-call benchmark should become an early stopping gate.
