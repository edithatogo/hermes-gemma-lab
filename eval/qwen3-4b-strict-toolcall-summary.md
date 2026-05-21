# Qwen3 4B Strict Tool-Call Heldout Summary

## Training

- Config: `scripts/train_config.qwen3-4b.strict-toolcall.yaml`
- Base model: `Qwen/Qwen3-4B-MLX-4bit`
- Adapter: `experiments/qwen3-4b-strict-toolcall/lora_adapter`
- Dataset: `data/strict_tool_call/splits`
- Iterations: 80
- Effective trained tokens: 28,020
- Final validation loss: 0.949
- Best observed validation loss: 0.762 at iteration 40
- Peak memory: 3.785 GB
- Wall time: 119.6 seconds

## Benchmark Results

| Suite | Strict Pass | Diagnostic Empty-Think-Stripped Pass | Notes |
|---|---:|---:|---|
| `benchmarks/tool_call_local/suite.json` | 0.167 | 1.000 | Mirrored regression suite; not held-out evidence |
| `benchmarks/tool_call_local/heldout_suite.json` | 0.250 | 0.750 | Publication gate failed |

Held-out details:

- Strict JSON validity: 0.000
- Strict argument correctness: 0.667
- Invalid-tool handling: 1.000
- Multi-turn repair: 0.000
- Raw output: `/Volumes/PortableSSD/hermes-evals/tool-call-benchmark/qwen3-4b-strict-toolcall-heldout-nothink-20260522`

## Decision

The adapter is not publishable. It improves mirrored shape behavior after runtime normalization, but held-out strict tool calling remains too weak. Keep Hugging Face publication blocked.
