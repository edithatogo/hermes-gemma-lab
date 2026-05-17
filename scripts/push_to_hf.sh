#!/bin/bash
# Push adapter and model card to Hugging Face Hub
# Usage: scripts/push_to_hf.sh [adapter_dir]

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ADAPTER_DIR="${1:-$REPO_DIR/experiments/gemma4-e4b/lora_adapter}"
HF_USERNAME="${HF_USERNAME:-edithatogo}"
ADAPTER_REPO="${HF_USERNAME}/gemma4-e4b-hermes-lora"
DATASET_REPO="${HF_USERNAME}/hermes-training-data"

echo "=== Pushing to Hugging Face Hub ==="
echo "Adapter repo: $ADAPTER_REPO"
echo ""

# Check for HF token
if [ -z "${HF_TOKEN:-}" ] && [ ! -f ~/.cache/huggingface/token ]; then
    echo "Warning: No HF_TOKEN set. Login required."
    huggingface-cli login --token "$HF_TOKEN" 2>/dev/null || true
fi

# Step 1: Create/push adapter repo
echo "Step 1: Pushing LoRA adapter..."
if huggingface-cli repo list 2>/dev/null | grep -q "$ADAPTER_REPO"; then
    echo "  Repo exists, pushing to existing repo."
else
    huggingface-cli create "$ADAPTER_REPO" --type model --private 2>/dev/null || true
fi

# Copy adapter to a temp dir with model card
TMP_DIR=$(mktemp -d)
cp -r "$ADAPTER_DIR"/* "$TMP_DIR/"
cp "$REPO_DIR/exports/hf/adapter_card.md" "$TMP_DIR/README.md" 2>/dev/null || true

cd "$TMP_DIR"
huggingface-cli upload "$ADAPTER_REPO" . --private
rm -rf "$TMP_DIR"

# Step 2: Push dataset
echo "Step 2: Pushing dataset..."
if huggingface-cli repo list 2>/dev/null | grep -q "$DATASET_REPO"; then
    echo "  Dataset repo exists."
else
    huggingface-cli create "$DATASET_REPO" --type dataset --private 2>/dev/null || true
fi

TMP_DIR=$(mktemp -d)
cp "$REPO_DIR/data/splits/train.jsonl" "$TMP_DIR/"
cp "$REPO_DIR/data/splits/val.jsonl" "$TMP_DIR/" 2>/dev/null || true
cp "$REPO_DIR/data/splits/test.jsonl" "$TMP_DIR/"
cp "$REPO_DIR/exports/hf/dataset_card.md" "$TMP_DIR/README.md" 2>/dev/null || cat > "$TMP_DIR/README.md" << 'CARD'
---
license: apache-2.0
task_categories:
- text-generation
language:
- en
tags:
- hermes
- instruction-tuning
- tool-use
---
# Hermes-Style Training Data

Cleaned and deduplicated Hermes-style conversations for fine-tuning.
CARD

cd "$TMP_DIR"
huggingface-cli upload "$DATASET_REPO" . --private 2>/dev/null || true
rm -rf "$TMP_DIR"

echo ""
echo "=== HF Push Complete ==="
echo "Adapter: https://huggingface.co/$ADAPTER_REPO"
echo "Dataset: https://huggingface.co/$DATASET_REPO"