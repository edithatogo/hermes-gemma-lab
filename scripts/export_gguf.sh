#!/bin/bash
# Convert trained adapter + base model to GGUF for Ollama
# Usage: scripts/export_gguf.sh [adapter_dir] [output_model_name]

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ADAPTER_DIR="${1:-$REPO_DIR/experiments/gemma4-e4b/lora_adapter}"
MODEL_NAME="${2:-gemma4-hermes}"
OUTPUT_DIR="$REPO_DIR/exports/ollama/$MODEL_NAME"

echo "=== Exporting to Ollama ==="
echo "Adapter: $ADAPTER_DIR"
echo "Model name: $MODEL_NAME"
echo "Output: $OUTPUT_DIR"
echo ""

# Ensure llama.cpp is available
LLAMA_CPP_DIR="$REPO_DIR/../llama.cpp"
if [ ! -d "$LLAMA_CPP_DIR" ]; then
    echo "llama.cpp not found at $LLAMA_CPP_DIR"
    echo "Cloning..."
    git clone --depth 1 https://github.com/ggerganov/llama.cpp.git "$LLAMA_CPP_DIR"
    cd "$LLAMA_CPP_DIR"
    make -j4
fi

# Create output dir
mkdir -p "$OUTPUT_DIR"

# Step 1: Merge LoRA adapter into base model (if using HuggingFace format)
echo "Step 1: Merging LoRA adapter..."
# For MLX: merge the adapter into a safetensors model first using the mlx_lm fuse command
# mlx_lm.fuse expects the base model and adapter

# Step 2: Convert to GGUF
echo "Step 2: Converting to GGUF..."
if command -v python3 &>/dev/null; then
    # Use llama.cpp's convert script
    HF_MODEL_DIR="$OUTPUT_DIR/hf-merged"
    if [ -d "$HF_MODEL_DIR" ]; then
        python3 "$LLAMA_CPP_DIR/convert_hf_to_gguf.py" "$HF_MODEL_DIR" \
            --outfile "$OUTPUT_DIR/$MODEL_NAME-f16.gguf" \
            --outtype f16
    fi
fi

# Step 3: Quantize (optional)
echo "Step 3: Quantizing..."
if command -v "$LLAMA_CPP_DIR/quantize" &>/dev/null; then
    "$LLAMA_CPP_DIR/quantize" "$OUTPUT_DIR/$MODEL_NAME-f16.gguf" \
        "$OUTPUT_DIR/$MODEL_NAME-q4_k_m.gguf" q4_k_m
fi

# Step 4: Create Ollama model
echo "Step 4: Creating Ollama model..."
OLLAMA_MODEL_DIR="$OUTPUT_DIR/ollama-model"
mkdir -p "$OLLAMA_MODEL_DIR"
# Copy the quantized model (or f16 if no quantization)
if [ -f "$OUTPUT_DIR/$MODEL_NAME-q4_k_m.gguf" ]; then
    cp "$OUTPUT_DIR/$MODEL_NAME-q4_k_m.gguf" "$OLLAMA_MODEL_DIR/model.gguf"
elif [ -f "$OUTPUT_DIR/$MODEL_NAME-f16.gguf" ]; then
    cp "$OUTPUT_DIR/$MODEL_NAME-f16.gguf" "$OLLAMA_MODEL_DIR/model.gguf"
fi

# Use the Modelfile from the repo
cp "$REPO_DIR/modelfiles/Gemma4-Hermes.Modelfile" "$OLLAMA_MODEL_DIR/Modelfile"
cd "$OLLAMA_MODEL_DIR"
ollama create "$MODEL_NAME" -f Modelfile

echo ""
echo "=== Export complete ==="
echo "Model '${MODEL_NAME}' should now be available in Ollama."
echo "Run: ollama list | grep ${MODEL_NAME}"