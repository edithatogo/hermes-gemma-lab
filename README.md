# Hermes Gemma Lab

Training and packaging workspace for Gemma-family and Qwen3 4B first-pass Hermes-style fine-tunes.

Status: scaffolded

Folder structure:
- data/raw/ — raw collected conversations
- data/clean/ — cleaned, deduped conversations
- data/splits/ — train/val/test splits in JSONL
- experiments/gemma4-e4b/ — Gemma-family MLX LoRA training outputs
- experiments/qwen3-4b/ — Qwen3 4B MLX LoRA training outputs
- eval/ — evaluation prompts and results
- exports/hf/ — artifacts for Hugging Face publishing
- scripts/ — helper scripts for dataset, training, eval, export
- modelfiles/ — Ollama Modelfile(s)

Configs:

- `scripts/train_config.yaml` — Gemma-family default.
- `scripts/train_config.qwen3-4b.smoke.yaml` — first end-to-end smoke run; use this before the longer Qwen3 config.
- `scripts/train_config.qwen3-4b.yaml` — Qwen3 4B experiment, currently the preferred first new bleeding-edge track for Hermes agent behavior.
- `scripts/train_config.qwen3.6-35b-a3b.experimental.yaml` — Qwen3.6 frontier MoE smoke config; inference/teacher target first.
- `scripts/train_config.gemma4-26b-a4b.experimental.yaml` — Gemma 4 26B A4B smoke config; runtime target first.
- `scripts/train_config.hermes4-14b.experimental.yaml` — Hermes 4 14B smoke config; baseline/teacher target first.
