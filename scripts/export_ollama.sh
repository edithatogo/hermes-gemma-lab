#!/bin/bash
# Merge MLX LoRA adapter with base model, convert to GGUF, push to Ollama.
# Usage: scripts/export_ollama.sh [adapter_dir] [model_name]

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ADAPTER="${1:-$REPO_DIR/experiments/gemma4-e4b/lora_adapter}"
MODEL_NAME="${2:-gemma4-hermes}"
if [ -z "${HERMES_EXPORT_ROOT:-}" ]; then
    if [ -d /Volumes/PortableSSD ]; then
        HERMES_EXPORT_ROOT="/Volumes/PortableSSD/hermes-exports"
    else
        HERMES_EXPORT_ROOT="$REPO_DIR/exports"
    fi
fi
WORK_DIR="${WORK_DIR:-$HERMES_EXPORT_ROOT/ollama/$MODEL_NAME}"
MERGE_DIR="$WORK_DIR/merged"
OLLAMA_DIR="$WORK_DIR/ollama-pkg"

echo "=== Exporting to Ollama ==="
echo "Adapter:   $ADAPTER"
echo "Model:     $MODEL_NAME"
echo "Work dir:  $WORK_DIR"
echo ""

mkdir -p "$MERGE_DIR" "$OLLAMA_DIR"

# Step 1: Merge LoRA adapter using mlx_lm.fuse
echo "Step 1: Merging LoRA adapter..."
if command -v mlx_lm.fuse &>/dev/null; then
    mlx_lm.fuse \
        --adapter-path "$ADAPTER" \
        --save-path "$MERGE_DIR"
elif python3 -c "import mlx_lm.fuse" 2>/dev/null; then
    /usr/local/bin/python3 -m mlx_lm.fuse \
        --adapter-path "$ADAPTER" \
        --save-path "$MERGE_DIR"
else
    echo "  mlx_lm.fuse not found. Attempting Python import..."
    /usr/local/bin/python3 -c "
import sys, json
from pathlib import Path
adapter = Path('$ADAPTER')
merge_dir = Path('$MERGE_DIR')
# Load adapter config to find base model
cfg_path = adapter / 'adapter_config.json'
if cfg_path.exists():
    cfg = json.loads(cfg_path.read_text())
    print(f'  Base model from config: {cfg.get(\"model\", \"unknown\")}')
if not list(merge_dir.glob('*')):
    print('  No merge tool available — adapter weights preserved separately.')
    print(f'  Manual merge command: mlx_lm.fuse --adapter-path {adapter} --save-path {merge_dir}')
    merge_dir.mkdir(parents=True, exist_ok=True)
    (merge_dir / 'USE_ADAPTER').write_text(str(adapter))
"
fi

# Step 2: Install llama.cpp if needed
LLAMA_CPP="${LLAMA_CPP_DIR:-${HERMES_STORAGE_ROOT:-$REPO_DIR/..}/llama.cpp}"
if [ ! -f "$LLAMA_CPP/convert_hf_to_gguf.py" ]; then
    echo "Step 2: Cloning llama.cpp..."
    git clone --depth 1 https://github.com/ggerganov/llama.cpp.git "$LLAMA_CPP"
fi

# Step 3: Convert merged model to GGUF
echo "Step 3: Converting to GGUF..."
GGUF_FILE="$WORK_DIR/$MODEL_NAME-f16.gguf"
if [ -f "$MERGE_DIR/config.json" ]; then
    /usr/local/bin/python3 "$LLAMA_CPP/convert_hf_to_gguf.py" "$MERGE_DIR" \
        --outfile "$GGUF_FILE" \
        --outtype f16
else
    echo "  No merged model found at $MERGE_DIR. Creating placeholder model info."
    cat > "$OLLAMA_DIR/Modelfile" << MODFILE
# $MODEL_NAME — Hermes-style fine-tune
# Base model: google/gemma-4-E4B-it
FROM google/gemma-4-E4B-it

SYSTEM """You are Hermes, an AI assistant fine-tuned from Gemma 4 E4B.
You are helpful, harmless, and honest. You provide clear, accurate answers.
When using tools, follow the exact function schema provided."""

TEMPLATE """{{ if .System }}<|start_header_id|>system<|end_header_id|>

{{ .System }}<|eot_id|>{{ end }}{{ range .Messages }}{{ if eq .Role "user" }}<|start_header_id|>user<|end_header_id|>

{{ .Content }}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

{{ else if eq .Role "assistant" }}{{ .Content }}<|eot_id|>{{ end }}{{ end }}"""

PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER stop "<|eot_id|>"
PARAMETER stop "<|start_header_id|>"
PARAMETER num_ctx 8192
MODFILE
    echo "  Modelfile created. Build with: ollama create $MODEL_NAME -f $OLLAMA_DIR/Modelfile"
    exit 0
fi

# Step 4: Quantize
echo "Step 4: Quantizing..."
Q4_FILE="$WORK_DIR/$MODEL_NAME-q4_k_m.gguf"
if [ -f "$GGUF_FILE" ] && [ -f "$LLAMA_CPP/quantize" ]; then
    "$LLAMA_CPP/quantize" "$GGUF_FILE" "$Q4_FILE" q4_k_m
    MODEL_FILE="$Q4_FILE"
elif [ -f "$GGUF_FILE" ]; then
    echo "  quantize binary not found, building llama.cpp..."
    cd "$LLAMA_CPP"
    make -j4 quantize 2>/dev/null || make -j4 2>/dev/null || true
    cd "$REPO_DIR"
    if [ -f "$LLAMA_CPP/quantize" ]; then
        "$LLAMA_CPP/quantize" "$GGUF_FILE" "$Q4_FILE" q4_k_m
        MODEL_FILE="$Q4_FILE"
    else
        echo "  Using f16 (no quantization available)"
        MODEL_FILE="$GGUF_FILE"
    fi
else
    echo "  No GGUF file to quantize."
    exit 0
fi

# Step 5: Package for Ollama
echo "Step 5: Creating Ollama package..."
cp "$MODEL_FILE" "$OLLAMA_DIR/model.gguf"
cp "$REPO_DIR/modelfiles/Gemma4-Hermes.Modelfile" "$OLLAMA_DIR/Modelfile"

# Step 6: Create Ollama model
echo "Step 6: Creating Ollama model..."
cd "$OLLAMA_DIR"
ollama create "$MODEL_NAME" -f Modelfile
cd "$REPO_DIR"

echo ""
echo "=== Complete ==="
echo "Ollama model: $MODEL_NAME"
ollama list | grep "$MODEL_NAME"
echo ""
echo "Run: ollama run $MODEL_NAME"
echo "Or in Hermes: switch to model $MODEL_NAME"
