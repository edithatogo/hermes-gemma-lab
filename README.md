# Hermes Gemma Lab

Training and packaging workspace for Gemma-family and Qwen3 4B first-pass Hermes-style fine-tunes.

Status: scaffolded

Folder structure:
- data/raw/ — raw collected conversations
- data/clean/ — cleaned, deduped conversations
- data/splits/ — train/val/test splits in JSONL
- data/strict_tool_call/ — isolated strict tool-call seed lane and materialized splits
- experiments/gemma4-e4b/ — Gemma-family MLX LoRA training outputs
- experiments/qwen3-4b/ — Qwen3 4B MLX LoRA training outputs
- eval/ — evaluation prompts and results
- exports/hf/ — artifacts for Hugging Face publishing
- scripts/ — helper scripts for dataset, training, eval, export
- modelfiles/ — Ollama Modelfile(s)

Export policy:

- `scripts/export_gguf.sh` and `scripts/export_ollama.sh` default to `$HERMES_EXPORT_ROOT/ollama/<model>` when `scripts/env.sh` is sourced.
- If `$HERMES_EXPORT_ROOT` is not set and `/Volumes/PortableSSD` exists, exports default to `/Volumes/PortableSSD/hermes-exports/ollama/<model>`.
- Keep merged models, GGUF files, and Ollama packages out of the repo tree.

Configs:

- `scripts/train_config.yaml` — Gemma-family default.
- `scripts/train_config.qwen3-4b.smoke.yaml` — first end-to-end smoke run; use this before the longer Qwen3 config.
- `scripts/train_config.qwen3-4b.yaml` — Qwen3 4B experiment, currently the preferred first new bleeding-edge track for Hermes agent behavior.
- `scripts/train_config.qwen3-4b.candidate.yaml` — local-safe Qwen3 4B follow-on with early response-gate checkpoints and SSD-first defaults.
- `scripts/train_config.qwen3-4b.toolcall-repair.yaml` — targeted Qwen3 4B strict tool-call repair proof; not publishable because it trains on benchmark-mirrored seed data.
- `scripts/train_config.qwen3-4b.strict-toolcall.yaml` — held-out promotion proof against the isolated strict tool-call seed lane; current run is not publishable because held-out strict pass is below `1.000`.
- `scripts/train_config.qwen3-4b.strict-toolcall-expanded.yaml` — expanded strict tool-call retrain; completed but not publishable because held-out strict pass is `0.250`.
- `scripts/train_config.qwen3-4b.strict-toolcall-v2.yaml` — format-guard retrain; completed but not publishable because held-out strict pass is `0.250`.
- `scripts/train_config.qwen3-4b.strict-toolcall-v3-no-think.yaml` — `/no_think`-augmented retrain; completed but not publishable because held-out strict pass is `0.250`.
- `scripts/train_config.qwen3.6-35b-a3b.experimental.yaml` — Qwen3.6 frontier MoE smoke config; inference/teacher target first.
- `scripts/train_config.gemma4-26b-a4b.experimental.yaml` — Gemma 4 26B A4B smoke config; runtime target first.
- `scripts/train_config.hermes4-14b.experimental.yaml` — Hermes 4 14B smoke config; baseline/teacher target first.

Strict tool-call seed lane:

- [docs/strict-tool-call-lane.md](./docs/strict-tool-call-lane.md) — format, split policy, benchmark alignment, and SSD/artifact rules.
- [data/strict_tool_call/EXPANSION.md](./data/strict_tool_call/EXPANSION.md) — expanded-data source policy, contamination guard, and promotion criteria.
- [eval/qwen3-4b-strict-toolcall-expanded-summary.md](./eval/qwen3-4b-strict-toolcall-expanded-summary.md) — completed expanded-data retrain summary and blocked publication decision.
- [eval/qwen3-4b-strict-toolcall-v2-v3-summary.md](./eval/qwen3-4b-strict-toolcall-v2-v3-summary.md) — format-guard and `/no_think` augmentation results.
