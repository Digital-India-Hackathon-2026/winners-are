"use client";

import { useState, useEffect } from "react";

export type DeepfakeScanResult = {
  deepfake_probability: number;
  is_deepfake: boolean;
  manipulation_type: string;
  signals: string[];
  error?: string;
};

export type VPAValidationResult = {
  upi_id: string | null;
  vpa_handle_valid: boolean;
  vpa_exists: boolean | null;
  registered_name: string | null;
  name_match: boolean | null;
  error?: string;
};

export type DeterministicFlags = {
  foreign_currency_detected: boolean;
  utr_format_violation: boolean;
  utr_dummy_pattern: boolean;
  exif_editing_software: boolean;
  exif_software_name: string | null;
  timestamp_late_night: boolean;
  replay_detected: boolean;
  replay_count: number;
  score_breakdown: Record<string, number> | null;
  triggered_caps: string[] | null;
};

export type ScanResponse = {
  success: boolean;
  metadata: { execution_time_ms: number; modules_executed: string[] };
  trust_score_data: {
    trust_score: number;
    risk_level: string;
    fraud_probability: number;
    confidence_reasoning: string[];
    recommended_actions: string[];
    verdict?: string;
    extraction_quality_label?: string;
  };
  ocr_data: {
    fields: {
      payment_amount: string | null;
      upi_transaction_id: string | null;
      receiver_name: string | null;
      timestamp: string | null;
      payment_app_name: string | null;
    };
    confidence_score: number;
    used_fallback: boolean;
    image_quality_score?: number;
    ocr_pass_count?: number;
  };
  fraud_intelligence_data: {
    fingerprint_match: boolean;
    match_confidence: number;
    match_count: number;
    fraud_type: string | null;
  };
  app_forensics?: {
    detected_app: string;
    logo_match: boolean;
    layout_consistency: string;
    authenticity_score: number;
    suspected_clone: boolean;
    explanation: string;
  };
  deepfake_data?: DeepfakeScanResult;
  vpa_validation_data?: VPAValidationResult;
  deterministic_flags?: DeterministicFlags;
  anonymous_session_id?: string;
  remaining_scans?: number;
} | null;

type ResultsPanelProps = {
  results: any;
  isScanning?: boolean;
};

const SCORE_SIGNALS: { key: string; label: string; max: number; color: string }[] = [
  { key: "utr",       label: "UTR / Transaction ID",  max: 25, color: "#34e6ff" },
  { key: "vpa",       label: "VPA Live Lookup",        max: 20, color: "#34e6ff" },
  { key: "branding",  label: "App Branding Match",     max: 15, color: "#dbff4a" },
  { key: "exif",      label: "EXIF Integrity",         max: 15, color: "#dbff4a" },
  { key: "deepfake",  label: "Deepfake Detection",     max: 10, color: "#dbff4a" },
  { key: "timestamp", label: "Timestamp Validity",     max:  8, color: "#ffb22e" },
  { key: "amount",    label: "Amount Consistency",     max:  7, color: "#ffb22e" },
  { key: "no_replay", label: "No Replay Detected",     max:  5, color: "#31f58b" },
];

function ScoreBreakdown({ breakdown, caps }: { breakdown: Record<string, number>; caps?: string[] | null }) {
  return (
    <div className="score-breakdown">
      {SCORE_SIGNALS.map(({ key, label, max, color }) => {
        const earned = breakdown[key] ?? null;
        if (earned === null) return null;
        const pct = Math.max(0, Math.min(100, (earned / max) * 100));
        const isCapped = caps?.some(c => c.toLowerCase().includes(key.toLowerCase()));
        return (
          <div className="score-bar-row" key={key}>
            <div className="score-bar-meta">
              <span className="score-bar-label">{label}</span>
              <span className="score-bar-pts" style={{ color: isCapped ? "#ff4d2e" : color }}>
                {isCapped ? "CAPPED" : `+${earned}`}
                <span className="score-bar-max">/{max}</span>
              </span>
            </div>
            <div className="score-bar-track">
              <div
                className="score-bar-fill"
                style={{
                  width: `${pct}%`,
                  background: isCapped
                    ? "linear-gradient(90deg, #ff4d2e, #ff7752)"
                    : `linear-gradient(90deg, ${color}aa, ${color})`,
                  boxShadow: isCapped ? `0 0 8px rgba(255,77,46,0.4)` : `0 0 8px ${color}44`,
                }}
              />
            </div>
          </div>
        );
      })}
      {caps && caps.length > 0 && (
        <div className="score-caps-row">
          <span className="score-caps-label">Hard caps triggered:</span>
          <span className="score-caps-list">{caps.join(" · ")}</span>
        </div>
      )}
    </div>
  );
}

