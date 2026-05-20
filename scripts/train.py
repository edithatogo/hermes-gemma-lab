#!/usr/bin/env python3
"""
MLX LoRA fine-tuning for Apple Silicon (M1 Max).

Usage:
  python3 scripts/train.py --config scripts/train_config.yaml
  python3 scripts/train.py --config scripts/train_config.yaml --dry-run
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

import mlx.core as mx
import mlx.optimizers as optim
import mlx.nn as nn
import yaml

import mlx_lm
from mlx_lm import load
from mlx_lm.tuner import (
    linear_to_lora_layers,
    train,
)
from mlx_lm.tuner.datasets import load_dataset
from mlx_lm.tuner.trainer import TrainingArgs

def count_parameters(params):
    total = 0
    if isinstance(params, dict):
        for value in params.values():
            total += count_parameters(value)
    elif isinstance(params, (list, tuple)):
        for value in params:
            total += count_parameters(value)
    elif hasattr(params, "size"):
        total += params.size
    return total

class ProcessedDataset:
    def __init__(self, dataset):
        self.dataset = dataset

    def __getitem__(self, idx):
        return self.dataset.process(self.dataset[idx])

    def __len__(self):
        return len(self.dataset)

def ensure_processed_dataset(dataset):
    if hasattr(dataset, "process"):
        return ProcessedDataset(dataset)
    return dataset

def main():
    parser = argparse.ArgumentParser(description="Fine-tune with LoRA using MLX.")
    parser.add_argument("--config", type=Path, required=True, help="YAML config path.")
    parser.add_argument("--dry-run", action="store_true", help="Check config and exit.")
    args = parser.parse_args()

    with args.config.open("r") as f:
        cfg = yaml.safe_load(f)

    model_name = cfg.get("model")
    adapter_dir = Path(cfg.get("adapter_path", "experiments/gemma4-e4b/lora_adapter"))
    data_path = Path(cfg.get("data", "data/splits"))
    lora_rank = int(cfg.get("lora_rank", 16))
    lora_scale = float(cfg.get("lora_scale", 20.0))
    lora_dropout = float(cfg.get("lora_dropout", 0.0))
    lora_layers = int(cfg.get("lora_layers", 16))
    batch_size = int(cfg.get("batch_size", 4))
    iters = int(cfg.get("iters", 100))
    val_batches = int(cfg.get("val_batches", 25))
    steps_per_report = int(cfg.get("steps_per_report", 10))
    steps_per_eval = int(cfg.get("steps_per_eval", 200))
    steps_per_save = int(cfg.get("steps_per_save", 100))
    max_seq_length = int(cfg.get("max_seq_length", 2048))
    learning_rate = float(cfg.get("learning_rate", 1e-4))
    grad_checkpoint = cfg.get("grad_checkpoint", False)
    grad_accumulation_steps = int(cfg.get("grad_accumulation_steps", 1))
    seed = int(cfg.get("seed", 42))

    mx.random.seed(seed)

    if args.dry_run:
        print("=== Dry run — config summary ===")
        for k, v in sorted(cfg.items()):
            print(f"  {k}: {v}")
        print(f"\nAdapter path: {adapter_dir.resolve()}")
        print(f"Data path: {data_path.resolve()}")
        print("Dry run complete.")
        return 0

    # Step 1: Load model and tokenizer
    print(f"\nLoading model: {model_name}")
    model, tokenizer = load(model_name)
    print(f"  Model loaded. Freezing weights...")
    model.freeze()
    model.train(True)

    # Step 2: Apply LoRA to last N layers
    print(f"  Applying LoRA (rank={lora_rank}, layers={lora_layers})...")
    lora_config = {
        "rank": lora_rank,
        "scale": lora_scale,
        "dropout": lora_dropout,
    }
    linear_to_lora_layers(model, lora_layers, lora_config)
    p_num = count_parameters(model.trainable_parameters())
    print(f"  Trainable parameters: {p_num:,}")

    # Step 3: Load dataset
    # We need an args-like namespace for load_dataset
    class Args:
        pass
    ds_args = Args()
    ds_args.data = str(data_path)  # path to directory with train.jsonl, valid.jsonl, test.jsonl
    ds_args.train = True
    ds_args.test = True
    ds_args.hf_dataset = False
    # Optional dataset config attrs
    ds_args.chat_feature = "messages"
    ds_args.mask_prompt = False

    print(f"\nLoading dataset from: {data_path}")
    train_set, valid_set, _ = load_dataset(ds_args, tokenizer)
    train_set = ensure_processed_dataset(train_set)
    valid_set = ensure_processed_dataset(valid_set)
    print(f"  Train samples: {len(train_set)}")
    print(f"  Valid samples: {len(valid_set)}")

    # Step 4: Create optimizer and training args
    optimizer = optim.AdamW(learning_rate=learning_rate)
    train_args = TrainingArgs(
        batch_size=batch_size,
        iters=iters,
        val_batches=val_batches,
        steps_per_report=steps_per_report,
        steps_per_eval=steps_per_eval,
        steps_per_save=steps_per_save,
        max_seq_length=max_seq_length,
        adapter_file=str(adapter_dir / "adapters.safetensors"),
        grad_checkpoint=grad_checkpoint,
        grad_accumulation_steps=grad_accumulation_steps,
    )

    # Step 5: Train
    adapter_dir.mkdir(parents=True, exist_ok=True)
    print(f"\nStarting training for {iters} iterations...")
    print(f"  Batch size: {batch_size}")
    print(f"  Learning rate: {learning_rate}")
    print(f"  Max seq length: {max_seq_length}")
    t0 = time.time()
    train(
        model=model,
        optimizer=optimizer,
        train_dataset=train_set,
        val_dataset=valid_set,
        args=train_args,
    )
    elapsed = time.time() - t0
    print(f"\nTraining complete in {elapsed:.1f}s")

    # Step 6: Save adapter metadata
    with open(adapter_dir / "adapter_config.json", "w") as f:
        json.dump({
            "model": model_name,
            "fine_tune_type": "lora",
            "num_layers": lora_layers,
            "lora_parameters": {
                "rank": lora_rank,
                "scale": lora_scale,
                "dropout": lora_dropout,
            },
            "lora_rank": lora_rank,
            "lora_scale": lora_scale,
            "lora_dropout": lora_dropout,
            "lora_layers": lora_layers,
            "max_seq_length": max_seq_length,
            "learning_rate": learning_rate,
            "batch_size": batch_size,
            "iters": iters,
            "seed": seed,
        }, f, indent=2)
    print(f"Adapter saved to: {adapter_dir}")
    print(f"  Adapter weights: {adapter_dir / 'adapters.safetensors'}")
    print(f"  Config: {adapter_dir / 'adapter_config.json'}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
