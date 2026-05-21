# Qwen3 4B Strict Tool-Call Expanded Summary

## Training

- Config: `scripts/train_config.qwen3-4b.strict-toolcall-expanded.yaml`
- Base model: `Qwen/Qwen3-4B-MLX-4bit`
- Adapter: `experiments/qwen3-4b-strict-toolcall-expanded/lora_adapter`
- Dataset: `data/strict_tool_call/expanded_splits_v1`
- Rows: 33 train, 4 validation, 5 test
- Iterations: 120
- Effective trained tokens: 33,133
- Final validation loss: 0.917
- Best observed validation loss: 0.795 at iteration 50
- Peak memory: 3.785 GB
- Wall time: 172.6 seconds

## Benchmark Results

| Suite / Checkpoint | Strict Pass | Diagnostic Empty-Think-Stripped Pass | Notes |
|---|---:|---:|---|
| mirrored final | 0.167 | 0.833 | Regression suite, not held-out evidence |
| held-out final | 0.250 | 0.750 | Publication gate failed |
| mirrored iter50 | 0.167 | 1.000 | Best validation-loss checkpoint |
| held-out iter50 | 0.125 | 0.500 | Worse than final on held-out |

Final held-out details:

- Strict JSON validity: 0.000
- Strict argument correctness: 1.000
- Invalid-tool handling: 1.000
- Multi-turn repair: 0.000
- Raw output: `/Volumes/PortableSSD/hermes-evals/tool-call-benchmark/qwen3-4b-strict-toolcall-expanded-heldout-nothink-20260522`

## Decision

The adapter is not publishable. Expanded training improved held-out argument correctness to 1.000, but strict JSON/tool-call shape still fails because the model keeps emitting empty thinking wrappers and repair cases remain fragile.
