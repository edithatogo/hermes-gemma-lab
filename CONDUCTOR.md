# Gemma/Qwen/Hermes — Conductor Context

This repo is the Gemma/Qwen/Hermes model track for the Hermes Training Hub.

## Hub References

| Document | Location |
|---|---|
| Hub conductor | `/Users/doughnut/GitHub/hermes-training/CONDUCTOR.md` |
| Benchmark plan | `/Users/doughnut/GitHub/hermes-training/BENCHMARKING_PLAN.md` |
| Standard benchmarks | `/Users/doughnut/GitHub/hermes-training/STANDARD_BENCHMARKS.md` |
| Documentation plan | `/Users/doughnut/GitHub/hermes-training/DOCUMENTATION_PLAN.md` |
| Applications | `/Users/doughnut/GitHub/hermes-training/APPLICATIONS.md` |

## Track Status

| Requirement | Status |
|---|---|
| MLX LoRA pipeline | Script fixed and readiness-validated |
| Dataset splits | Present: train/val/valid/test JSONL |
| Dataset compatibility | Chat dataset wrapper fixed for current `mlx-lm` |
| Qwen3 4B smoke config | Present |
| Qwen3 4B model download | Stalled unauthenticated; retry with `HF_TOKEN` or prefetch |
| Hermes 4 baseline config | Present as experimental/baseline target |
| Qwen3.6/Gemma4 MoE configs | Present as experimental runtime/teacher targets |
| SSD caching | Managed by hub `scripts/env.sh` |

## Current Models

| Model | Role | Status |
|---|---|---|
| `Qwen/Qwen3-4B-MLX-4bit` | Practical local fine-tune target | Smoke and 60-step candidate proof complete; tool-call data needs improvement |
| `NousResearch/Hermes-4-14B` | Hermes-aligned baseline/teacher | Configured; runtime proof before local training |
| `Qwen/Qwen3.6-35B-A3B` | Frontier MoE baseline/teacher | Runtime first, do not local-train by default |
| `google/gemma-4-26B-A4B-it` | Frontier MoE baseline | Runtime first, do not local-train by default |
| `lmstudio-community/gemma-4-E4B-it-MLX-4bit` | Original Gemma track default | Keep as fallback |

## Next Actions

1. Add explicit strict tool-call target data before extending Qwen3 training beyond the 25k-token candidate proof.
2. Keep `scripts/train_config.qwen3-4b.smoke.yaml` as the pipeline proof and `scripts/train_config.qwen3-4b.candidate.yaml` as the local-safe checkpoint cadence.
3. Re-run the local tool-call benchmark after any tool-call data update.
4. Use Hermes 4 14B as a behavior baseline and possible teacher/evaluator before training larger adapters.
5. Treat Qwen3.6/Gemma4 MoE as runtime/teacher candidates until memory and licensing proofs are documented.

## Contracts in Effect

- `data/raw/*.jsonl`: raw Hermes-style messages.
- `data/splits/*.jsonl`: train/val/valid/test split JSONL.
- `scripts/train_config*.yaml`: MLX LoRA or experimental config.
- `experiments/*/lora_adapter/`: ignored local adapter output.
- `eval/prompts.jsonl`: seed eval input, to be expanded.
- `modelfiles/*.Modelfile`: runtime packaging input.

## Application Notes

This track supports:

- stronger local coding assistant candidates
- Hermes-aligned tool-use and function-calling adapters
- baseline/teacher comparisons against Hermes 4
- runtime experiments with large active-sparse MoE models
- benchmark comparisons against LFM-family low-latency adapters

Do not publish a Qwen/Gemma/Hermes adapter until the standard benchmark gate in the hub passes.
