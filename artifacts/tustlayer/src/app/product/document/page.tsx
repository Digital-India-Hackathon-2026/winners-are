"use client";

import { ChangeEvent, DragEvent, useRef, useState } from "react";
import Link from "next/link";

type UrlAnalysis = {
  url: string;
  risk: "SAFE" | "MEDIUM" | "HIGH";
  reasons: string[];
};

type DocResult = {
  success: boolean;
  document_type: string;
  page_count: number;
  steganography_suspected: boolean;
  steganography_signals: string[];
  urls_found: string[];
  suspicious_urls: string[];
  url_risk_level: string;
  url_analysis: UrlAnalysis[];
  embedded_files_found: boolean;
  embedded_file_count: number;
  pdf_javascript_found: boolean;
  pdf_auto_action_found: boolean;
  risk_level: string;
  risk_signals: string[];
  explanation: string;
  error?: string;
} | null;

function RiskLevel({ level }: { level: string }) {
  const map: Record<string, { bg: string; color: string }> = {
    LOW:     { bg: "rgba(49,245,139,0.1)",  color: "#31f58b" },
    MEDIUM:  { bg: "rgba(255,178,46,0.1)",  color: "#ffb22e" },
    HIGH:    { bg: "rgba(255,77,46,0.12)",  color: "#ff6450" },
    UNKNOWN: { bg: "rgba(255,248,238,0.05)", color: "var(--foreground-dim)" },
  };
  const s = map[level?.toUpperCase()] ?? map.UNKNOWN;
  return (
    <span style={{
      display: "inline-flex", alignItems: "center", gap: "6px",
      padding: "5px 14px", borderRadius: "999px", fontSize: "0.74rem",
      fontWeight: 800, letterSpacing: "0.1em", textTransform: "uppercase",
      background: s.bg, color: s.color, border: `1px solid ${s.color}44`,
    }}>
      <span style={{ width: "6px", height: "6px", borderRadius: "50%", background: s.color, boxShadow: `0 0 6px ${s.color}` }} />
      {level} RISK
    </span>
  );
}

