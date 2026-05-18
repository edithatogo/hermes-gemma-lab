#!/bin/bash
# Push adapter and dataset card to Hugging Face Hub.
# Usage: scripts/push_to_hf.sh [adapter_dir]

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ADAPTER_DIR="${1:-$REPO_DIR/experiments/gemma4-e4b/lora_adapter}"
HF_USERNAME="${HF_USERNAME:-edithatogo}"
ADAPTER_REPO="${ADAPTER_REPO:-${HF_USERNAME}/gemma4-e4b-hermes-lora}"
DATASET_REPO="${DATASET_REPO:-${HF_USERNAME}/hermes-training-data}"

command -v hf >/dev/null || {
    echo "Missing 'hf' CLI. Install huggingface_hub or run from the project venv." >&2
    exit 1
}

if [ ! -d "$ADAPTER_DIR" ]; then
    echo "Adapter directory not found: $ADAPTER_DIR" >&2
    exit 1
fi

if [ ! -f "$ADAPTER_DIR/adapters.safetensors" ]; then
    echo "Adapter weights missing: $ADAPTER_DIR/adapters.safetensors" >&2
    echo "Run training before publishing." >&2
    exit 1
fi

echo "=== Hugging Face publish ==="
echo "Adapter: $ADAPTER_REPO"
echo "Dataset: $DATASET_REPO"

hf repo create "$ADAPTER_REPO" --type model --private --exist-ok
TMP_DIR="$(mktemp -d)"
cp -R "$ADAPTER_DIR"/. "$TMP_DIR"/
cp "$REPO_DIR/exports/hf/adapter_card.md" "$TMP_DIR/README.md"
hf upload "$ADAPTER_REPO" "$TMP_DIR" . --repo-type model
rm -rf "$TMP_DIR"

hf repo create "$DATASET_REPO" --type dataset --private --exist-ok
TMP_DIR="$(mktemp -d)"
cp "$REPO_DIR/data/splits/train.jsonl" "$TMP_DIR/"
cp "$REPO_DIR/data/splits/val.jsonl" "$TMP_DIR/"
cp "$REPO_DIR/data/splits/test.jsonl" "$TMP_DIR/"
cp "$REPO_DIR/exports/hf/dataset_card.md" "$TMP_DIR/README.md"
hf upload "$DATASET_REPO" "$TMP_DIR" . --repo-type dataset
rm -rf "$TMP_DIR"

echo "Adapter: https://huggingface.co/$ADAPTER_REPO"
echo "Dataset: https://huggingface.co/datasets/$DATASET_REPO"
