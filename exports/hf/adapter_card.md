---
license: apache-2.0
library_name: mlx
tags:
- hermes
- gemma-4
- lora
- fine-tune
- instruction-tuning
base_model: google/gemma-4-E4B-it
datasets:
- NousResearch/Hermes-3-Dataset
- NousResearch/hermes-function-calling-v1
language:
- en
pipeline_tag: text-generation
---

# Gemma 4 E4B Hermes — LoRA Adapter

A LoRA fine-tune of [google/gemma-4-E4B-it](https://huggingface.co/google/gemma-4-E4B-it)
trained on Hermes-style instruction data.

## Training Details

- **Base model:** google/gemma-4-E4B-it (4B active params, MoE)
- **Method:** LoRA (rank 16)
- **Framework:** Apple MLX
- **Hardware:** MacBook Pro M1 Max (32GB)
- **Dataset:** Hermes-3-Dataset + hermes-function-calling-v1
- **License:** Apache 2.0

## Usage with MLX

```python
from mlx_lm import load, generate

model, tokenizer = load(
    "google/gemma-4-E4B-it",
    adapter_path="path/to/adapter"
)

response = generate(model, tokenizer, "Hello!", verbose=True)
```

## Usage with Ollama

```bash
ollama run gemma4-hermes
```

## Contents

- `adapters.safetensors` — LoRA adapter weights
- `adapter_config.json` — Training hyperparameters
- This model card

## Notes

- This is an adapter-only release. You need the base model to use it.
- Trained on Apple Silicon (M1 Max, 32GB RAM).
- The training dataset is available as [`edithatogo/hermes-training-data`](https://huggingface.co/datasets/edithatogo/hermes-training-data).