function RiskBadge({ level }: { level: string }) {
  const map: Record<string, { bg: string; color: string }> = {
    LOW:     { bg: "rgba(49,245,139,0.1)",  color: "#31f58b" },
    MEDIUM:  { bg: "rgba(255,178,46,0.1)",  color: "#ffb22e" },
    HIGH:    { bg: "rgba(255,77,46,0.12)",  color: "#ff6450" },
    UNKNOWN: { bg: "rgba(255,248,238,0.05)", color: "var(--foreground-dim)" },
  };
  const s = map[level?.toUpperCase()] ?? map.UNKNOWN;
  return (
    <span style={{
      display: "inline-block",
      padding: "3px 10px",
      borderRadius: "999px",
      fontSize: "0.68rem",
      fontWeight: 800,
      letterSpacing: "0.08em",
      textTransform: "uppercase",
      background: s.bg,
      color: s.color,
      border: `1px solid ${s.color}33`,
    }}>
      {level}
    </span>
  );
}

function getVerdictStyle(verdict: string): { color: string; icon: string } {
  const v = verdict.toLowerCase();
  if (v.includes("verified"))              return { color: "#31f58b", icon: "✓" };
  if (v.includes("likely authentic"))      return { color: "#31f58b", icon: "◉" };
  if (v.includes("partial verification")) return { color: "#ffb22e", icon: "◎" };
  if (v.includes("low confidence") || v.includes("verification recommended")) return { color: "#ffb22e", icon: "⚠" };
  if (v.includes("needs review"))         return { color: "#ff9466", icon: "⚡" };
  if (v.includes("fake"))                 return { color: "#ff6450", icon: "✕" };
  return { color: "#8899aa", icon: "?" };
}

function getQualityBadgeStyle(label: string): { bg: string; text: string } {
  const l = label.toLowerCase();
  if (l.includes("high quality")) return { bg: "rgba(49,245,139,0.12)",  text: "#31f58b" };
  if (l.includes("good"))         return { bg: "rgba(49,245,139,0.08)",  text: "#7bf5a8" };
  if (l.includes("partial"))      return { bg: "rgba(255,178,46,0.10)",  text: "#ffb22e" };
  if (l.includes("low"))          return { bg: "rgba(255,148,102,0.10)", text: "#ff9466" };
  return                                 { bg: "rgba(255,100,80,0.10)",  text: "#ff6450" };
}

