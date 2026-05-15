# Gemma 4 Hermes Finetune Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Finetune Gemma 4 E4B-it on Hermes-style data using Apple Silicon-friendly tooling, then export an Ollama-ready build and publish reproducible artifacts to GitHub and Hugging Face.

**Architecture:**
Use a local MLX-based LoRA training pipeline on the M1 Max, with dataset curation, supervised finetuning, evaluation, export/quantization, and packaging separated into small scripts. Keep the base model and adapter artifacts versioned, and produce an Ollama Modelfile plus Hugging Face-compatible model cards and dataset snapshots.

**Tech Stack:**
- Python 3.11+
- mlx-lm / MLX
- datasets, pandas, pyarrow
- huggingface_hub
- llama.cpp for conversion/quantization
- Ollama for local serving
- git / gh for publishing

---

### Task 1: Create repo scaffolding

**Objective:** Set up reproducible folders for data, experiments, evals, exports, and scripts.

**Files:**
- Create: `data/raw/`, `data/clean/`, `data/splits/`
- Create: `experiments/gemma4-e4b/`
- Create: `eval/`
- Create: `exports/hf/`
- Create: `scripts/`
- Modify: `README.md`

**Step 1: Add a minimal README**

**Step 2: Verify folder structure exists**

Run: `find . -maxdepth 2 -type d | sort`
Expected: the directories above are present.

**Step 3: Commit**

```bash
git add -A
git commit -m "chore: scaffold gemma finetune workspace"
```

### Task 2: Add model bakeoff harness

**Objective:** Create a benchmark script to compare Gemma 4, Ministral 3 8B, Qwen3 8B, and LFM2 8B on the same Hermes-style prompts.

**Files:**
- Create: `scripts/bakeoff.py`
- Create: `eval/prompts.jsonl`
- Create: `eval/README.md`

**Step 1: Write a failing smoke test**

Create a tiny prompt loader test or a CLI smoke check that fails until the script exists.

**Step 2: Implement prompt loading and model invocation stubs**

**Step 3: Verify output is a JSONL score file**

Run: `python scripts/bakeoff.py --help`
Expected: usage text.

### Task 3: Build Hermes-style dataset pipeline

**Objective:** Convert source conversations into a training-ready chat/tool schema.

**Files:**
- Create: `scripts/build_dataset.py`
- Create: `data/clean/`
- Create: `data/splits/`

**Step 1: Define input schema and output schema**

**Step 2: Implement filtering, de-duplication, and split generation**

**Step 3: Verify dataset manifests and sample rows**

Run: `python scripts/build_dataset.py --help`
Expected: usage text.

### Task 4: Train Gemma 4 LoRA on Apple Silicon

**Objective:** Run MLX LoRA training for a first adapter checkpoint.

**Files:**
- Create: `scripts/train_mlx_lora.sh`
- Create: `scripts/train_config.yaml`
- Create: `experiments/gemma4-e4b/`

**Step 1: Wire training command**

**Step 2: Run a short dry-run / tiny subset**

**Step 3: Run real finetune**

### Task 5: Evaluate and export

**Objective:** Measure quality and export to Ollama/Hugging Face formats.

**Files:**
- Create: `scripts/evaluate.py`
- Create: `scripts/export_gguf.sh`
- Create: `modelfiles/Gemma4-Hermes.Modelfile`

**Step 1: Run evaluation harness**

**Step 2: Convert and quantize**

**Step 3: Build Ollama model**

Run: `ollama create ...`
Expected: model appears in `ollama list`.
