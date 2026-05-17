#!/bin/bash
export HF_HOME=/Volumes/PortableSSD/huggingface
export HF_HUB_CACHE=/Volumes/PortableSSD/huggingface/hub
mkdir -p "$HF_HUB_CACHE"
cd /Users/doughnut/GitHub/hermes-training/gemma4
exec /usr/local/bin/python3 scripts/train.py --config scripts/train_config.yaml