export function ResultsPanel({ results, isScanning }: ResultsPanelProps) {
  const [activeStep, setActiveStep] = useState(0);

  useEffect(() => {
    if (!isScanning) { setActiveStep(0); return; }
    const interval = setInterval(() => {
      setActiveStep((prev) => (prev < 6 ? prev + 1 : prev));
    }, 1100);
    return () => clearInterval(interval);
  }, [isScanning]);

  if (isScanning) {
    const steps = [
      { icon: "🔍", title: "Nemotron OCR v2",              desc: "Extracting transaction fields, UPI handles & timestamps..." },
      { icon: "🛡️", title: "App Forensics + Dual AI Blend", desc: "Color fingerprint + NemotronNano12B branding authentication..." },
      { icon: "📡", title: "EXIF & Metadata Analysis",      desc: "Checking editing software traces, GPS strips, timestamp delta..." },
      { icon: "🤖", title: "Hive Deepfake Detector",        desc: "Scanning pixel entropy for AI-generation and splicing artifacts..." },
      { icon: "🔗", title: "Razorpay VPA Live Lookup",      desc: "Verifying UPI VPA exists in NPCI registry via live API..." },
      { icon: "🧠", title: "Qwen 3.5-397B Reasoning",       desc: "Synthesising all signals into a natural-language verdict..." },
      { icon: "🏁", title: "Trust Score Engine v2",         desc: "Applying additive formula + hard caps → final 0–100 score..." },
    ];

    return (
      <div className="product-panel results-panel">
        <div className="product-panel-header">
          <span className="dot" style={{ backgroundColor: "var(--signal)", boxShadow: "0 0 12px var(--signal)" }} />
          Active Scan Diagnostics
        </div>
        
        <div className="results-panel-content" style={{ display: "flex", flexDirection: "column", gap: "20px", padding: "20px" }}>
          <div style={{ display: "grid", placeItems: "center", margin: "10px 0" }}>
            <div className="radar-scanner">
              <div className="radar-sweep" />
              <div className="radar-ping" />
              <span style={{
                fontFamily: "var(--font-mono)", fontSize: "0.74rem", fontWeight: 950,
                color: "var(--foreground)", zIndex: 6,
                background: "var(--bg)", border: "1px solid var(--border-active)", borderRadius: "999px",
                padding: "6px 14px", boxShadow: "0 4px 12px rgba(var(--shadow-rgb), 0.5), 0 0 10px rgba(219,255,74,0.15)",
                textShadow: "0 0 8px rgba(255,255,255,0.3)"
              }}>
                {activeStep < 6 ? "RUNNING" : "RESOLVING"}
              </span>
            </div>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
            {steps.map((step, idx) => {
              const isCompleted = idx < activeStep;
              const isActive    = idx === activeStep;
              const isPending   = idx > activeStep;
              return (
                <div key={idx}
                  className={`scanning-step ${isCompleted ? "completed" : isActive ? "active" : "pending"}`}
                  style={{ opacity: isPending ? 0.32 : 1 }}
                >
                  <span className="step-icon">{step.icon}</span>
                  <div className="step-content">
                    <strong>{step.title}</strong>
                    <p>{step.desc}</p>
                  </div>
                  {isCompleted && <div className="step-checkmark">✓</div>}
                  {isActive    && <div className="scanning-spinner" />}
                  {isPending   && <div style={{ width: "10px", height: "10px", border: "1px solid var(--border)", borderRadius: "50%", alignSelf: "center", marginRight: "3px" }} />}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    );
  }

  if (!results) {
    return (
      <div className="product-panel results-panel">
        <div className="product-panel-header">
          <span className="dot" style={{ background: "rgba(255,255,255,0.2)" }} /> Verification Status
        </div>
        <div className="results-panel-content" style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "40px 24px", textAlign: "center", color: "var(--foreground-dim)", gap: "16px", height: "100%" }}>
          <div style={{ fontSize: "2.5rem", opacity: 0.75 }}>🛡️</div>
          <strong style={{ fontSize: "0.92rem", color: "var(--foreground)" }}>Ready for Forensic Scan</strong>
          <p style={{ fontSize: "0.78rem", lineHeight: 1.5, margin: 0, maxWidth: "290px", color: "var(--foreground-muted)" }}>
            Upload a transaction screenshot, bank PDF statement, or payment QR code inside the mockup screen to generate a real-time risk assessment report.
          </p>
        </div>
      </div>
    );
  }

  // 1. PDF File Results
  if (results.file_type === "pdf" && results.document_result) {
    const doc = results.document_result;
    return (
      <div className="product-panel results-panel">
        <div className="product-panel-header">
          <span className="dot" /> Document Forensic Results
        </div>
        
      <div className="results-panel-content">
        <div className="result-block" style={{ textAlign: "center", padding: "24px 0 8px" }}>
          <div className="result-score-number" style={{ color: doc.risk_level === "LOW" ? "#31f58b" : doc.risk_level === "MEDIUM" ? "#ffb22e" : "#ff4d2e" }}>
            {doc.risk_level}
          </div>
          <div className="result-score-label">Document Threat Risk Level</div>
          <div className="result-verdict" style={{
            borderColor: doc.risk_level === "LOW" ? "#31f58b55" : "#ff4d2e55",
            background: doc.risk_level === "LOW" ? "#31f58b0a" : "#ff4d2e0a"
          }}>
            <span>Verdict</span>
            <strong style={{ color: doc.risk_level === "LOW" ? "#31f58b" : "#ff4d2e" }}>
              {doc.risk_level === "LOW" ? "✓ Appears Legitimate" : "⚠ Suspected Threat"}
            </strong>
          </div>
        </div>

        <div className="result-block">
          <h4 className="result-block-title">File Details</h4>
          <div className="result-row">
            <span className="label">Document Type</span>
            <span className="value">{doc.document_type.toUpperCase()}</span>
          </div>
          <div className="result-row">
            <span className="label">Page Count</span>
            <span className="value">{doc.page_count}</span>
          </div>
        </div>

        <div className="result-block">
          <h4 className="result-block-title">Document Heuristics</h4>
          {doc.heuristics_checklist && doc.heuristics_checklist.length > 0 ? (
            doc.heuristics_checklist.map((item: any, idx: number) => (
              <div key={idx} className="result-row" style={{ display: "block", marginBottom: "12px", borderBottom: idx !== doc.heuristics_checklist.length - 1 ? "1px solid rgba(255,255,255,0.05)" : "none", paddingBottom: "10px" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span className="label" style={{ fontWeight: 600 }}>{item.label}</span>
                  <span className={`value ${item.risk === "HIGH" ? "danger" : item.risk === "MEDIUM" ? "warn" : "success"}`}>
                    {item.status}
                  </span>
                </div>
                {item.reasoning && (
                  <p style={{ fontSize: "0.8rem", color: "var(--text-muted)", margin: "4px 0 0 0", lineHeight: 1.4 }}>
                    {item.reasoning}
                  </p>
                )}
              </div>
            ))
          ) : (
            <>
              <div className="result-row">
                <span className="label">Steganography Check</span>
                <span className={`value ${doc.steganography_suspected ? "danger" : "success"}`}>
                  {doc.steganography_suspected ? "⚠ SUSPICIOUS" : "✓ PASS"}
                </span>
              </div>
              <div className="result-row">
                <span className="label">Embedded JS / Triggers</span>
                <span className={`value ${doc.pdf_javascript_found || doc.pdf_auto_action_found ? "danger" : "success"}`}>
                  {doc.pdf_javascript_found || doc.pdf_auto_action_found ? "⚠ DETECTED" : "✓ PASS"}
                </span>
              </div>
              <div className="result-row">
                <span className="label">Embedded Files count</span>
                <span className="value">{doc.embedded_file_count}</span>
              </div>
            </>
          )}
        </div>

        {doc.urls_found.length > 0 && (
          <div className="result-block">
            <h4 className="result-block-title">URL Safety Scan ({doc.urls_found.length} links)</h4>
            <div className="result-row">
              <span className="label">URL Risk level</span>
              <span className={`value ${doc.url_risk_level === "HIGH" ? "danger" : doc.url_risk_level === "MEDIUM" ? "warn" : "success"}`}>
                {doc.url_risk_level}
              </span>
            </div>
            <ul style={{ padding: 0, margin: "8px 0 0 0", listStyle: "none" }}>
              {doc.url_analysis.slice(0, 4).map((urlData: any, idx: number) => (
                <li key={idx} className="result-reason" style={{ borderLeftColor: urlData.risk === "HIGH" ? "var(--ember)" : "var(--warn)" }}>
                  <strong>{urlData.url}</strong>: {urlData.reasons.join(", ") || "Safe domain"}
                </li>
              ))}
            </ul>
          </div>
        )}

        <div className="result-block">
          <h4 className="result-block-title">Forensic Assessment</h4>
          <p className="result-reason" style={{ borderLeftColor: doc.risk_level === "LOW" ? "#31f58b" : "#ff4d2e" }}>
            {doc.explanation}
          </p>
        </div>
      </div>
      </div>
    );
  }

  // 2. QR Code Scanner Results
  if (results.file_type === "qr" && results.qr_result) {
    const qr = results.qr_result;
    const isUpi = qr.is_upi;
    const p = qr.upi_payload;
    return (
      <div className="product-panel results-panel">
        <div className="product-panel-header">
          <span className="dot" /> QR Code Analysis
        </div>
        
      <div className="results-panel-content">
        <div className="result-block" style={{ textAlign: "center", padding: "24px 0 8px" }}>
          <div className="result-score-number" style={{
            color: qr.risk_level === "HIGH" ? "#ff4d2e" : qr.risk_level === "MEDIUM" ? "#ffb22e" : "#31f58b"
          }}>
            {isUpi ? "UPI QR" : "URL QR"}
          </div>
          <div className="result-score-label">Payload Type</div>
          <div className="result-verdict" style={{
            borderColor: qr.risk_level === "HIGH" ? "#ff4d2e55" : qr.risk_level === "MEDIUM" ? "#ffb22e55" : "#31f58b55",
            background: qr.risk_level === "HIGH" ? "#ff4d2e0a" : qr.risk_level === "MEDIUM" ? "#ffb22e0a" : "#31f58b0a"
          }}>
            <span>Verdict</span>
            <strong style={{
              color: qr.risk_level === "HIGH" ? "#ff4d2e" : qr.risk_level === "MEDIUM" ? "#ffb22e" : "#31f58b"
            }}>
              {qr.risk_level === "HIGH" ? "❌ High Risk Payload" : qr.risk_level === "MEDIUM" ? "⚠ Suspicious Payload" : "✓ Secure Payload"}
            </strong>
          </div>
        </div>

        {isUpi && p ? (
          <div className="result-block">
            <h4 className="result-block-title">UPI Parameters</h4>
            <div className="result-row">
              <span className="label">VPA (Receiver Address)</span>
              <span className="value" style={{ color: "var(--signal)" }}>{p.pa}</span>
            </div>
            <div className="result-row">
              <span className="label">Receiver Name</span>
              <span className="value">{p.pn || "N/A"}</span>
            </div>
            <div className="result-row">
              <span className="label">Hardcoded Amount</span>
              <span className="value">{p.am ? `₹${p.am}` : "User input requested"}</span>
            </div>
            <div className="result-row">
              <span className="label">Currency</span>
              <span className="value">{p.cu || "INR"}</span>
            </div>
            <div className="result-row">
              <span className="label">Verified Merchant Sign</span>
              <span className={`value ${p.sign ? "success" : "warn"}`}>
                {p.sign ? "✓ Present" : "⚠ None (Personal QR)"}
              </span>
            </div>
          </div>
        ) : (
          <div className="result-block">
            <h4 className="result-block-title">QR Payload Link</h4>
            <p className="result-reason" style={{ wordBreak: "break-all", fontStyle: "italic" }}>
              {qr.raw_qr_data}
            </p>
          </div>
        )}

        <div className="result-block">
          <h4 className="result-block-title">Risk Signals</h4>
          <ul style={{ padding: 0, margin: "8px 0 0 0", listStyle: "none" }}>
            {qr.risk_signals && qr.risk_signals.length > 0 ? (
              qr.risk_signals.map((sig: string, idx: number) => (
                <li key={idx} className="result-reason" style={{ borderLeftColor: "var(--ember)" }}>{sig}</li>
              ))
            ) : (
              <li className="result-action" style={{ borderLeftColor: "var(--success)" }}>All QR integrity validations passed.</li>
            )}
          </ul>
        </div>
      </div>
      </div>
    );
  }

  const screenshotData = results.screenshot_result || (results as any);
  const { trust_score_data, ocr_data, fraud_intelligence_data, metadata,
          deepfake_data, vpa_validation_data, deterministic_flags, app_forensics } = screenshotData;

  const finalVerdict  = trust_score_data.verdict || "Analysis Complete";
  const verdictStyle  = getVerdictStyle(finalVerdict);
  const ocrPct        = Math.round(ocr_data.confidence_score * 100);
  const qualityLabel  = trust_score_data.extraction_quality_label;
  const qualityBadge  = qualityLabel ? getQualityBadgeStyle(qualityLabel) : null;
  const scoreColor    = verdictStyle.color;
  const imageQualPct  = ocr_data.image_quality_score != null ? Math.round(ocr_data.image_quality_score * 100) : null;
  const deepfakePct   = deepfake_data ? Math.round(deepfake_data.deepfake_probability * 100) : null;

  return (
    <div className="product-panel results-panel">
      <div className="product-panel-header">
        <span className="dot" /> Forensic Results
      </div>

      <div className="results-panel-content">
        {/* ── Trust Score Hero ── */}
        <div className="result-block">
          <div className="result-score">
            <div className="result-score-number" style={{ color: scoreColor }}>
              {Math.round(trust_score_data.trust_score)}
            </div>
            <div className="result-score-label">Trust Score / 100</div>
            <div className="result-verdict" style={{ borderColor: `${scoreColor}55`, background: `${scoreColor}0a` }}>
              <span>Verdict</span>
              <strong style={{ color: verdictStyle.color }}>{verdictStyle.icon} {finalVerdict}</strong>
            </div>
            {qualityLabel && qualityBadge && (
              <div style={{
                marginTop: "8px", display: "inline-block", padding: "4px 12px",
                borderRadius: "20px", fontSize: "0.72rem", fontWeight: 500, letterSpacing: "0.04em",
                background: qualityBadge.bg, color: qualityBadge.text, border: `1px solid ${qualityBadge.text}22`,
              }}>
                {qualityLabel}
              </div>
            )}
          </div>
        </div>

        {/* ── Score Breakdown ── */}
        {deterministic_flags?.score_breakdown && (
          <div className="result-block">
            <h4 className="result-block-title">Score Breakdown</h4>
            <ScoreBreakdown
              breakdown={deterministic_flags.score_breakdown}
              caps={deterministic_flags.triggered_caps}
            />
          </div>
        )}

        {/* ── Deterministic Flags ── */}
        {deterministic_flags && (
          <div className="result-block">
            <h4 className="result-block-title">Deterministic Flags</h4>
            <div className="flags-grid">
              <FlagChip
                label="Foreign Currency"
                active={deterministic_flags.foreign_currency_detected}
                danger
              />
              <FlagChip
                label="UTR Format Issue"
                active={deterministic_flags.utr_format_violation || deterministic_flags.utr_dummy_pattern}
                danger
              />
              <FlagChip
                label="EXIF Editing SW"
                active={deterministic_flags.exif_editing_software}
                danger
                detail={deterministic_flags.exif_software_name ?? undefined}
              />
              <FlagChip
                label="Late Night Txn"
                active={deterministic_flags.timestamp_late_night}
                warn
              />
              <FlagChip
                label="Replay Attack"
                active={deterministic_flags.replay_detected}
                danger
                detail={deterministic_flags.replay_count > 0 ? `${deterministic_flags.replay_count}×` : undefined}
              />
            </div>
          </div>
        )}

        {/* ── Deepfake Detection ── */}
        {deepfake_data && (
          <div className="result-block">
            <h4 className="result-block-title">Deepfake Detection</h4>
            <div style={{ marginBottom: "10px" }}>
              <div className="score-bar-meta">
                <span className="score-bar-label">AI Manipulation Probability</span>
                <span className="score-bar-pts" style={{
                  color: (deepfakePct ?? 0) > 70 ? "var(--ember)" : (deepfakePct ?? 0) > 40 ? "var(--warn)" : "var(--success)"
                }}>
                  {deepfakePct}%
                </span>
              </div>
              <div className="score-bar-track">
                <div className="score-bar-fill" style={{
                  width: `${deepfakePct}%`,
                  background: (deepfakePct ?? 0) > 70
                    ? "var(--ember)"
                    : (deepfakePct ?? 0) > 40
                    ? "var(--warn)"
                    : "var(--success)",
                  boxShadow: (deepfakePct ?? 0) > 70 ? "0 0 8px var(--ember-glow)" : "0 0 8px var(--signal-glow)",
                }} />
              </div>
            </div>
            <div className="result-row">
              <span className="label">Verdict</span>
              <span className={`value ${deepfake_data.is_deepfake ? "danger" : "success"}`}>
                {deepfake_data.is_deepfake ? "⚠ Manipulation Detected" : "✓ Appears Authentic"}
              </span>
            </div>
            {deepfake_data.manipulation_type && deepfake_data.manipulation_type !== "none" && deepfake_data.manipulation_type !== "unknown" && (
              <div className="result-row">
                <span className="label">Type</span>
                <span className="value warn">{deepfake_data.manipulation_type}</span>
              </div>
            )}
            {deepfake_data.signals?.length > 0 && (
              <ul className="signal-list">
                {deepfake_data.signals.slice(0, 4).map((s: string, i: number) => (
                  <li key={i}>{s}</li>
                ))}
              </ul>
            )}
          </div>
        )}

        {/* ── App Forensics ── */}
        {app_forensics && (
          <div className="result-block">
            <h4 className="result-block-title">App Forensics</h4>
            <div className="result-row">
              <span className="label">Detected App</span>
              <span className="value">{app_forensics.detected_app}</span>
            </div>
            <div className="result-row">
              <span className="label">Logo Match</span>
              <span className={`value ${app_forensics.logo_match ? "success" : "warn"}`}>
                {app_forensics.logo_match ? "✓ Matched" : "⚠ No Match"}
              </span>
            </div>
            <div className="result-row">
              <span className="label">Layout Consistency</span>
              <span className={`value ${app_forensics.layout_consistency === "HIGH" ? "success" : app_forensics.layout_consistency === "MEDIUM" ? "warn" : "danger"}`}>
                {app_forensics.layout_consistency}
              </span>
            </div>
            <div className="result-row">
              <span className="label">Clone Suspected</span>
              <span className={`value ${app_forensics.suspected_clone ? "danger" : "success"}`}>
                {app_forensics.suspected_clone ? "⚠ Yes" : "✓ No"}
              </span>
            </div>
            {app_forensics.explanation && (
              <p style={{ fontSize: "0.76rem", color: "var(--foreground-muted)", marginTop: "8px", lineHeight: 1.5, fontStyle: "italic" }}>
                {app_forensics.explanation}
              </p>
            )}
          </div>
        )}

        {/* ── UPI & Transaction Integrity ── */}
        {(vpa_validation_data || deterministic_flags) && (
          <div className="result-block">
            <h4 className="result-block-title">UPI & Transaction Integrity</h4>
            
            {vpa_validation_data && (
              <>
                <div className="result-row">
                  <span className="label">VPA (UPI ID) Address</span>
                  <span className="value" style={{ fontFamily: "var(--font-mono)", color: "var(--signal)" }}>
                    {vpa_validation_data.upi_id || "Not Found"}
                  </span>
                </div>
                <div className="result-row">
                  <span className="label">VPA Registry Check</span>
                  <span className={`value ${vpa_validation_data.vpa_exists === true ? "success" : vpa_validation_data.vpa_exists === false ? "danger" : "warn"}`}>
                    {vpa_validation_data.vpa_exists === true ? "✓ VALID VPA" : vpa_validation_data.vpa_exists === false ? "❌ VPA DOES NOT EXIST" : "⚠ LOOKUP FAILED"}
                  </span>
                </div>
                {vpa_validation_data.registered_name && (
                  <div className="result-row">
                    <span className="label">VPA Registered Name</span>
                    <span className="value">{vpa_validation_data.registered_name}</span>
                  </div>
                )}
                {vpa_validation_data.name_match !== null && (
                  <div className="result-row">
                    <span className="label">Receiver Name Correlation</span>
                    <span className={`value ${vpa_validation_data.name_match ? "success" : "warn"}`}>
                      {vpa_validation_data.name_match ? "✓ MATCHED" : "⚠ MISMATCHED / SUSPICIOUS"}
                    </span>
                  </div>
                )}
              </>
            )}

            {deterministic_flags && (
              <div className="result-row" style={{ marginTop: "8px", paddingTop: "8px", borderTop: "1px solid rgba(255,255,255,0.05)" }}>
                <span className="label">Transaction Replay Attack</span>
                <span className={`value ${deterministic_flags.replay_detected ? "danger font-extrabold animate-pulse" : "success"}`}>
                  {deterministic_flags.replay_detected 
                    ? `❌ REPLAY DETECTED (${deterministic_flags.replay_count} times seen)` 
                    : "✓ UNIQUE (First scan)"}
                </span>
              </div>
            )}
          </div>
        )}

        {/* ── OCR Data ── */}
        <div className="result-block">
          <h4 className="result-block-title" style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            OCR Data
            <span style={{
              fontSize: "0.68rem", fontWeight: 400, padding: "2px 8px", borderRadius: "10px",
              background: ocrPct >= 70 ? "var(--signal-glow)" : ocrPct >= 40 ? "rgba(255,178,46,0.10)" : "var(--ember-glow)",
              color: ocrPct >= 70 ? "var(--success)" : ocrPct >= 40 ? "var(--warn)" : "var(--ember)",
            }}>
              {ocrPct}% confidence
            </span>
          </h4>
          {([
            ["Amount",         ocr_data.fields.payment_amount ? (
              /^[₹$€£]|^(?:Rs\.?|INR)/i.test(ocr_data.fields.payment_amount)
                ? ocr_data.fields.payment_amount
                : `₹${ocr_data.fields.payment_amount}`) : "N/A"],
            ["Transaction ID", ocr_data.fields.upi_transaction_id || "N/A"],
            ["Receiver",       ocr_data.fields.receiver_name || "N/A"],
            ["Timestamp",      ocr_data.fields.timestamp || "N/A"],
            ["Payment App",    ocr_data.fields.payment_app_name || "N/A"],
            ...(imageQualPct != null ? [["Image Quality", `${imageQualPct}%`]] : []),
          ] as [string, string][]).map(([label, value]) => (
            <div className="result-row" key={label}>
              <span className="label">{label}</span>
              <span className="value">{value}</span>
            </div>
          ))}
        </div>

        {/* ── Fraud Intelligence ── */}
        <div className="result-block">
          <h4 className="result-block-title">Fraud Intelligence</h4>
          <div className="result-row">
            <span className="label">Template Match</span>
            <span className={`value ${fraud_intelligence_data.fingerprint_match ? "danger" : "success"}`}>
              {fraud_intelligence_data.fingerprint_match ? "⚠ DETECTED" : "✓ CLEAR"}
            </span>
          </div>
          <div className="result-row">
            <span className="label">Confidence</span>
            <span className="value">{Math.round(fraud_intelligence_data.match_confidence * 100)}%</span>
          </div>
          <div className="result-row">
            <span className="label">Fraud Type</span>
            <span className="value">{fraud_intelligence_data.fraud_type || "None Detected"}</span>
          </div>
        </div>

        {/* ── AI Reasoning ── */}
        <div className="result-block">
          <h4 className="result-block-title">AI Reasoning</h4>
          <ul style={{ padding: 0, margin: "8px 0 0 0", listStyle: "none" }}>
            {(trust_score_data.confidence_reasoning.length > 0
              ? trust_score_data.confidence_reasoning
              : ["Standard verification checks passed successfully."]
            ).map((reason: string, idx: number) => (
              <li key={idx} className="result-reason">{reason}</li>
            ))}
          </ul>
        </div>

        {/* ── Recommended Actions ── */}
        <div className="result-block">
          <h4 className="result-block-title">Recommended Actions</h4>
          <ul style={{ padding: 0, margin: "8px 0 0 0", listStyle: "none" }}>
            {(trust_score_data.recommended_actions.length > 0
              ? trust_score_data.recommended_actions
              : ["Verify transaction UTR and receiver credentials directly in your banking app before releasing goods."]
            ).map((action: string, idx: number) => (
              <li key={idx} className="result-action">{action}</li>
            ))}
          </ul>
        </div>

        {/* ── Scan Metadata ── */}
        <div className="result-block">
          <h4 className="result-block-title">Scan Metadata</h4>
          <div className="result-row">
            <span className="label">Execution Time</span>
            <span className="value">{(metadata.execution_time_ms / 1000).toFixed(2)}s</span>
          </div>
        </div>
      </div>
    </div>
  );
}

function FlagChip({ label, active, danger, warn, detail }: {
  label: string; active: boolean; danger?: boolean; warn?: boolean; detail?: string;
}) {
  if (!active) return (
    <div className="flag-chip flag-chip--ok">
      <span className="flag-chip-dot" />
      {label}
    </div>
  );
  const colorVar = danger ? "var(--ember)" : warn ? "var(--warn)" : "var(--success)";
  const bgVar = danger ? "var(--ember-glow)" : warn ? "rgba(255, 178, 46, 0.15)" : "var(--signal-glow)";
  return (
    <div className="flag-chip flag-chip--active" style={{ borderColor: colorVar, background: bgVar, color: colorVar }}>
      <span className="flag-chip-dot" style={{ background: colorVar, boxShadow: `0 0 6px ${colorVar}` }} />
      {label}{detail ? ` (${detail})` : ""}
    </div>
  );
}