function UrlVerdictCard({ analysis }: { analysis: UrlAnalysis }) {
  const riskConfig = {
    SAFE:   { icon: "✓", label: "Safe",       color: "#31f58b", bg: "rgba(49,245,139,0.05)",  border: "rgba(49,245,139,0.15)" },
    MEDIUM: { icon: "⚠", label: "Suspicious", color: "#ffb22e", bg: "rgba(255,178,46,0.06)",  border: "rgba(255,178,46,0.2)" },
    HIGH:   { icon: "✕", label: "Dangerous",  color: "#ff4d2e", bg: "rgba(255,77,46,0.07)",   border: "rgba(255,77,46,0.22)" },
  };
  const cfg = riskConfig[analysis.risk] ?? riskConfig.MEDIUM;

  return (
    <div style={{
      padding: "10px 12px", borderRadius: "10px", fontSize: "0.72rem",
      background: cfg.bg, border: `1px solid ${cfg.border}`,
      display: "flex", flexDirection: "column", gap: "6px",
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
        <span style={{
          width: "22px", height: "22px", borderRadius: "50%", display: "flex",
          alignItems: "center", justifyContent: "center", fontSize: "0.68rem",
          fontWeight: 900, background: `${cfg.color}22`, color: cfg.color,
          border: `1.5px solid ${cfg.color}55`, flexShrink: 0,
        }}>{cfg.icon}</span>
        <span style={{
          fontFamily: "var(--font-mono)", wordBreak: "break-all",
          color: analysis.risk === "SAFE" ? "var(--foreground-muted)" : cfg.color,
          flex: 1, lineHeight: 1.4,
        }}>{analysis.url}</span>
        <span style={{
          padding: "2px 8px", borderRadius: "6px", fontSize: "0.6rem",
          fontWeight: 800, letterSpacing: "0.08em", textTransform: "uppercase",
          background: `${cfg.color}18`, color: cfg.color, flexShrink: 0,
          border: `1px solid ${cfg.color}33`,
        }}>{cfg.label}</span>
      </div>
      {analysis.reasons && analysis.reasons.length > 0 && (
        <div style={{
          paddingLeft: "30px", display: "flex", flexDirection: "column", gap: "3px",
        }}>
          {analysis.reasons.map((reason, i) => (
            <span key={i} style={{
              fontSize: "0.65rem", color: analysis.risk === "SAFE" ? "var(--foreground-dim)" : `${cfg.color}cc`,
              lineHeight: 1.5,
            }}>
              {analysis.risk !== "SAFE" ? "→ " : "• "}{reason}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

export default function DocumentScannerPage() {
  const [file,       setFile]       = useState<File | null>(null);
  const [preview,    setPreview]    = useState<string | null>(null);
  const [isScanning, setIsScanning] = useState(false);
  const [result,     setResult]     = useState<DocResult>(null);
  const [error,      setError]      = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  const handleFile = (f: File) => {
    setFile(f);
    setResult(null);
    setError(null);
    if (f.type.startsWith("image/")) {
      const reader = new FileReader();
      reader.onload = (e) => { if (typeof e.target?.result === "string") setPreview(e.target.result); };
      reader.readAsDataURL(f);
    } else {
      setPreview(null);
    }
  };

  const handleDrop  = (e: DragEvent<HTMLDivElement>)    => { e.preventDefault(); const f = e.dataTransfer.files?.[0]; if (f) handleFile(f); };
  const handleInput = (e: ChangeEvent<HTMLInputElement>) => { const f = e.target.files?.[0]; if (f) handleFile(f); e.target.value = ""; };

  const handleScan = async () => {
    if (!file) return;
    setIsScanning(true);
    setError(null);
    try {
      const formData = new FormData();
      formData.append("file", file, file.name);
      const res = await fetch("/api/v1/document/scan", { method: "POST", body: formData });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setResult(await res.json());
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Scan failed");
    } finally {
      setIsScanning(false);
    }
  };

  const docIcon = file?.type === "application/pdf" ? "📄" : "🖼️";

  // Derive URL analysis — use backend data or fallback to simple list
  const urlAnalysis: UrlAnalysis[] = result?.url_analysis ?? 
    (result?.urls_found ?? []).map(url => ({
      url,
      risk: (result?.suspicious_urls ?? []).includes(url) ? "HIGH" as const : "SAFE" as const,
      reasons: (result?.suspicious_urls ?? []).includes(url) ? ["Matched suspicious pattern"] : ["No issues detected"],
    }));

  return (
    <div className="product-page">
      <div className="tool-switcher">
        <Link href="/product" className="tool-tab">Screenshot Scan</Link>
        <Link href="/product/qr" className="tool-tab">QR Inspector</Link>
        <Link href="/product/document" className="tool-tab tool-tab--active">Document Scanner</Link>
      </div>

      <div className="tool-layout">
        {/* ── Left: Upload ── */}
        <div className="product-panel">
          <div className="product-panel-header">
            <span className="dot" /> Document Upload
          </div>
          <div className="product-panel-body">
            <div
              className="upload-dropzone"
              onDrop={handleDrop}
              onDragOver={(e) => e.preventDefault()}
              onClick={() => fileRef.current?.click()}
            >
              <div className="upload-dropzone-icon">📄</div>
              <p><strong>Click to upload</strong> or drag and drop</p>
              <div className="format-hint">PNG · JPG · JPEG · PDF</div>
              <input
                ref={fileRef} type="file"
                accept="image/*,application/pdf"
                onChange={handleInput}
                style={{ display: "none" }}
              />
            </div>

            {file && (
              <div className="doc-file-badge">
                <span className="doc-file-icon">{docIcon}</span>
                <div>
                  <p className="doc-file-name">{file.name}</p>
                  <p className="doc-file-size">{(file.size / 1024).toFixed(1)} KB</p>
                </div>
              </div>
            )}

            {preview && (
              <div className="upload-preview">
                <img src={preview} alt="Document preview" />
              </div>
            )}

            <button className="scan-btn" onClick={handleScan} disabled={!file || isScanning}>
              {isScanning ? "Scanning..." : "Scan Document"}
            </button>

            {error && (
              <p style={{ marginTop: "12px", fontSize: "0.78rem", color: "var(--ember)", textAlign: "center" }}>
                {error}
              </p>
            )}

            <div className="tool-info-card">
              <p className="tool-info-title">What this checks</p>
              <ul className="tool-info-list">
                <li>LSB steganography detection (hidden data in pixels)</li>
                <li>PDF embedded file scanning</li>
                <li>JavaScript injection in PDFs</li>
                <li>Auto-action / launch triggers</li>
                <li>URL extraction &amp; phishing verification</li>
                <li>Brand impersonation &amp; suspicious TLD detection</li>
                <li>Pixel-level anomaly analysis</li>
              </ul>
            </div>
          </div>
        </div>

        {/* ── Right: Results ── */}
        <div className="product-panel tool-results-panel">
          <div className="product-panel-header">
            <span className="dot" style={{
              background: result
                ? result.risk_level === "LOW" ? "#31f58b"
                : result.risk_level === "HIGH" ? "#ff4d2e"
                : "#ffb22e"
                : "var(--signal)"
            }} />
            Scan Results
          </div>

          {isScanning && (
            <div style={{ display: "flex", flexDirection: "column", alignItems: "center", padding: "40px 20px", gap: "24px" }}>
              <div className="radar-scanner" style={{ width: "100px", height: "100px" }}>
                <div className="radar-sweep" />
                <div className="radar-ping" />
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: "10px", width: "100%" }}>
                {["Analysing pixel entropy for steganographic signatures...",
                  "Parsing document structure and embedded objects...",
                  "Verifying URLs against phishing and brand impersonation databases..."].map((msg, i) => (
                  <div key={i} className="scanning-step active" style={{ opacity: 1 }}>
                    <span className="scanning-spinner" />
                    <div className="step-content"><p style={{ margin: 0 }}>{msg}</p></div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {!isScanning && !result && (
            <div style={{ display: "grid", placeItems: "center", padding: "60px 20px", textAlign: "center", color: "var(--foreground-dim)" }}>
              <div style={{ fontSize: "2.5rem", marginBottom: "12px", opacity: 0.3 }}>📄</div>
              <p style={{ margin: 0, fontSize: "0.88rem" }}>Upload a payment document or PDF to scan for hidden threats.</p>
            </div>
          )}

          {!isScanning && result && (
            <div style={{ overflowY: "auto", maxHeight: "calc(100svh - 200px)" }}>
              {/* Risk Level */}
              <div className="result-block" style={{ textAlign: "center", padding: "20px" }}>
                <RiskLevel level={result.risk_level} />
                {result.explanation && (
                  <p style={{ marginTop: "12px", fontSize: "0.82rem", color: "var(--foreground-muted)", lineHeight: 1.55 }}>
                    {result.explanation}
                  </p>
                )}
              </div>

              {/* Document Info */}
              <div className="result-block">
                <h4 className="result-block-title">Document Info</h4>
                {[
                  ["Type",       result.document_type.toUpperCase()],
                  ["Pages",      result.page_count > 0 ? String(result.page_count) : "N/A"],
                  ["URL Risk",   result.url_risk_level],
                ] .map(([label, value]) => (
                  <div className="result-row" key={label}>
                    <span className="label">{label}</span>
                    <span className="value" style={{
                      color: value === "HIGH" ? "#ff4d2e" : value === "MEDIUM" ? "#ffb22e" : undefined
                    }}>{value}</span>
                  </div>
                ))}
              </div>

              {/* Threat Detection */}
              <div className="result-block">
                <h4 className="result-block-title">Threat Detection</h4>
                <div className="flags-grid">
                  {[
                    { label: "Steganography",      active: result.steganography_suspected,   danger: true  },
                    { label: "Embedded Files",      active: result.embedded_files_found,      danger: true  },
                    { label: "PDF JavaScript",      active: result.pdf_javascript_found,      danger: true  },
                    { label: "PDF Auto-Action",     active: result.pdf_auto_action_found,     danger: true  },
                    { label: "Suspicious URLs",     active: result.suspicious_urls.length > 0, warn: true   },
                  ].map(({ label, active, danger, warn }) => {
                    if (!active) return (
                      <div key={label} className="flag-chip flag-chip--ok">
                        <span className="flag-chip-dot" />{label}
                      </div>
                    );
                    const color = danger ? "#ff4d2e" : "#ffb22e";
                    return (
                      <div key={label} className="flag-chip flag-chip--active" style={{ borderColor: `${color}44`, background: `${color}0d`, color }}>
                        <span className="flag-chip-dot" style={{ background: color, boxShadow: `0 0 6px ${color}` }} />
                        {label}
                      </div>
                    );
                  })}
                </div>

                {result.embedded_files_found && (
                  <div className="result-row" style={{ marginTop: "10px" }}>
                    <span className="label">Embedded Count</span>
                    <span className="value danger">{result.embedded_file_count}</span>
                  </div>
                )}
              </div>

              {/* Steganography Signals */}
              {result.steganography_signals.length > 0 && (
                <div className="result-block">
                  <h4 className="result-block-title">Steganography Signals</h4>
                  <ul style={{ padding: 0, margin: "8px 0 0 0", listStyle: "none" }}>
                    {result.steganography_signals.map((sig, i) => (
                      <li key={i} className="result-reason">{sig}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* URL Verification — Per-URL verdicts */}
              {urlAnalysis.length > 0 && (
                <div className="result-block">
                  <h4 className="result-block-title">URL Verification ({urlAnalysis.length})</h4>
                  <div style={{ display: "flex", flexDirection: "column", gap: "8px", marginTop: "10px" }}>
                    {urlAnalysis.slice(0, 10).map((analysis, i) => (
                      <UrlVerdictCard key={i} analysis={analysis} />
                    ))}
                    {urlAnalysis.length > 10 && (
                      <p style={{ fontSize: "0.72rem", color: "var(--foreground-dim)", margin: "4px 0 0", textAlign: "center" }}>
                        +{urlAnalysis.length - 10} more URLs not shown
                      </p>
                    )}
                  </div>
                </div>
              )}

              {/* Risk Signals */}
              {result.risk_signals.length > 0 && (
                <div className="result-block">
                  <h4 className="result-block-title">Risk Signals</h4>
                  <ul style={{ padding: 0, margin: "8px 0 0 0", listStyle: "none" }}>
                    {result.risk_signals.map((sig, i) => (
                      <li key={i} className="result-reason">{sig}</li>
                    ))}
                  </ul>
                </div>
              )}

              {result.error && (
                <div className="result-block">
                  <p style={{ fontSize: "0.78rem", color: "var(--ember)", fontStyle: "italic" }}>Error: {result.error}</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

