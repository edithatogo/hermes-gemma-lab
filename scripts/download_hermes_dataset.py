#!/usr/bin/env python3
"""
Download the actual Hermes datasets from Nous Research and convert to our training format.
Downloads to portable SSD to save disk space on the main drive.
"""
import json
import os
import sys
from pathlib import Path

# Point HF cache to SSD
os.environ["HF_HOME"] = "/Volumes/PortableSSD/huggingface"
os.environ["HF_HUB_CACHE"] = "/Volumes/PortableSSD/huggingface/hub"
os.environ["XDG_CACHE_HOME"] = "/Volumes/PortableSSD/cache"

from datasets import load_dataset, get_dataset_config_names

REPO_DIR = Path("/Users/doughnut/GitHub/hermes-training/gemma4")
RAW_DIR = REPO_DIR / "data/raw"

def convert_messages_to_hermes(example):
    """Convert any dataset format to our JSONL format with 'messages' key."""
    # Check for 'messages' key (already in chat format)
    if "messages" in example:
        return {"messages": example["messages"]}
    
    # Check for 'conversation' key
    if "conversation" in example:
        return {"messages": example["conversation"]}
    
    # Check for 'text' key (raw text)
    if "text" in example:
        return {"messages": [{"role": "user", "content": example["text"]}, 
                            {"role": "assistant", "content": example.get("response", "...")}]}
    
    # Check for instruction/response format
    if "instruction" in example and "response" in example:
        return {
            "messages": [
                {"role": "user", "content": example["instruction"]},
                {"role": "assistant", "content": example["response"]}
            ]
        }
    
    # Check for system/instruction/response
    if "system" in example and "instruction" in example and "response" in example:
        return {
            "messages": [
                {"role": "system", "content": example["system"]},
                {"role": "user", "content": example["instruction"]},
                {"role": "assistant", "content": example["response"]}
            ]
        }
    
    return None

def download_dataset(name, output_file, max_samples=None):
    """Download a dataset and save as JSONL in our format."""
    print(f"\n=== Downloading {name} ===")
    
    try:
        configs = get_dataset_config_names(name)
        print(f"  Configs: {configs}")
    except Exception:
        configs = ["default"]
    
    written = 0
    with open(output_file, "w") as f:
        for config in configs[:2]:  # Limit to first 2 configs
            try:
                print(f"  Loading config: {config}")
                ds = load_dataset(name, config, split="train", trust_remote_code=True)
                print(f"    Dataset size: {len(ds)} samples")
                
                for i, example in enumerate(ds):
                    if max_samples and i >= max_samples / len(configs):
                        break
                    
                    converted = convert_messages_to_hermes(example)
                    if converted and "messages" in converted:
                        # Add an id
                        converted["id"] = f"{name.replace('/','-')}-{written}"
                        f.write(json.dumps(converted) + "\n")
                        written += 1
                        
            except Exception as e:
                print(f"    Error with config {config}: {e}")
                continue
    
    print(f"  Written {written} conversations to {output_file}")
    return written

def main():
    total = 0
    
    # 1. Hermes-3-Dataset (main Hermes 3 training data)
    total += download_dataset(
        "NousResearch/Hermes-3-Dataset",
        RAW_DIR / "hermes3_dataset.jsonl",
        max_samples=500
    )
    
    # 2. Hermes function calling dataset
    total += download_dataset(
        "NousResearch/hermes-function-calling-v1",
        RAW_DIR / "hermes_function_calling.jsonl",
        max_samples=200
    )
    
    # 3. Optional: a small general instruction dataset for variety
    # Skipping for now - focus on Hermes-specific data
    
    print(f"\n=== Total: {total} conversations across all datasets ===")
    
    # Run the build_dataset pipeline
    print("\n=== Running dataset pipeline ===")
    ret = os.system(f"cd {REPO_DIR} && python3 scripts/build_dataset.py --input-dir data/raw --output-dir data/splits --dedup")
    
    if ret == 0:
        print("\n=== Split sizes ===")
        for split in ["train", "val", "test"]:
            path = REPO_DIR / "data/splits" / f"{split}.jsonl"
            if path.exists():
                lines = len(path.read_text().strip().splitlines())
                print(f"  {split}: {lines} conversations")
    else:
        print(f"Dataset pipeline failed with exit code {ret}")

if __name__ == "__main__":
    main()