"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

export function ForensicScanSection() {
  const [activePhase, setActivePhase] = useState(1);
  const [liveTrustScore, setLiveTrustScore] = useState(100);

  // Auto-cycle the active phase every 3.8 seconds
  useEffect(() => {
    const timer = setInterval(() => {
      setActivePhase((prev) => (prev % 3) + 1);
    }, 4000);
    return () => clearInterval(timer);
  }, []);

  // Animate the local trust score countdown when phase 3 is active
  useEffect(() => {
    if (activePhase === 3) {
      let current = 100;
      const interval = setInterval(() => {
        if (current > 26) {
          current -= 2;
          setLiveTrustScore(Math.max(current, 26));
        } else {
          clearInterval(interval);
        }
      }, 25);
      return () => clearInterval(interval);
    } else {
      setLiveTrustScore(100);
    }
  }, [activePhase]);

  type DataRow = {
    label: string;
    val: string;
    highlight: boolean;
    color?: string;
    useLiveScore?: boolean;
  };

  const phases: {
    id: number;
    tag: string;
    title: string;
    desc: string;
    glowColor: string;
    borderColor: string;
    statusText: string;
    rows: DataRow[];
  }[] = [
    {
      id: 1,
      tag: "Phase 01",
      title: "OCR Extraction",
      desc: "Extracts deep transaction strings and counter QR payees directly from raw screenshot pixels.",
      glowColor: "rgba(52, 230, 255, 0.28)",
      borderColor: "var(--cyan)",
      statusText: "DEEP OCR PROCESSOR ACTIVE",
      rows: [
        { label: "Detected Amount", val: "₹4,500", highlight: false },
        { label: "Extracted VPA", val: "9876543210@ybl", highlight: false },
        { label: "Claimed Merchant", val: "Ramesh Kirana", highlight: false },
        { label: "QR payload check", val: "MISMATCH", highlight: true, color: "var(--ember)" }
      ]
    },
    {
      id: 2,
      tag: "Phase 02",
      title: "Fraud Intelligence",
      desc: "Performs real-time template match checks against known cloner APK outputs and fake receipts.",
      glowColor: "rgba(219, 255, 74, 0.28)",
      borderColor: "var(--signal)",
      statusText: "TEMPLATE PATTERN COMPILING",
      rows: [
        { label: "Template Match", val: "DETECTED", highlight: true, color: "var(--ember)" },
        { label: "Match Confidence", val: "98%", highlight: false, color: "var(--signal)" },
        { label: "Signature DB", val: "12,847 patterns", highlight: false },
        { label: "Suspect Profile", val: "Paytm Fake Clone v4", highlight: false }
      ]
    },
    {
      id: 3,
      tag: "Phase 03",
      title: "Trust Calculation",
      desc: "Passes extracted values and pattern matches through our secure verification weighting loop.",
      glowColor: "rgba(255, 77, 46, 0.28)",
      borderColor: "var(--ember)",
      statusText: "COMPUTING SYSTEM LOGS",
      rows: [
        { label: "Calculated Score", val: `${liveTrustScore}%`, highlight: true, color: "var(--ember)", useLiveScore: true },
        { label: "System Risk Level", val: "HIGH", highlight: true, color: "var(--ember)" },
        { label: "Fraud Probability", val: "99%", highlight: true, color: "var(--ember)" },
        { label: "Final Verdict", val: "LIKELY FAKE PROOF", highlight: true, color: "var(--ember)" }
      ]
    }
  ];


  return (
    <section id="forensic-scan" className="tl-section forensic-section" style={{ position: "relative" }}>
      <div className="tl-section-inner">
        <div className="forensic-header reveal-up">
          <span className="section-tag">The Solution</span>
          <h2>AI Forensic Intelligence</h2>
          <p>
            TrustLayer executes a sequential multi-stage verification stack, actively scanning files to detect tampering signatures in real time.
          </p>
        </div>

        {/* Dynamic Timeline Indicator Connector (Desktop) */}
        <div
          className="timeline-rail"
          style={{
            position: "relative",
            width: "80%",
            height: "2px",
            background: "rgba(255,248,238,0.06)",
            margin: "0 auto 40px",
            borderRadius: "999px",
            display: "block"
          }}
        >
          <motion.div
            style={{
              position: "absolute",
              top: "-2px",
              height: "6px",
              width: "12px",
              borderRadius: "50%",
              background: activePhase === 1 ? "var(--cyan)" : activePhase === 2 ? "var(--signal)" : "var(--ember)",
              boxShadow: activePhase === 1 ? "0 0 12px var(--cyan)" : activePhase === 2 ? "0 0 12px var(--signal)" : "0 0 12px var(--ember)"
            }}
            animate={{
              left: activePhase === 1 ? "16%" : activePhase === 2 ? "50%" : "84%"
            }}
            transition={{ type: "spring", stiffness: 90, damping: 15 }}
          />
          <motion.div
            style={{
              position: "absolute",
              top: 0,
              height: "2px",
              background: activePhase === 1 ? "var(--cyan)" : activePhase === 2 ? "var(--signal)" : "var(--ember)",
              boxShadow: activePhase === 1 ? "0 0 8px var(--cyan)" : activePhase === 2 ? "0 0 8px var(--signal)" : "0 0 8px var(--ember)"
            }}
            animate={{
              left: 0,
              width: activePhase === 1 ? "16%" : activePhase === 2 ? "50%" : "84%"
            }}
            transition={{ type: "spring", stiffness: 90, damping: 15 }}
          />
        </div>

        {/* Forensic Cards Grid */}
        <div className="forensic-grid">
          {phases.map((phase) => {
            const isActive = activePhase === phase.id;

            return (
              <motion.div
                key={phase.id}
                onClick={() => setActivePhase(phase.id)}
                className={`forensic-card ${isActive ? "active" : ""}`}
                animate={{
                  scale: isActive ? 1.02 : 0.98,
                  borderColor: isActive ? phase.borderColor : "rgba(255,248,238,0.1)",
                  boxShadow: isActive
                    ? `0 18px 45px rgba(0,0,0,0.5), 0 0 20px ${phase.glowColor}`
                    : "0 4px 20px rgba(0,0,0,0.15)"
                }}
                transition={{ type: "tween", duration: 0.35 }}
                style={{
                  cursor: "pointer",
                  position: "relative",
                  display: "flex",
                  flexDirection: "column",
                  border: "1px solid",
                  background: isActive ? "rgba(255,248,238,0.03)" : "rgba(255,248,238,0.015)"
                }}
              >
                {/* Visual Header Tag */}
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "14px" }}>
                  <span
                    className="forensic-card-tag"
                    style={{
                      color: isActive ? phase.borderColor : "var(--foreground-dim)",
                      marginBottom: 0
                    }}
                  >
                    {phase.tag}
                  </span>
                  
                  {isActive && (
                    <motion.span
                      animate={{ opacity: [0.4, 1, 0.4] }}
                      transition={{ repeat: Infinity, duration: 1.5 }}
                      style={{
                        display: "inline-block",
                        width: "6px",
                        height: "6px",
                        borderRadius: "50%",
                        background: phase.borderColor,
                        boxShadow: `0 0 8px ${phase.borderColor}`
                      }}
                    />
                  )}
                </div>

                <h3 style={{ fontSize: "1.2rem", fontWeight: 850 }}>{phase.title}</h3>
                <p style={{ flexGrow: 1, minHeight: "56px", fontSize: "0.84rem", color: "var(--foreground-muted)" }}>
                  {phase.desc}
                </p>

                {/* Staggered Rows / Real-time compilation vibe */}
                <div style={{ display: "flex", flexDirection: "column", gap: "6px", width: "100%", marginTop: "14px", borderTop: "1px solid rgba(255,248,238,0.06)", paddingTop: "14px" }}>
                  {isActive ? (
                    <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                      {/* Active Status Header */}
                      <div style={{ fontSize: "0.58rem", fontFamily: "var(--font-mono)", color: phase.borderColor, fontWeight: 900, marginBottom: "4px", letterSpacing: "0.08em" }}>
                        ⚡ {phase.statusText}
                      </div>

                      {phase.rows.map((row, idx) => (
                        <motion.div
                          key={row.label}
                          initial={{ opacity: 0, x: -10 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: idx * 0.15, duration: 0.3 }}
                          className="forensic-data-row"
                          style={{
                            display: "flex",
                            justifyContent: "space-between",
                            fontSize: "0.76rem",
                            padding: "4px 0",
                            borderBottom: "1px solid rgba(255,248,238,0.02)"
                          }}
                        >
                          <span style={{ color: "var(--foreground-dim)" }}>{row.label}</span>
                          <strong
                            style={{
                              color: row.color ? row.color : "var(--foreground)",
                              textShadow: row.highlight ? `0 0 6px ${row.color || "rgba(255,255,255,0.4)"}` : "none"
                            }}
                          >
                            {row.useLiveScore ? `${liveTrustScore}%` : row.val}
                          </strong>
                        </motion.div>
                      ))}
                    </div>
                  ) : (
                    <div style={{ opacity: 0.3, pointerEvents: "none" }}>
                      <div style={{ fontSize: "0.58rem", fontFamily: "var(--font-mono)", color: "var(--foreground-dim)", fontWeight: 900, marginBottom: "4px" }}>
                        OFFLINE
                      </div>
                      {phase.rows.map((row) => (
                        <div key={row.label} className="forensic-data-row" style={{ display: "flex", justifyContent: "space-between", fontSize: "0.76rem", padding: "4px 0" }}>
                          <span>{row.label}</span>
                          <strong>{row.useLiveScore ? "100%" : row.val}</strong>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
