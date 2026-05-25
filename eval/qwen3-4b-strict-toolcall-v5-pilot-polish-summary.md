# Qwen3 4B Strict Tool-Call V5 Pilot Polish Summary

Date: 2026-05-25

## Purpose

V5 tested whether adding non-heldout invalid-tool refusal examples to the V4
strict-tool-call dataset could improve the BFCL-style pilot failure without
weakening the strict Hermes held-out gate.

The first materialized V5 draft also included ordinary instruction-following
rows. The strict tool-call audit rejected those rows because their assistant
messages were neither tool calls nor refusals. They were removed before
training; broader instruction-following polish belongs in a separate adapter
lane.

## Training

- Base model: `Qwen/Qwen3-4B-MLX-4bit`
- Config: `scripts/train_config.qwen3-4b.strict-toolcall-v5-pilot-polish.yaml`
- Data: `data/strict_tool_call/expanded_splits_v5_pilot_polish`
- Adapter: `experiments/qwen3-4b-strict-toolcall-v5-pilot-polish/lora_adapter`
- Train rows: `100`
- Validation rows: `5`
- Iterations: `150`
- Trained tokens: `37,867`
- Best observed validation loss: `0.640` at iterations `110` and `120`
- Final validation loss: `0.689`
- Peak memory: `3.785 GB`
- Wall time: `273.1 s`
- Raw training log:
  `/Volumes/PortableSSD/hermes-evals/tool-call-benchmark/qwen3-4b-strict-toolcall-v5-pilot-polish-train-20260525.log`

## Results

All local runs used `/no_think` plus assistant prefill
`<think>\n\n</think>\n\n`.

| Suite | Pass rate | Decision |
|---|---:|---|
| Held-out strict local tool-call | `0.875` | Failed publication gate |
| Mirrored regression | `1.000` | Passed regression only |
| BFCL-style pilot | `1.000` | Improved over V4 pilot |
| IFEval-style pilot | `0.667` | Unchanged from V4 pilot |
| Coding pilot | `1.000` | Unchanged from V4 pilot |

Residual held-out failure:

- `heldout-argument-correctness-lab-order`: emitted valid JSON and valid tool
  names, but set `priority` to `"priority"` instead of the expected extracted
  value.

Residual IFEval-style pilot failure:

- `ifeval-forbidden-word`: avoided the forbidden word but missed the required
  phrase `completed successfully`.

## Decision

Do not promote V5. It improved the BFCL-style pilot, but the strict held-out
Hermes tool-call gate regressed from V4's `1.000` to `0.875`. V4 remains the
recommended and public adapter. V5 should inform the next experiment: add
invalid-tool polish only if paired with argument-extraction retention examples
and an early-stop/checkpoint selection rule.
