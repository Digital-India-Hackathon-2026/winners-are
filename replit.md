# TrustLayer AI

India's UPI payment forensics platform — a 9-layer AI pipeline that assigns a 0–100 Trust Score to any UPI payment screenshot and flags fakes, deepfakes, and fraud templates.

## Run & Operate

- `cd artifacts/tustlayer && python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload` — run Python backend (FastAPI)
- `pnpm --filter @workspace/tustlayer run dev` — run Next.js frontend (port 20033, proxies /api → port 8000)
- Workflows: **"artifacts/tustlayer: Python Backend"** (port 8000) + **"artifacts/tustlayer: web"** (port 20033)
- Required env vars: `NVIDIA_API_KEY`, `SUPABASE_URL`, `SUPABASE_KEY`, `RAZORPAY_KEY_ID`, `RAZORPAY_KEY_SECRET`, `GOOGLE_SAFE_BROWSING_KEY`, `VIRUSTOTAL_API_KEY`

## Stack

- **Frontend**: Next.js 15 + React 19 + Tailwind CSS v4 + Framer Motion + GSAP
- **Backend**: FastAPI (Python 3.12) + uvicorn
- **AI**: NVIDIA NIM (Nemotron OCR v2, Nemotron Nano 12B VL, Hive Deepfake, Qwen 3.5 397B, Phi-4)
- **DB**: Supabase (PostgreSQL)
- **Validation**: Razorpay VPA lookup, Google Safe Browsing, VirusTotal
- Python packages: Pillow, numpy, PyMuPDF, opencv-python-headless, imagehash, pytesseract, httpx, tenacity

## Where things live

- `artifacts/tustlayer/backend/` — FastAPI app root
  - `main.py` — FastAPI app + router registrations
  - `core/config.py` — all model IDs + env var settings (source of truth for model names)
  - `integrations/nvidia_client.py` — all NVIDIA NIM clients (v2)
  - `modules/scan_pipeline/service.py` — 9-layer pipeline orchestrator
  - `modules/scan_pipeline/aggregator.py` — maps all module outputs → TrustScoreInput
  - `modules/trust_score/engine.py` — additive scoring formula (source of truth)
  - `modules/trust_score/schemas.py` — TrustScoreInput / TrustScoreResult (12 fields)
  - `modules/scan_pipeline/schemas.py` — FinalScanResponse v2
  - `modules/vpa_validator/` — Razorpay live VPA lookup
  - `modules/deepfake/` — Hive deepfake detection wrapper
  - `modules/qr_inspector/` — OpenCV QR decode + UPI URI parse (POST /api/v1/qr/inspect)
  - `modules/document_scanner/` — LSB stego + PDF analysis (POST /api/v1/document/scan)
- `artifacts/tustlayer/api/index.py` — ASGI bridge (imports backend.main.app)
- `artifacts/tustlayer/api/requirements.txt` — Python package list

## Architecture decisions

- **Additive Trust Score (0→100)**: Points are earned per verified signal (UTR+25, VPA+20, branding+15, EXIF+15, deepfake+10, timestamp+8, amount+7, no-replay+5). Hard caps override: foreign-currency→10, UTR-wrong→15, fraud-template→5, EXIF-edited→40, deepfake>0.7→25, VPA-nonexistent→20.
- **Dual-validation in app_forensics**: Deterministic color-fingerprint (65%) blended with NemotronNano12BVL branding_auth (35%) so AI catches edge cases that pixel math misses.
- **9-layer pipeline**: Layers 1+2 (OCR + fraud pHash) run parallel; layers 5+6 (deepfake + VPA) run parallel; aggregation → score → AI reasoning is sequential.
- **No model names in code**: All model IDs live in `core/config.py` only. Clients read `settings.*_MODEL`.
- **Graceful degradation**: Every AI call is wrapped in try/except; the pipeline completes even if individual layers fail.

## Product

- Upload any UPI payment screenshot → get a 0–100 Trust Score with breakdown (UTR validity, VPA existence, app branding, EXIF integrity, deepfake probability)
- QR code inspection: decode UPI QR → validate VPA + amount + merchant
- Document scanning: detect PDF injection, LSB steganography, and hidden payloads
- AI reasoning narrative in Hindi-compatible English explaining why the score was assigned

## User preferences

_Populate as you build — explicit user instructions worth remembering across sessions._

## Gotchas

- Python backend runs on port 8000; Next.js proxies `/api/*` to it in dev (see `next.config.ts`)
- `requirements.txt` lives at `artifacts/tustlayer/api/requirements.txt` (not inside `backend/`)
- BOM (`\xef\xbb\xbf`) was removed from `main.py` — write it with UTF-8 (no BOM) only
- `pnpm run dev` at workspace root has no script — always use `--filter` or the workflow
- Tesseract system binary is needed for `pytesseract`; install via `installSystemDependencies(["tesseract"])`

## Pointers

- See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details
- NVIDIA NIM API key goes in `NVIDIA_API_KEY` env var (same key for all NIM models)
