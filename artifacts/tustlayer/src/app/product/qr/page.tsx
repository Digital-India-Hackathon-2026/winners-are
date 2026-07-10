"use client";

import { ChangeEvent, DragEvent, useRef, useState } from "react";
import Link from "next/link";

type UPIPayload = {
  raw_uri: string;
  pa?: string;
  pn?: string;
  am?: string;
  tn?: string;
  tr?: string;
  mc?: string;
  cu?: string;
  mode?: string;
  sign?: string;
};

type QRResult = {
  success: boolean;
  qr_found: boolean;
  qr_count: number;
  is_upi_qr: boolean;
  upi_payload?: UPIPayload;
  foreign_currency: boolean;
  amount_hardcoded: boolean;
  unknown_vpa_handle: boolean;
  vpa_handle_valid: boolean;
  multiple_qr_codes: boolean;
  suspicious_uri: boolean;
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

export default function QRInspectorPage() {
  const [image,      setImage]      = useState<string | null>(null);
  const [fileName,   setFileName]   = useState<string>("");
  const [isScanning, setIsScanning] = useState(false);
  const [result,     setResult]     = useState<QRResult>(null);
  const [error,      setError]      = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  const handleFile = (file: File) => {
    if (!file.type.startsWith("image/")) return;
    setFileName(file.name);
    setResult(null);
    setError(null);
    const reader = new FileReader();
    reader.onload = (e) => {
      if (typeof e.target?.result === "string") setImage(e.target.result);
    };
    reader.readAsDataURL(file);
  };

  const handleDrop  = (e: DragEvent<HTMLDivElement>)    => { e.preventDefault(); const f = e.dataTransfer.files?.[0]; if (f) handleFile(f); };
  const handleInput = (e: ChangeEvent<HTMLInputElement>) => { const f = e.target.files?.[0]; if (f) handleFile(f); e.target.value = ""; };

  const handleScan = async () => {
    if (!image) return;
    setIsScanning(true);
    setError(null);
    try {
      const blob     = await (await fetch(image)).blob();
      const formData = new FormData();
      formData.append("file", blob, fileName || "qr.png");
      const res = await fetch("/api/v1/qr/inspect", { method: "POST", body: formData });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setResult(await res.json());
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Scan failed");
    } finally {
      setIsScanning(false);
    }
  };

  return (
    <div className="product-page">
      <div className="tool-switcher">
        <Link href="/product" className="tool-tab">Screenshot Scan</Link>
        <Link href="/product/qr" className="tool-tab tool-tab--active">QR Inspector</Link>
        <Link href="/product/document" className="tool-tab">Document Scanner</Link>
      </div>

      <div className="tool-layout">
        {/* ── Left: Upload ── */}
        <div className="product-panel">
          <div className="product-panel-header">
            <span className="dot" /> QR Code Upload
          </div>
          <div className="product-panel-body">
            <div
              className="upload-dropzone"
              onDrop={handleDrop}
              onDragOver={(e) => e.preventDefault()}
              onClick={() => fileRef.current?.click()}
            >
              <div className="upload-dropzone-icon">⬡</div>
              <p><strong>Click to upload</strong> or drag and drop</p>
              <div className="format-hint">PNG · JPG · JPEG containing a QR code</div>
              <input ref={fileRef} type="file" accept="image/*" onChange={handleInput} style={{ display: "none" }} />
            </div>

            {image && (
              <div className="upload-preview">
                <img src={image} alt="QR code" />
              </div>
            )}

            <button className="scan-btn" onClick={handleScan} disabled={!image || isScanning}>
              {isScanning ? "Inspecting..." : "Inspect QR Code"}
            </button>

            {error && (
              <p style={{ marginTop: "12px", fontSize: "0.78rem", color: "var(--ember)", textAlign: "center" }}>
                {error}
              </p>
            )}

            <div className="tool-info-card">
              <p className="tool-info-title">What this checks</p>
              <ul className="tool-info-list">
                <li>Decodes UPI QR URI via OpenCV</li>
                <li>Validates VPA handle format</li>
                <li>Flags hardcoded amounts</li>
                <li>Detects foreign currency codes</li>
                <li>Checks for suspicious URI patterns</li>
                <li>Warns on multiple embedded QR codes</li>
              </ul>
            </div>
          </div>
        </div>

        {/* ── Right: Results ── */}
        <div className="product-panel tool-results-panel">
          <div className="product-panel-header">
            <span className="dot" style={{ background: result ? (result.risk_level === "LOW" ? "#31f58b" : result.risk_level === "HIGH" ? "#ff4d2e" : "#ffb22e") : "var(--signal)" }} />
            Inspection Results
          </div>

          {isScanning && (
            <div style={{ display: "grid", placeItems: "center", padding: "60px 20px", gap: "20px" }}>
              <div className="radar-scanner" style={{ width: "100px", height: "100px" }}>
                <div className="radar-sweep" />
                <div className="radar-ping" />
              </div>
              <p style={{ color: "var(--foreground-muted)", fontSize: "0.84rem", margin: 0 }}>
                Decoding QR code &amp; validating UPI URI...
              </p>
            </div>
          )}

          {!isScanning && !result && (
            <div style={{ display: "grid", placeItems: "center", padding: "60px 20px", textAlign: "center", color: "var(--foreground-dim)" }}>
              <div style={{ fontSize: "2.5rem", marginBottom: "12px", opacity: 0.3 }}>⬡</div>
              <p style={{ margin: 0, fontSize: "0.88rem" }}>Upload an image containing a UPI QR code to inspect it.</p>
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

              {/* QR Status */}
              <div className="result-block">
                <h4 className="result-block-title">QR Detection</h4>
                {(
                  [
                    ["QR Found",  result.qr_found  ? "✓ Yes" : "✕ No", result.qr_found  ? "success" : "danger"],
                    ["QR Count",  String(result.qr_count),               result.multiple_qr_codes ? "warn" : ""],
                    ["Is UPI QR", result.is_upi_qr ? "✓ Yes" : "✕ No", result.is_upi_qr ? "success" : "danger"],
                  ] satisfies [string, string, string][]
                ).map(([label, value, cls]) => (
                  <div className="result-row" key={label}>
                    <span className="label">{label}</span>
                    <span className={`value ${cls}`}>{value}</span>
                  </div>
                ))}
              </div>

              {/* UPI Payload */}
              {result.upi_payload && (
                <div className="result-block">
                  <h4 className="result-block-title">UPI URI Fields</h4>
                  {(
                    [
                      ["Payee VPA (pa)",      result.upi_payload.pa   || "—"],
                      ["Payee Name (pn)",     result.upi_payload.pn   || "—"],
                      ["Amount (am)",         result.upi_payload.am   ? `₹${result.upi_payload.am}` : "—"],
                      ["Currency (cu)",       result.upi_payload.cu   || "INR"],
                      ["Txn Note (tn)",       result.upi_payload.tn   || "—"],
                      ["Txn Ref (tr)",        result.upi_payload.tr   || "—"],
                      ["Merchant Code (mc)",  result.upi_payload.mc   || "—"],
                      ["Mode",                result.upi_payload.mode || "—"],
                      ["Signed",              result.upi_payload.sign ? "✓ Yes" : "✕ No"],
                    ] satisfies [string, string][]
                  ).map(([label, value]) => (
                    <div className="result-row" key={label}>
                      <span className="label" style={{ fontFamily: "var(--font-mono)", fontSize: "0.7rem" }}>{label}</span>
                      <span className="value" style={{ fontFamily: label.includes("VPA") ? "var(--font-mono)" : undefined, fontSize: "0.74rem" }}>
                        {value}
                      </span>
                    </div>
                  ))}
                  {result.upi_payload.raw_uri && (
                    <details style={{ marginTop: "10px" }}>
                      <summary style={{ cursor: "pointer", fontSize: "0.72rem", color: "var(--foreground-dim)", fontWeight: 700, letterSpacing: "0.06em", textTransform: "uppercase" }}>
                        Raw URI
                      </summary>
                      <p style={{ marginTop: "6px", fontSize: "0.68rem", fontFamily: "var(--font-mono)", color: "var(--cyan)", wordBreak: "break-all", background: "rgba(52,230,255,0.04)", border: "1px solid rgba(52,230,255,0.12)", borderRadius: "8px", padding: "8px" }}>
                        {result.upi_payload.raw_uri}
                      </p>
                    </details>
                  )}
                </div>
              )}

              {/* Risk Flags */}
              <div className="result-block">
                <h4 className="result-block-title">Risk Flags</h4>
                <div className="flags-grid">
                  {[
                    { label: "Foreign Currency", active: result.foreign_currency,     danger: true  },
                    { label: "Hardcoded Amount",  active: result.amount_hardcoded,     warn:  true  },
                    { label: "Unknown VPA Handle",active: result.unknown_vpa_handle,   danger: true  },
                    { label: "Multiple QR Codes", active: result.multiple_qr_codes,   warn:  true  },
                    { label: "Suspicious URI",    active: result.suspicious_uri,       danger: true  },
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
                  <div className={`flag-chip ${result.vpa_handle_valid ? "flag-chip--ok" : "flag-chip--active"}`}
                    style={!result.vpa_handle_valid ? { borderColor: "#ff4d2e44", background: "#ff4d2e0d", color: "#ff4d2e" } : {}}>
                    <span className="flag-chip-dot" style={!result.vpa_handle_valid ? { background: "#ff4d2e" } : {}} />
                    VPA Handle {result.vpa_handle_valid ? "Valid" : "Invalid"}
                  </div>
                </div>
              </div>

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
