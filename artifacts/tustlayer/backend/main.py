import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from backend.modules.fraud_intelligence.router import router as fraud_intelligence_router
from backend.modules.ocr.router import router as ocr_router
from backend.modules.trust_score.router import router as trust_score_router
from backend.modules.scan_pipeline.router import router as scan_pipeline_router
from backend.modules.scan_pipeline.mock_router import router as mock_router
from backend.modules.qr_inspector.router import router as qr_inspector_router
from backend.modules.document_scanner.router import router as document_scanner_router
from backend.modules.whatsapp.router import router as whatsapp_router
from backend.modules.chatbot.router import router as chatbot_router

app = FastAPI(
    title="TrustLayer AI API",
    description="The Trust Verification Layer for Digital Payments",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(fraud_intelligence_router)
app.include_router(ocr_router)
app.include_router(trust_score_router)
app.include_router(scan_pipeline_router)
app.include_router(mock_router)
app.include_router(qr_inspector_router)
app.include_router(document_scanner_router)
from backend.version import GIT_COMMIT, GIT_BRANCH, DEPLOYED_AT

print(f"[TrustLayer AI] Starting server. Branch: {GIT_BRANCH}, Commit: {GIT_COMMIT}, Deployed At: {DEPLOYED_AT}")

app.include_router(whatsapp_router)
app.include_router(chatbot_router)

@app.get("/api/health")
@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "TrustLayer AI", "version": GIT_COMMIT}

@app.get("/api/v1/version")
async def get_version():
    return {
        "git_commit": GIT_COMMIT,
        "deployed_at": DEPLOYED_AT,
        "git_branch": GIT_BRANCH
    }

