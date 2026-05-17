# Gemma 4 — Conductor Setup

This repo is Track 1 of the Hermes Training Hub.

## Hub References

| Document | Location |
|----------|----------|
| Hub conductor | `/Users/doughnut/GitHub/hermes-training/CONDUCTOR.md` |
| MoSCoW requirements | `/Users/doughnut/GitHub/hermes-training/REQUIREMENTS.md` |
| Architecture design | `/Users/doughnut/GitHub/hermes-training/DESIGN.md` |
| Interface contracts | `/Users/doughnut/GitHub/hermes-training/CONTRACTS.md` |

## Track Status

| Requirement | Status |
|-------------|--------|
| M1 MLX LoRA pipeline | ✅ scripts/train.py written, verified dry-run |
| M2 Download dataset | 🔄 download_hermes_dataset.py running |
| M3 Train on Hermes data | 🔄 Awaiting model + dataset downloads |
| M4 Save adapter | 🔄 Will run after training |
| M8 Dataset dedup | ✅ build_dataset.py tested on sample data |
| M9 Apple Silicon MLX | ✅ mlx + mlx-lm installed |
| M10 SSD caching | ✅ HF_HOME=/Volumes/PortableSSD/... |
| S1 Eval comparison | ✅ scripts/evaluate.py + compare.py written |
| S3 HF publishing | ✅ scripts/push_to_hf.sh + model cards written |

## Active Processes

| Process | PID | What |
|---------|-----|------|
| proc_73119ed18037 | 98060 | Gemma 4 model download (~16 GB, 3.5 MB/s) |
| proc_1f512fca91da | 39708 | Hermes dataset download (gemma4) |

## Contracts in Effect

- CONTRACT-001: `data/raw/*.jsonl` (Hermes-style messages format)
- CONTRACT-002: `data/splits/*.jsonl` (deduped, 80/10/10 split)
- CONTRACT-003: `scripts/train_config.yaml` (MLX LoRA params)
- CONTRACT-004: `experiments/gemma4-e4b/lora_adapter/` (adapter output)
- CONTRACT-005: `eval/` (eval input/output format)
- CONTRACT-006: `modelfiles/Gemma4-Hermes.Modelfile` (Ollama packaging)
- CONTRACT-007/008: HF repos (publishing format)

## Context Preservation Notes

When working here:
- Load `kanban-orchestrator` for task decomposition
- Load `kanban-worker` for implementation context
- This repo only tracks Gemma 4 work. LFM2 is in `/Users/doughnut/GitHub/hermes-training/lfm2/`
- Training runs on M1 Max 32GB — batch size capped at 4 for 8B models
- Downloads go to portable SSD at `/Volumes/PortableSSD/`
