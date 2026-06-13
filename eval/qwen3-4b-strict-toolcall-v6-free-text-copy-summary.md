# Qwen3 4B Strict Tool-Call V6 Free-Text Copy Summary

Date: 2026-06-13

## Purpose

V6 tested whether adding non-heldout free-text-copy repair rows could restore
the held-out lab-order argument failure observed in V5 and in the Gemma 4 26B
A4B runtime probe. The target failure class is narrow: short user-provided
`message`, `note`, `reason`, or `summary` strings must be copied exactly into
tool-call arguments rather than paraphrased.

## Training

- Base model: `Qwen/Qwen3-4B-MLX-4bit`
- Config: `scripts/train_config.qwen3-4b.strict-toolcall-v6-free-text-copy.yaml`
- Data: `data/strict_tool_call/expanded_splits_v6_free_text_copy`
- Final adapter: `experiments/qwen3-4b-strict-toolcall-v6-free-text-copy/lora_adapter`
- Recommended checkpoint alias: `experiments/qwen3-4b-strict-toolcall-v6-free-text-copy/lora_adapter_iter125`
- Train rows: `116`
- Validation rows: `5`
- Iterations: `170`
- Trained tokens: `43,724`
- Best observed validation loss: `0.636` at iteration `110`
- Final validation loss: `0.670`
- Peak memory: `3.785 GB`
- Wall time: `241.9 s`
- Raw training log:
  `/Volumes/PortableSSD/hermes-evals/training/qwen3-4b-strict-toolcall-v6-free-text-copy-20260613.log`

The exact best validation point was not saved because checkpoints were written
every 25 iterations. Iteration 125 is the recommended checkpoint because it
passes both strict held-out and mirrored suites, while iteration 100 fails the
mirrored argument extraction case and final iteration 170 regresses on the
held-out lab-order case.

## Results

All local runs used `/no_think` plus assistant prefill
`<think>\n\n</think>\n\n`.

| Checkpoint | Suite | Cases | Passed | Pass rate | Residual failure |
|---|---|---:|---:|---:|---|
| Iter 100 | Held-out strict local tool-call | 8 | 8 | `1.000` | none |
| Iter 125 | Held-out strict local tool-call | 8 | 8 | `1.000` | none |
| Final 170 | Held-out strict local tool-call | 8 | 7 | `0.875` | `heldout-argument-correctness-lab-order` |
| Iter 100 | Mirrored regression | 6 | 5 | `0.833` | `argument-correctness-emr` |
| Iter 125 | Mirrored regression | 6 | 6 | `1.000` | none |
| Iter 100 | BFCL-style pilot | 3 | 2 | `0.667` | `bfcl-invalid-tool` |
| Iter 125 | BFCL-style pilot | 3 | 2 | `0.667` | `bfcl-invalid-tool` |
| Iter 100 | Coding sanity pilot | 3 | 2 | `0.667` | `coding-python-filter-even` |
| Iter 125 | Coding sanity pilot | 3 | 2 | `0.667` | `coding-python-filter-even` |
| Iter 100 | IFEval-style pilot | 3 | 3 | `1.000` | none |
| Iter 125 | IFEval-style pilot | 3 | 2 | `0.667` | `ifeval-forbidden-word` |

## Artifact Roots

- Iter 100 held-out:
  `/Volumes/PortableSSD/hermes-evals/tool-call-benchmark/qwen3-4b-strict-toolcall-v6-free-text-copy-iter100-heldout-prefill-20260613`
- Iter 125 held-out:
  `/Volumes/PortableSSD/hermes-evals/tool-call-benchmark/qwen3-4b-strict-toolcall-v6-free-text-copy-iter125-heldout-prefill-20260613`
- Final 170 held-out:
  `/Volumes/PortableSSD/hermes-evals/tool-call-benchmark/qwen3-4b-strict-toolcall-v6-free-text-copy-final170-heldout-prefill-20260613`
- Iter 125 mirrored:
  `/Volumes/PortableSSD/hermes-evals/tool-call-benchmark/qwen3-4b-strict-toolcall-v6-free-text-copy-iter125-mirrored-prefill-20260613`
- Iter 125 pilots:
  `/Volumes/PortableSSD/hermes-evals/standard-benchmarks/local-pilots/qwen3-4b-strict-toolcall-v6-free-text-copy-iter125-local-bfcl-prefill-20260613`
  `/Volumes/PortableSSD/hermes-evals/standard-benchmarks/local-pilots/qwen3-4b-strict-toolcall-v6-free-text-copy-iter125-local-coding-prefill-20260613`
  `/Volumes/PortableSSD/hermes-evals/standard-benchmarks/local-pilots/qwen3-4b-strict-toolcall-v6-free-text-copy-iter125-local-ifeval-prefill-20260613`

## Decision

Promote iteration 125 as the local Hermes strict tool-call candidate for
continued runtime integration and publication packaging. It restores the held-
out strict gate to `1.000` and keeps mirrored regression at `1.000`.

Do not use the final 170-iteration adapter as the default; it overfits relative
to the strict held-out gate. Keep broader instruction-following and pilot
failures in a separate polish lane so they do not destabilize exact tool-call
argument extraction.
