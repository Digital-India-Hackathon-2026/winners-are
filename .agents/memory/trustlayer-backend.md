---
name: TrustLayer AI backend
description: Architecture and operational notes for the TrustLayer AI FastAPI backend in artifacts/tustlayer.
---

## Key layout
- Backend root: `artifacts/tustlayer/backend/`
- Entry: `backend/main.py` (FastAPI, version 2.0.0)
- ASGI bridge: `artifacts/tustlayer/api/index.py` imports `backend.main.app`
- Requirements: `artifacts/tustlayer/api/requirements.txt` (NOT inside backend/)
- Python version: 3.12 (installed as Replit module)

## Runtime
- Workflow "artifacts/tustlayer: Python Backend": `cd artifacts/tustlayer && python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload`
- Next.js dev proxies `/api/*` → `http://127.0.0.1:8000` (see `next.config.ts`)

## Model IDs (all in core/config.py — never hardcode elsewhere)
- OCR: nvidia/nemotron-ocr-v2
- Visual: nvidia/nemotron-nano-12b-v2-vl (NemotronNano12BVLProvider, 4 tasks)
- Deepfake: hive/deepfake-image-detection
- Reasoning: qwen/qwen3.5-397b-a17b
- Fallback: microsoft/phi-4-multimodal-instruct

## Trust Score formula (additive, 0→100)
UTR+25, VPA+20, branding+15, EXIF+15, deepfake+10, timestamp+8, amount+7, no-replay+5.
Hard caps: foreign-currency→10, UTR-wrong→15, fraud-template→5, EXIF-edited→40, deepfake>0.7→25, VPA-nonexistent→20.

## Architecture decisions
- App forensics uses dual-validation: deterministic color fingerprint (65%) + NemotronNano12BVL branding_auth (35%)
- main.py has a large inline HTML template with JS regexes — the `\*` in JS regex strings inside Python strings causes SyntaxWarning (harmless). Fixed by using `\\*` in the Python string.
- BOM (U+FEFF) was removed from main.py — always write it UTF-8 without BOM.

**Why:** The project was cloned from GitHub with Windows-style BOM. Future edits must save files without BOM.
