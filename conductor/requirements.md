# Requirements — Gemma/Qwen/Hermes Track

## Must Have

| ID | Requirement | Verification |
|---|---|---|
| M1 | Qwen3 4B model download is SSD-backed and reliable | cached under `/Volumes/PortableSSD/huggingface` |
| M2 | Qwen3 4B smoke config trains to adapter save | smoke run passes |
| M3 | Hermes 4 baseline role documented | config and docs present |
| M4 | Base vs adapter evaluation | comparison report exists |
| M5 | Health >= 9.5 before completion | health checkpoint in plan |
| M6 | Gemma 4 26B/31B no-thinking configs use empty thought channel data | validator passes |

## Should Have

| ID | Requirement | Priority |
|---|---|---|
| S1 | Hermes 4 teacher/evaluator workflow | High |
| S2 | Qwen3.6/Gemma4 MoE runtime proof | Medium |
| S3 | Coding/tool-call benchmark subset | High |
| S4 | Gemma 4 prompt-format materialization stays separate from shared Qwen data | High |

## Won't Have

| ID | Requirement | Reason |
|---|---|
| W1 | Local fine-tune of Qwen3.6/Gemma4 MoE by default | runtime/teacher first |
