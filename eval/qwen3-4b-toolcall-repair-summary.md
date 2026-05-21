# Qwen3 4B Tool-Call Repair Summary

## Training

- Config: `scripts/train_config.qwen3-4b.toolcall-repair.yaml`
- Base model: `Qwen/Qwen3-4B-MLX-4bit`
- Adapter: `experiments/qwen3-4b-toolcall-repair/lora_adapter`
- Dataset: `data/tool_call_splits`
- Iterations: 40
- Effective trained tokens: 10,603
- Final validation loss: 0.140
- Peak memory: 3.417 GB
- Wall time: 59.0 seconds

## Benchmark

- Command: `source scripts/env.sh && ./.venv/bin/python scripts/run_tool_call_benchmark.py --model Qwen/Qwen3-4B-MLX-4bit --adapter gemma4/experiments/qwen3-4b-toolcall-repair/lora_adapter --user-prefix /no_think --run-id qwen3-4b-toolcall-repair-nothink-20260522 --max-tokens 512`
- Output: `/Volumes/PortableSSD/hermes-evals/tool-call-benchmark/qwen3-4b-toolcall-repair-nothink-20260522`

| Metric | Strict Result | Diagnostic Empty-Think-Stripped Result |
|---|---:|---:|
| Pass rate | 0.167 | 0.833 |
| JSON validity | 0.000 | 0.800 |
| Argument correctness | 0.800 | 0.800 |
| Invalid-tool handling | 1.000 | 1.000 |
| Multi-turn repair | 0.000 | not promoted |

The diagnostic column removes only a leading empty `<think></think>` wrapper to separate runtime wrapper noise from actual tool-call mistakes. It does not change the publication gate.

## Decision

Do not publish this adapter to Hugging Face. It is a local proof that tool arguments are learnable, but it still fails strict output-shape requirements and the training split overlaps the benchmark suite.

Next steps:

- add a Hermes runtime normalizer for empty leading thinking wrappers before tool-call parsing
- retrain on the larger isolated `data/strict_tool_call` lane
- add a held-out tool-call benchmark that does not overlap the training seed
- require strict pass before any model-card checklist can be marked `Publication status: READY`
