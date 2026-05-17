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
- fine-tuning
size_categories:
- 1K<n<10K
---

# Hermes-Style Training Data

A collection of Hermes-style conversations for supervised fine-tuning,
derived from the [NousResearch/Hermes-3-Dataset](https://huggingface.co/datasets/NousResearch/Hermes-3-Dataset)
and [NousResearch/hermes-function-calling-v1](https://huggingface.co/datasets/NousResearch/hermes-function-calling-v1).

## Format

Each example is a JSON object with:

```json
{
  "id": "unique-id",
  "messages": [
    {"role": "system", "content": "You are Hermes..."},
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ]
}
```

## Preprocessing

- Deduplicated by conversation hash
- Filtered to conversations with 2–100 turns
- Split into train (80%), val (10%), test (10%)

## Files

- `train.jsonl` — Training split
- `val.jsonl` — Validation split
- `test.jsonl` — Test split

## Usage

```python
from datasets import load_dataset

ds = load_dataset("json", data_files="train.jsonl")
```

## License

Apache 2.0
