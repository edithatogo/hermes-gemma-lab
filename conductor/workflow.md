# Gemma/Qwen/Hermes Track Workflow

1. Source `../scripts/env.sh` before downloads, training, or evals.
2. Prefetch or authenticate Hugging Face downloads before Qwen smoke training.
3. Run smoke training before longer training.
4. Treat Hermes 4, Qwen3.6, and Gemma4 MoE as runtime/teacher targets until benchmarked.
5. Keep artifacts ignored unless promoted.