@app.get("/", response_class=HTMLResponse)
async def homepage():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>TrustLayer AI - Payment Proof Forensics</title>
        <meta name="description" content="Advanced deterministic Trust Score and multi-model AI reasoning engine for verifying digital payment proofs.">
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
        <style>
            :root {
                --bg: #090D16;
                --card-bg: rgba(17, 24, 39, 0.7);
                --card-border: rgba(255, 255, 255, 0.08);
                --primary: #3B82F6;
                --primary-glow: rgba(59, 130, 246, 0.3);
                --accent: #6366F1;
                --accent-glow: rgba(99, 102, 241, 0.3);
                --success: #10B981;
                --success-glow: rgba(16, 185, 129, 0.2);
                --warning: #F59E0B;
                --danger: #EF4444;
                --danger-glow: rgba(239, 68, 68, 0.2);
                --text: #F3F4F6;
                --text-muted: #9CA3AF;
                --text-dim: #6B7280;
            }

            * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Plus Jakarta Sans', sans-serif; }

            body {
                background-color: var(--bg);
                color: var(--text);
                min-height: 100vh;
                overflow-x: hidden;
                position: relative;
            }

            body::before, body::after {
                content: '';
                position: fixed;
                width: 400px;
                height: 400px;
                border-radius: 50%;
                filter: blur(120px);
                z-index: -1;
                opacity: 0.12;
            }
            body::before { background: var(--primary); top: -100px; right: -100px; animation: float 10s ease-in-out infinite alternate; }
            body::after { background: var(--accent); bottom: -100px; left: -100px; animation: float 10s ease-in-out infinite alternate-reverse; }

            @keyframes float { 0% { transform: translate(0, 0) scale(1); } 100% { transform: translate(50px, 50px) scale(1.2); } }
            @keyframes pulse { 0% { opacity: 0.4; } 50% { opacity: 1; } 100% { opacity: 0.4; } }
            @keyframes spin { 100% { transform: rotate(360deg); } }
            @keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
            @keyframes scoreReveal { from { transform: scale(0.5); opacity: 0; } to { transform: scale(1); opacity: 1; } }
            @keyframes shimmer { 0% { background-position: -200% 0; } 100% { background-position: 200% 0; } }

            header {
                max-width: 1200px;
                margin: 0 auto;
                padding: 1.5rem 1.5rem;
                width: 100%;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }

            .logo {
                display: flex;
                align-items: center;
                gap: 0.5rem;
                font-weight: 700;
                font-size: 1.25rem;
                background: linear-gradient(135deg, #FFF 0%, #93C5FD 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }

            .logo-shield {
                width: 24px;
                height: 24px;
                background: var(--primary);
                clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
                box-shadow: 0 0 10px var(--primary-glow);
            }

            .status-badge {
                display: flex;
                align-items: center;
                gap: 0.5rem;
                background: rgba(16, 185, 129, 0.1);
                border: 1px solid rgba(16, 185, 129, 0.2);
                color: var(--success);
                padding: 0.35rem 0.85rem;
                border-radius: 9999px;
                font-size: 0.85rem;
                font-weight: 500;
                box-shadow: 0 0 15px var(--success-glow);
            }

            .status-dot {
                width: 8px;
                height: 8px;
                background-color: var(--success);
                border-radius: 50%;
                animation: pulse 1.5s infinite;
            }

            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 0 1.5rem 3rem 1.5rem;
                width: 100%;
            }

            /* --- TOP SECTION: Upload --- */
            .top-section {
                display: grid;
                grid-template-columns: 1.2fr 1fr;
                gap: 2.5rem;
                align-items: start;
                margin-bottom: 2rem;
            }

            @media (max-width: 968px) {
                .top-section { grid-template-columns: 1fr; }
            }

            .hero-section h1 {
                font-size: 2.75rem;
                font-weight: 800;
                line-height: 1.15;
                margin-bottom: 0.75rem;
                letter-spacing: -0.03em;
                background: linear-gradient(135deg, #FFFFFF 30%, #93C5FD 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }

            .hero-section p {
                color: var(--text-muted);
                font-size: 1rem;
                line-height: 1.6;
                margin-bottom: 1.5rem;
            }

            .stack-info {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 0.75rem;
                margin-bottom: 1.5rem;
            }

            .stack-card {
                background: var(--card-bg);
                border: 1px solid var(--card-border);
                border-radius: 12px;
                padding: 0.75rem;
                text-align: center;
                backdrop-filter: blur(12px);
            }

            .stack-card h4 { font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase; margin-bottom: 0.2rem; letter-spacing: 0.05em; }
            .stack-card p { font-size: 0.85rem; font-weight: 600; color: var(--text); margin: 0; }

            .upload-card {
                background: linear-gradient(135deg, rgba(255,255,255,0.03) 0%, rgba(255,255,255,0.01) 100%);
                border: 1px solid var(--card-border);
                border-radius: 20px;
                padding: 2rem;
                backdrop-filter: blur(20px);
                box-shadow: 0 20px 40px rgba(0,0,0,0.3);
                position: relative;
                overflow: hidden;
            }

            .upload-card::before {
                content: '';
                position: absolute;
                top: 0; left: 0; right: 0;
                height: 2px;
                background: linear-gradient(90deg, transparent, var(--primary), var(--accent), transparent);
            }

            .dropzone {
                border: 2px dashed rgba(255,255,255,0.15);
                border-radius: 12px;
                padding: 2.5rem 1.5rem;
                text-align: center;
                cursor: pointer;
                transition: all 0.3s ease;
                background: rgba(255,255,255,0.01);
            }

            .dropzone:hover, .dropzone.highlight {
                border-color: var(--primary);
                background: rgba(59,130,246,0.05);
                box-shadow: 0 0 15px rgba(59,130,246,0.1);
            }

            .dropzone svg { width: 40px; height: 40px; margin-bottom: 0.75rem; stroke: var(--text-muted); transition: stroke 0.3s ease; }
            .dropzone:hover svg, .dropzone.highlight svg { stroke: var(--primary); }
            .dropzone p { font-size: 0.9rem; color: var(--text-muted); }
            .dropzone span { color: var(--text); font-weight: 600; }

            .file-input { display: none; }

            .btn {
                width: 100%;
                background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
                border: none;
                border-radius: 12px;
                color: white;
                padding: 0.85rem;
                font-weight: 600;
                font-size: 0.95rem;
                cursor: pointer;
                transition: all 0.3s ease;
                margin-top: 1.25rem;
                box-shadow: 0 4px 15px rgba(99,102,241,0.2);
            }

            .btn:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(99,102,241,0.4); }
            .btn:disabled { opacity: 0.5; cursor: not-allowed; transform: none !important; box-shadow: none !important; }

            .preview-container { margin-top: 1rem; display: none; }
            .preview-img { width: 100%; max-height: 180px; object-fit: contain; border-radius: 8px; border: 1px solid var(--card-border); }

            /* --- INITIAL PLACEHOLDER (right column) --- */
            .placeholder-card {
                background: var(--card-bg);
                border: 1px solid var(--card-border);
                border-radius: 20px;
                padding: 3rem 2rem;
                backdrop-filter: blur(12px);
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                text-align: center;
                min-height: 380px;
            }

            .placeholder-card svg { width: 64px; height: 64px; stroke: rgba(255,255,255,0.08); margin-bottom: 1rem; }
            .placeholder-card p { color: var(--text-muted); font-size: 0.95rem; line-height: 1.5; }

            /* --- LOADING STATE --- */
            .loading-card {
                background: var(--card-bg);
                border: 1px solid var(--card-border);
                border-radius: 20px;
                padding: 3rem 2rem;
                backdrop-filter: blur(12px);
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                min-height: 380px;
                gap: 1rem;
            }

            .spinner {
                width: 44px;
                height: 44px;
                border: 3px solid rgba(59,130,246,0.1);
                border-radius: 50%;
                border-top-color: var(--primary);
                animation: spin 1s linear infinite;
            }

            /* --- RESULTS DASHBOARD --- */
            .results-section {
                display: none;
                animation: fadeInUp 0.6s ease;
            }

            .results-section.visible { display: block; }

            .results-header-bar {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 1.5rem;
                padding-bottom: 1rem;
                border-bottom: 1px solid var(--card-border);
            }

            .results-header-bar h2 {
                font-size: 1.3rem;
                font-weight: 700;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }

            .results-header-bar h2 svg { width: 22px; height: 22px; fill: var(--primary); }

            .timing-badge {
                font-size: 0.8rem;
                color: var(--text-muted);
                background: rgba(255,255,255,0.04);
                padding: 0.3rem 0.75rem;
                border-radius: 8px;
                border: 1px solid var(--card-border);
            }

            /* Score Hero */
            .score-hero {
                display: grid;
                grid-template-columns: auto 1fr;
                gap: 2rem;
                align-items: center;
                background: var(--card-bg);
                border: 1px solid var(--card-border);
                border-radius: 20px;
                padding: 2rem;
                margin-bottom: 1.5rem;
                backdrop-filter: blur(12px);
                animation: scoreReveal 0.5s ease;
            }

            .score-ring {
                width: 130px;
                height: 130px;
                position: relative;
                display: flex;
                align-items: center;
                justify-content: center;
            }

            .score-ring svg { width: 100%; height: 100%; transform: rotate(-90deg); }

            .score-ring-bg { fill: none; stroke: rgba(255,255,255,0.06); stroke-width: 8; }
            .score-ring-fill { fill: none; stroke-width: 8; stroke-linecap: round; transition: stroke-dashoffset 1s ease, stroke 0.5s ease; }

            .score-number {
                position: absolute;
                font-size: 2.2rem;
                font-weight: 800;
                line-height: 1;
            }

            .score-label {
                position: absolute;
                bottom: 22px;
                font-size: 0.65rem;
                text-transform: uppercase;
                letter-spacing: 0.1em;
                color: var(--text-muted);
            }

            .score-details h3 {
                font-size: 1.5rem;
                font-weight: 700;
                margin-bottom: 0.5rem;
            }

            .risk-badge {
                display: inline-flex;
                align-items: center;
                gap: 0.4rem;
                padding: 0.3rem 0.8rem;
                border-radius: 8px;
                font-size: 0.8rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                margin-bottom: 0.75rem;
            }

            .risk-HIGH { background: rgba(239,68,68,0.15); color: #F87171; border: 1px solid rgba(239,68,68,0.3); }
            .risk-MEDIUM { background: rgba(245,158,11,0.15); color: #FBBF24; border: 1px solid rgba(245,158,11,0.3); }
            .risk-LOW { background: rgba(16,185,129,0.15); color: #34D399; border: 1px solid rgba(16,185,129,0.3); }

            .fraud-prob {
                font-size: 0.85rem;
                color: var(--text-muted);
            }

            .fraud-prob strong { color: var(--text); }

            /* Grid Cards */
            .dashboard-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 1.25rem;
                margin-bottom: 1.5rem;
            }

            @media (max-width: 768px) {
                .dashboard-grid { grid-template-columns: 1fr; }
                .score-hero { grid-template-columns: 1fr; justify-items: center; text-align: center; }
            }

            .dash-card {
                background: var(--card-bg);
                border: 1px solid var(--card-border);
                border-radius: 16px;
                padding: 1.5rem;
                backdrop-filter: blur(12px);
                animation: fadeInUp 0.5s ease backwards;
            }

            .dash-card:nth-child(1) { animation-delay: 0.1s; }
            .dash-card:nth-child(2) { animation-delay: 0.2s; }
            .dash-card:nth-child(3) { animation-delay: 0.3s; }
            .dash-card:nth-child(4) { animation-delay: 0.4s; }

            .dash-card-title {
                font-size: 0.7rem;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                color: var(--text-muted);
                margin-bottom: 1rem;
                display: flex;
                align-items: center;
                gap: 0.4rem;
                font-weight: 600;
            }

            .dash-card-title svg { width: 14px; height: 14px; }

            /* Extracted Data fields */
            .data-row {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 0.55rem 0;
                border-bottom: 1px solid rgba(255,255,255,0.04);
            }

            .data-row:last-child { border-bottom: none; }

            .data-label {
                font-size: 0.8rem;
                color: var(--text-muted);
            }

            .data-value {
                font-size: 0.85rem;
                font-weight: 600;
                color: var(--text);
                text-align: right;
                max-width: 60%;
                word-break: break-all;
            }

            .data-value.empty {
                color: var(--text-dim);
                font-style: italic;
                font-weight: 400;
            }

            .data-value .valid-icon { color: var(--success); }
            .data-value .invalid-icon { color: var(--danger); }

            /* Bullet lists */
            .reason-list, .action-list {
                list-style: none;
                padding: 0;
            }

            .reason-list li, .action-list li {
                font-size: 0.85rem;
                color: var(--text-muted);
                padding: 0.6rem 0 0.6rem 1.25rem;
                position: relative;
                border-bottom: 1px solid rgba(255,255,255,0.03);
                line-height: 1.5;
            }

            .reason-list li:last-child, .action-list li:last-child { border-bottom: none; }

            .reason-list li::before {
                content: '';
                position: absolute;
                left: 0;
                top: 0.85rem;
                width: 6px;
                height: 6px;
                border-radius: 50%;
                background: var(--primary);
            }

            .action-list li::before {
                content: '';
                position: absolute;
                left: 0;
                top: 0.85rem;
                width: 6px;
                height: 6px;
                border-radius: 2px;
                background: var(--warning);
            }

            /* Full-width cards */
            .full-card {
                background: var(--card-bg);
                border: 1px solid var(--card-border);
                border-radius: 16px;
                padding: 1.5rem;
                backdrop-filter: blur(12px);
                margin-bottom: 1.25rem;
                animation: fadeInUp 0.5s ease backwards;
            }

            .full-card.reasoning-card { animation-delay: 0.3s; }
            .full-card.actions-card { animation-delay: 0.45s; }

            /* Modules bar */
            .modules-bar {
                display: flex;
                gap: 0.5rem;
                flex-wrap: wrap;
                margin-top: 0.5rem;
            }

            .module-chip {
                font-size: 0.7rem;
                padding: 0.25rem 0.6rem;
                border-radius: 6px;
                background: rgba(59,130,246,0.1);
                color: var(--primary);
                border: 1px solid rgba(59,130,246,0.2);
                font-weight: 500;
            }

            /* Raw JSON toggle */
            .raw-toggle {
                display: inline-flex;
                align-items: center;
                gap: 0.4rem;
                background: none;
                border: 1px solid var(--card-border);
                color: var(--text-muted);
                padding: 0.3rem 0.75rem;
                border-radius: 8px;
                font-size: 0.75rem;
                cursor: pointer;
                transition: all 0.2s;
            }

            .raw-toggle:hover { background: rgba(255,255,255,0.05); color: var(--text); }

            .raw-json {
                display: none;
                background: rgba(0,0,0,0.3);
                border: 1px solid var(--card-border);
                border-radius: 8px;
                padding: 1rem;
                font-family: 'Courier New', monospace;
                font-size: 0.75rem;
                color: #34D399;
                overflow-x: auto;
                white-space: pre-wrap;
                margin-top: 1rem;
                max-height: 400px;
                overflow-y: auto;
                line-height: 1.4;
            }

            .raw-json.visible { display: block; }

            footer {
                text-align: center;
                padding: 2rem;
                font-size: 0.85rem;
                color: var(--text-muted);
                border-top: 1px solid var(--card-border);
                margin-top: 2rem;
            }

            footer a { color: var(--primary); text-decoration: none; }
        </style>
        <script>
            window.va = window.va || function () { (window.vaq = window.vaq || []).push(arguments); };
        </script>
        <script defer src="/_vercel/insights/script.js"></script>
    </head>
    <body>
        <header>
            <div class="logo">
                <div class="logo-shield"></div>
                TrustLayer AI
            </div>
            <div class="status-badge">
                <div class="status-dot"></div>
                API Active
            </div>
        </header>

        <div class="container">
            <!-- Upload Section -->
            <div class="top-section">
                <div class="hero-section">
                    <h1>Payment Proof Forensics</h1>
                    <p>An advanced deterministic Trust Score and multi-model AI reasoning engine verifying digital transactions against visual forging, tampering, and double-spend fraud.</p>

                    <div class="stack-info">
                        <div class="stack-card"><h4>OCR Engine</h4><p>Nemotron-VL</p></div>
                        <div class="stack-card"><h4>Reasoning LLM</h4><p>Qwen-3.5-122B</p></div>
                        <div class="stack-card"><h4>Persistence</h4><p>Supabase</p></div>
                    </div>

                    <div class="upload-card">
                        <div class="dropzone" id="dropzone" onclick="document.getElementById('fileInput').click()">
                            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M12 16.5V9.75m0 0l3 3m-3-3l-3 3M6.75 19.5a4.5 4.5 0 01-1.41-8.775 5.25 5.25 0 0110.233-2.33 3 3 0 013.758 3.848A3.752 3.752 0 0118 19.5H6.75z" />
                            </svg>
                            <p><span>Click to upload</span> or drag and drop</p>
                            <p style="font-size: 0.7rem; margin-top: 0.25rem;">Supports PNG, JPG, JPEG</p>
                        </div>
                        <input type="file" id="fileInput" class="file-input" accept="image/*" onchange="handleFileSelect(event)" />

                        <div class="preview-container" id="previewContainer">
                            <img src="" class="preview-img" id="previewImg" alt="Preview" />
                        </div>

                        <button class="btn" id="scanBtn" onclick="runForensicScan()" disabled>Execute Forensic Scan</button>
                    </div>
                </div>

                <!-- Right column: placeholder or loading -->
                <div id="rightPanel">
                    <div class="placeholder-card" id="placeholderCard">
                        <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
                        </svg>
                        <p>Upload a payment screenshot and execute a forensic scan to see the analysis dashboard.</p>
                    </div>
                </div>
            </div>

            <!-- Full-width Results Dashboard (hidden initially) -->
            <div class="results-section" id="resultsSection">
                <div class="results-header-bar">
                    <h2>
                        <svg viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-2 10H7v-2h10v2zm0-4H7V7h10v2zm0 8H7v-2h10v2z"/></svg>
                        Forensic Analysis Report
                    </h2>
                    <div style="display: flex; gap: 0.75rem; align-items: center;">
                        <span class="timing-badge" id="timingBadge"></span>
                        <button class="raw-toggle" onclick="toggleRawJson()">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 18l6-6-6-6M8 6l-6 6 6 6"/></svg>
                            Raw JSON
                        </button>
                    </div>
                </div>

                <!-- Trust Score Hero -->
                <div class="score-hero" id="scoreHero"></div>

                <!-- 2x2 Grid -->
                <div class="dashboard-grid" id="dashGrid"></div>

                <!-- AI Reasoning (full width) -->
                <div class="full-card reasoning-card" id="reasoningCard"></div>

                <!-- Recommended Actions (full width) -->
                <div class="full-card actions-card" id="actionsCard"></div>

                <!-- Modules -->
                <div class="full-card" id="modulesCard" style="animation-delay: 0.55s;"></div>

                <!-- Raw JSON (collapsed) -->
                <div class="raw-json" id="rawJsonBlock"></div>
            </div>
        </div>

        <footer>
            <p>Built for the Hackathon. Powered by <a href="https://build.nvidia.com" target="_blank">NVIDIA NIMs</a> & <a href="https://supabase.com" target="_blank">Supabase</a>.</p>
        </footer>

        <script>
            let selectedFile = null;

            const dropzone = document.getElementById('dropzone');
            const fileInput = document.getElementById('fileInput');

            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                dropzone.addEventListener(eventName, preventDefaults, false);
                document.body.addEventListener(eventName, preventDefaults, false);
            });

            function preventDefaults(e) { e.preventDefault(); e.stopPropagation(); }

            ['dragenter', 'dragover'].forEach(eventName => {
                dropzone.addEventListener(eventName, () => dropzone.classList.add('highlight'), false);
            });

            ['dragleave', 'drop'].forEach(eventName => {
                dropzone.addEventListener(eventName, () => dropzone.classList.remove('highlight'), false);
            });

            dropzone.addEventListener('drop', handleDrop, false);

            function handleDrop(e) {
                const dt = e.dataTransfer;
                const files = dt.files;
                if (files.length) {
                    fileInput.files = files;
                    handleFile(files[0]);
                }
            }

            function handleFileSelect(event) {
                const file = event.target.files[0];
                if (file) handleFile(file);
            }

            function handleFile(file) {
                selectedFile = file;
                const reader = new FileReader();
                reader.onload = function(e) {
                    document.getElementById('previewImg').src = e.target.result;
                    document.getElementById('previewContainer').style.display = 'block';
                    document.getElementById('scanBtn').disabled = false;
                };
                reader.readAsDataURL(file);
            }

            function toggleRawJson() {
                document.getElementById('rawJsonBlock').classList.toggle('visible');
            }

            // Helper functions
            function getRiskColor(risk) {
                if (risk === 'HIGH') return '#EF4444';
                if (risk === 'MEDIUM') return '#F59E0B';
                return '#10B981';
            }

            function getScoreGradient(score) {
                if (score <= 30) return '#EF4444';
                if (score <= 60) return '#F59E0B';
                return '#10B981';
            }

            function cleanReasonText(text) {
                // Remove leading markdown-style bold markers like "**text**:" or "text**:"
                let cleaned = text.replace(/^\\*\\*.*?\\*\\*:?\\s*/g, '');
                // Remove stray ** markers
                cleaned = cleaned.replace(/\\*\\*/g, '');
                // Remove leading "Based on..." preamble lines
                if (cleaned.toLowerCase().startsWith('based on the provided context')) return null;
                if (cleaned.toLowerCase().startsWith('based on the provided')) return null;
                return cleaned.trim();
            }

            function formatFieldName(key) {
                return key.replace(/_/g, ' ').replace(/\\b\\w/g, c => c.toUpperCase());
            }

            function displayVal(val) {
                if (val === null || val === undefined || val === '' || val === 'null') {
                    return '<span class="empty">Not detected</span>';
                }
                return val;
            }

            // --- RENDER DASHBOARD ---
            function renderDashboard(data, elapsedMs) {
                const ts = data.trust_score_data || {};
                const ocr = data.ocr_data || {};
                const fraud = data.fraud_intelligence_data || {};
                const meta = data.metadata || {};

                const score = ts.trust_score || 0;
                const risk = ts.risk_level || 'UNKNOWN';
                const fraudProb = ts.fraud_probability || 0;
                const reasons = (ts.confidence_reasoning || []).map(cleanReasonText).filter(Boolean);
                const actions = (ts.recommended_actions || []).map(cleanReasonText).filter(Boolean);
                const fields = ocr.fields || {};

                const scoreColor = getScoreGradient(score);
                const circumference = 2 * Math.PI * 52;
                const offset = circumference - (score / 100) * circumference;

                // 1. Score Hero
                document.getElementById('scoreHero').innerHTML = `
                    <div class="score-ring">
                        <svg viewBox="0 0 120 120">
                            <circle class="score-ring-bg" cx="60" cy="60" r="52" />
                            <circle class="score-ring-fill" cx="60" cy="60" r="52"
                                stroke="${scoreColor}"
                                stroke-dasharray="${circumference}"
                                stroke-dashoffset="${offset}" />
                        </svg>
                        <div class="score-number" style="color: ${scoreColor}">${score}</div>
                        <div class="score-label">Trust Score</div>
                    </div>
                    <div class="score-details">
                        <h3>Forensic Verdict</h3>
                        <div class="risk-badge risk-${risk}">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
                                ${risk === 'LOW'
                                    ? '<path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>'
                                    : '<path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>'
                                }
                            </svg>
                            ${risk} RISK
                        </div>
                        <p class="fraud-prob">Fraud Probability: <strong>${(fraudProb * 100).toFixed(0)}%</strong></p>
                        <p class="fraud-prob" style="margin-top: 0.25rem;">OCR Confidence: <strong>${((ocr.confidence_score || 0) * 100).toFixed(0)}%</strong></p>
                    </div>
                `;

                // 2. Dashboard Grid
                const fieldLabels = {
                    'payment_amount': 'Payment Amount',
                    'upi_transaction_id': 'UPI Transaction ID',
                    'receiver_name': 'Receiver Name',
                    'timestamp': 'Timestamp',
                    'payment_app_name': 'Payment App'
                };

                let fieldsHtml = '';
                for (const [key, label] of Object.entries(fieldLabels)) {
                    const val = fields[key];
                    fieldsHtml += `<div class="data-row"><span class="data-label">${label}</span><span class="data-value ${(!val || val === 'null') ? 'empty' : ''}">${displayVal(val)}</span></div>`;
                }

                let fraudHtml = `
                    <div class="data-row"><span class="data-label">Fingerprint Match</span><span class="data-value">${fraud.fingerprint_match ? '<span class="invalid-icon">&#9888; Matched</span>' : '<span class="valid-icon">&#10003; No Match</span>'}</span></div>
                    <div class="data-row"><span class="data-label">Match Confidence</span><span class="data-value">${((fraud.match_confidence || 0) * 100).toFixed(0)}%</span></div>
                    <div class="data-row"><span class="data-label">Fraud Type</span><span class="data-value ${!fraud.fraud_type ? 'empty' : ''}">${displayVal(fraud.fraud_type)}</span></div>
                    <div class="data-row"><span class="data-label">Known Matches</span><span class="data-value">${fraud.match_count || 0}</span></div>
                `;

                document.getElementById('dashGrid').innerHTML = `
                    <div class="dash-card">
                        <div class="dash-card-title">
                            <svg fill="none" viewBox="0 0 24 24" stroke="var(--primary)" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m5.231 13.481L15 17.25m-4.5-15H5.625c-.621 0-1.125.504-1.125 1.125v16.5c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" /></svg>
                            Extracted Data (OCR)
                        </div>
                        ${fieldsHtml}
                    </div>
                    <div class="dash-card">
                        <div class="dash-card-title">
                            <svg fill="none" viewBox="0 0 24 24" stroke="var(--danger)" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126z" /></svg>
                            Fraud Intelligence
                        </div>
                        ${fraudHtml}
                    </div>
                `;

                // 3. AI Reasoning
                if (reasons.length > 0) {
                    document.getElementById('reasoningCard').innerHTML = `
                        <div class="dash-card-title">
                            <svg fill="none" viewBox="0 0 24 24" stroke="var(--accent)" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" /></svg>
                            AI Confidence Reasoning
                        </div>
                        <ul class="reason-list">${reasons.map(r => '<li>' + r + '</li>').join('')}</ul>
                    `;
                    document.getElementById('reasoningCard').style.display = 'block';
                } else {
                    document.getElementById('reasoningCard').style.display = 'none';
                }

                // 4. Recommended Actions
                if (actions.length > 0) {
                    document.getElementById('actionsCard').innerHTML = `
                        <div class="dash-card-title">
                            <svg fill="none" viewBox="0 0 24 24" stroke="var(--warning)" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 18v-5.25m0 0a6.01 6.01 0 001.5-.189m-1.5.189a6.01 6.01 0 01-1.5-.189m3.75 7.478a12.06 12.06 0 01-4.5 0m3.75 2.383a14.406 14.406 0 01-3 0M14.25 18v-.192c0-.983.658-1.823 1.508-2.316a7.5 7.5 0 10-7.517 0c.85.493 1.509 1.333 1.509 2.316V18" /></svg>
                            Recommended Actions
                        </div>
                        <ul class="action-list">${actions.map(a => '<li>' + a + '</li>').join('')}</ul>
                    `;
                    document.getElementById('actionsCard').style.display = 'block';
                } else {
                    document.getElementById('actionsCard').style.display = 'none';
                }

                // 5. Modules & Timing
                const modules = meta.modules_executed || [];
                document.getElementById('modulesCard').innerHTML = `
                    <div class="dash-card-title">
                        <svg fill="none" viewBox="0 0 24 24" stroke="var(--success)" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" /></svg>
                        Pipeline Modules Executed
                    </div>
                    <div class="modules-bar">${modules.map(m => '<span class="module-chip">' + m + '</span>').join('')}</div>
                    <p style="margin-top: 0.75rem; font-size: 0.8rem; color: var(--text-muted);">Backend processing: <strong style="color: var(--text)">${meta.execution_time_ms || 0}ms</strong> &bull; Total round-trip: <strong style="color: var(--text)">${elapsedMs}ms</strong></p>
                `;

                // Show section
                document.getElementById('resultsSection').classList.add('visible');
                document.getElementById('resultsSection').scrollIntoView({ behavior: 'smooth', block: 'start' });
            }

            // --- MAIN SCAN FUNCTION ---
            async function runForensicScan() {
                if (!selectedFile) return;

                const btn = document.getElementById('scanBtn');
                const rightPanel = document.getElementById('rightPanel');
                const timingBadge = document.getElementById('timingBadge');
                const resultsSection = document.getElementById('resultsSection');

                btn.disabled = true;
                btn.innerText = "Analyzing...";
                resultsSection.classList.remove('visible');

                // Show loading in right panel
                rightPanel.innerHTML = `
                    <div class="loading-card">
                        <div class="spinner"></div>
                        <p style="color: var(--text-muted); font-size: 0.9rem; text-align: center;">Running Multimodal OCR<br>&amp; Fraud Verification...</p>
                    </div>
                `;

                const formData = new FormData();
                formData.append('file', selectedFile);

                try {
                    const start = performance.now();
                    const response = await fetch('/api/v1/scan/execute', {
                        method: 'POST',
                        body: formData
                    });

                    if (!response.ok) {
                        throw new Error('Server Error ' + response.status + ': ' + (await response.text()));
                    }

                    const data = await response.json();
                    const elapsed = Math.round(performance.now() - start);

                    // Restore placeholder in right panel
                    rightPanel.innerHTML = `
                        <div class="placeholder-card">
                            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5" style="stroke: var(--success);">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
                            </svg>
                            <p style="color: var(--success); font-weight: 600;">Scan Complete</p>
                            <p style="margin-top: 0.25rem;">Results displayed below &#x2193;</p>
                        </div>
                    `;

                    timingBadge.innerText = 'Completed in ' + elapsed + 'ms';

                    // Store raw JSON
                    document.getElementById('rawJsonBlock').textContent = JSON.stringify(data, null, 2);

                    // Render the visual dashboard
                    renderDashboard(data, elapsed);

                } catch (error) {
                    rightPanel.innerHTML = `
                        <div class="placeholder-card" style="border-color: rgba(239,68,68,0.3);">
                            <svg fill="none" viewBox="0 0 24 24" stroke="var(--danger)" stroke-width="1.5" style="width: 48px; height: 48px;">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
                            </svg>
                            <p style="color: var(--danger); font-weight: 600;">${error.message}</p>
                        </div>
                    `;
                    timingBadge.innerText = 'Scan Failed';
                } finally {
                    btn.disabled = false;
                    btn.innerText = "Execute Forensic Scan";
                }
            }
        </script>
    </body>
    </html>
    """

