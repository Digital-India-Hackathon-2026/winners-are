"use client";

import { useEffect, useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";

function TypewriterText({ text }: { text: string }) {
  const [displayedText, setDisplayedText] = useState("");

  useEffect(() => {
    // Check if prefers reduced motion is active
    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (prefersReducedMotion) {
      setDisplayedText(text);
      return;
    }

    setDisplayedText("");
    let i = 0;
    const interval = setInterval(() => {
      if (i < text.length) {
        setDisplayedText(text.substring(0, i + 1));
        i++;
      } else {
        clearInterval(interval);
      }
    }, 30);
    return () => clearInterval(interval);
  }, [text]);

  return (
    <span style={{ display: "inline-flex", alignItems: "center" }}>
      {displayedText}
      <span className="typewriter-cursor">_</span>
    </span>
  );
}

type ForensicPhoneProps = {
  active?: boolean;
};

export function ForensicPhone({ active = true }: ForensicPhoneProps) {
  const [step, setStep] = useState(0);
  const [rotateX, setRotateX] = useState(0);
  const [rotateY, setRotateY] = useState(0);
  const [trustScore, setTrustScore] = useState(100);
  const containerRef = useRef<HTMLDivElement>(null);

  // Auto-advance loop for scanning phases
  useEffect(() => {
    if (!active) return;
    const timer = setInterval(() => {
      setStep((prev) => (prev + 1) % 5);
    }, 2800);
    return () => clearInterval(timer);
  }, [active]);

  // Animate trust score ticking down when we reach the verdict step (step 4)
  useEffect(() => {
    if (step === 4) {
      let current = 100;
      const interval = setInterval(() => {
        if (current > 26) {
          current -= 2;
          setTrustScore(Math.max(current, 26));
        } else {
          clearInterval(interval);
        }
      }, 20);
      return () => clearInterval(interval);
    } else {
      setTrustScore(100);
    }
  }, [step]);

  // Handle mouse move for 3D parallax tilt
  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left - rect.width / 2;
    const y = e.clientY - rect.top - rect.height / 2;
    // Limit rotation to max 7 degrees for a premium subtle effect
    setRotateX(-(y / (rect.height / 2)) * 7);
    setRotateY((x / (rect.width / 2)) * 7);
  };

  const handleMouseLeave = () => {
    setRotateX(0);
    setRotateY(0);
  };

  // Determine glow colors based on the scanning phase
  const getGlowColor = () => {
    switch (step) {
      case 0: return "radial-gradient(circle, rgba(52, 230, 255, 0.15) 0%, rgba(52, 230, 255, 0.05) 50%, transparent 70%)";
      case 1:
      case 2: return "radial-gradient(circle, rgba(219, 255, 74, 0.15) 0%, rgba(219, 255, 74, 0.05) 50%, transparent 70%)";
      case 3:
      case 4: return "radial-gradient(circle, rgba(255, 77, 46, 0.18) 0%, rgba(255, 77, 46, 0.06) 50%, transparent 70%)";
      default: return "radial-gradient(circle, rgba(255, 255, 255, 0.08) 0%, transparent 70%)";
    }
  };

  const getStatusText = () => {
    switch (step) {
      case 0: return "ANALYZING PIXELS";
      case 1: return "EXTRACTING OCR DATA";
      case 2: return "VERIFYING UPI ID";
      case 3: return "CROSS-CORRELATING QR";
      case 4: return "FORENSIC COMPLETE";
      default: return "ACTIVE SCANNER";
    }
  };

  return (
    <div
      ref={containerRef}
      className="hero-phone-wrap"
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      style={{
        perspective: 1000,
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        width: "100%",
        cursor: "pointer"
      }}
    >
      {/* Ambient background glow dynamic backplate */}
      <div
        className="hero-phone-glow"
        style={{
          background: getGlowColor(),
          transition: "background 0.8s ease",
          position: "absolute",
          width: "350px",
          height: "350px",
          borderRadius: "50%",
          filter: "blur(40px)",
          zIndex: 0,
          pointerEvents: "none"
        }}
      />

      {/* Main 3D Phone Shell */}
      <motion.div
        className="phone-shell"
        animate={{
          rotateX,
          rotateY,
          y: [0, -6, 0]
        }}
        transition={{
          rotateX: { type: "spring", stiffness: 120, damping: 20 },
          rotateY: { type: "spring", stiffness: 120, damping: 20 },
          y: { repeat: Infinity, duration: 4.8, ease: "easeInOut" }
        }}
        style={{
          visibility: "visible",
          opacity: 1,
          zIndex: 1,
          transformStyle: "preserve-3d"
        }}
      >
        <div className="phone-screen" style={{ overflow: "hidden", display: "flex", flexDirection: "column" }}>
          {/* Notch */}
          <div className="phone-notch" />
          
          {/* Live Topbar */}
          <div className="phone-topbar" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", fontSize: "0.62rem", marginTop: "12px", borderBottom: "1px solid rgba(255,248,238,0.06)", paddingBottom: "8px" }}>
            <span>TrustLayer AI</span>
            <span className="live-dot" style={{ display: "flex", alignItems: "center", gap: "4px" }}>
              <span style={{
                display: "inline-block",
                width: "6px",
                height: "6px",
                borderRadius: "50%",
                background: step === 4 ? "var(--ember)" : "var(--signal)",
                boxShadow: step === 4 ? "0 0 8px var(--ember)" : "0 0 8px var(--signal)",
                animation: "pulse 1.5s infinite"
              }} />
              <TypewriterText text={getStatusText()} />
            </span>
          </div>

          {/* Active Scan Laser Line Sweep (Step 0 & 3) */}
          {(step === 0 || step === 3) && (
            <motion.div
              style={{
                position: "absolute",
                left: 0,
                right: 0,
                height: "4px",
                background: step === 3 ? "linear-gradient(90deg, transparent, var(--ember), transparent)" : "linear-gradient(90deg, transparent, var(--cyan), transparent)",
                boxShadow: step === 3 ? "0 0 15px var(--ember)" : "0 0 15px var(--cyan)",
                zIndex: 10,
                pointerEvents: "none"
              }}
              animate={{ top: ["5%", "92%", "5%"] }}
              transition={{ repeat: Infinity, duration: 2.2, ease: "easeInOut" }}
            />
          )}

          {/* Scanning Context receipt layout */}
          <div className="phone-receipt" style={{ display: "flex", flexDirection: "column", flexGrow: 1, position: "relative", gap: "10px", marginTop: "14px", padding: "12px", background: "rgba(255,248,238,0.02)" }}>
            <span className="phone-receipt-label" style={{ fontSize: "0.58rem", color: "var(--foreground-dim)", letterSpacing: "0.08em" }}>
              UPI VERIFICATION NODE
            </span>

            {/* Receipt Details with Highlights */}
            <div style={{ position: "relative", padding: "10px", borderRadius: "6px", border: "1px solid rgba(255,248,238,0.04)", background: "rgba(0,0,0,0.18)" }}>
              {/* Highlight Box for Amount (Step 1) */}
              {step >= 1 && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: [0, 1, 0.4, 1] }}
                  transition={{ duration: 0.6 }}
                  style={{
                    position: "absolute",
                    top: "34px",
                    left: "5px",
                    right: "5px",
                    bottom: "22px",
                    border: step >= 3 ? "1.5px solid var(--ember)" : "1.5px solid var(--signal)",
                    boxShadow: step >= 3 ? "0 0 8px rgba(255,77,46,0.3)" : "0 0 8px rgba(219,255,74,0.3)",
                    borderRadius: "4px",
                    pointerEvents: "none"
                  }}
                />
              )}

              <strong className="phone-receipt-title" style={{ fontSize: "0.78rem", color: "var(--foreground)", display: "block" }}>
                Ramesh Kirana Store
              </strong>
              <div className="phone-receipt-amount" style={{ fontSize: "1.5rem", fontWeight: 950, color: step >= 3 ? "var(--ember)" : "var(--foreground)", margin: "4px 0" }}>
                &#8377;4,500
              </div>
              <div className="phone-receipt-meta" style={{ display: "flex", justifyContent: "space-between", fontSize: "0.64rem", color: "var(--foreground-muted)" }}>
                <span>9876543210@ybl</span>
                <span>26 May, 1:23 PM</span>
              </div>
            </div>

            {/* Detailed Verification Fields (Sequential Reveal) */}
            <div style={{ display: "flex", flexDirection: "column", gap: "6px", fontSize: "0.68rem" }}>
              {/* Field 1: UPI ID */}
              <div style={{ display: "flex", justifyContent: "space-between", padding: "4px 0", borderBottom: "1px solid rgba(255,248,238,0.02)", position: "relative" }}>
                {step >= 2 && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    style={{ position: "absolute", left: -4, right: -4, top: 0, bottom: 0, border: "1px solid rgba(219,255,74,0.3)", background: "rgba(219,255,74,0.03)", borderRadius: "3px", pointerEvents: "none" }}
                  />
                )}
                <span style={{ color: "var(--foreground-dim)" }}>VPA Address</span>
                <strong style={{ color: step >= 2 ? "var(--signal)" : "var(--foreground-muted)" }}>9876543210@ybl</strong>
              </div>

              {/* Field 2: QR Scanner code payload anomaly (Step 3) */}
              <div style={{ display: "flex", justifyContent: "space-between", padding: "4px 0", borderBottom: "1px solid rgba(255,248,238,0.02)", position: "relative" }}>
                {step >= 3 && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    style={{ position: "absolute", left: -4, right: -4, top: 0, bottom: 0, border: "1px dashed var(--ember)", background: "rgba(255,77,46,0.04)", borderRadius: "3px", pointerEvents: "none" }}
                  />
                )}
                <span style={{ color: "var(--foreground-dim)" }}>Counter QR ID</span>
                <strong style={{ color: step >= 3 ? "var(--ember)" : "var(--foreground-muted)" }}>
                  {step >= 3 ? "rameshstore@okaxis" : "Verifying..."}
                </strong>
              </div>
            </div>

            {/* WhatsApp pressure tactic simulation (Step 3 and 4) */}
            <AnimatePresence>
              {step >= 3 && (
                <motion.div
                  initial={{ opacity: 0, y: 15 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  style={{
                    position: "absolute",
                    bottom: step === 4 ? "70px" : "12px",
                    left: "8px",
                    right: "8px",
                    background: "rgba(10,12,14,0.92)",
                    border: "1px solid rgba(255,77,46,0.24)",
                    borderRadius: "8px",
                    padding: "8px",
                    fontSize: "0.64rem",
                    display: "flex",
                    flexDirection: "column",
                    gap: "4px",
                    boxShadow: "0 8px 20px rgba(0,0,0,0.5)",
                    zIndex: 5
                  }}
                >
                  <div style={{ color: "var(--ember)", fontWeight: 800, fontSize: "0.58rem", textTransform: "uppercase", letterSpacing: "0.05em" }}>
                    ⚠️ WHATSAPP PRESSURE SEQUENCE DETECTED
                  </div>
                  <div style={{ background: "rgba(255,77,46,0.1)", borderRadius: "4px", padding: "4px 6px", width: "fit-content", alignSelf: "flex-start", border: "1px solid rgba(255,77,46,0.15)" }}>
                    Bhaiya payment ho gaya, server delay hai
                  </div>
                  <div style={{ background: "rgba(255,77,46,0.1)", borderRadius: "4px", padding: "4px 6px", width: "fit-content", alignSelf: "flex-start", border: "1px solid rgba(255,77,46,0.15)" }}>
                    Check counter once bro, trust me reflect will happen
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Progressive Floating Investigative Badges */}
            <div style={{ position: "absolute", top: "135px", right: "-12px", display: "flex", flexDirection: "column", gap: "6px", zIndex: 12, width: "130px" }}>
              <AnimatePresence>
                {step >= 1 && (
                  <motion.div
                    initial={{ opacity: 0, x: 25, scale: 0.8 }}
                    animate={{ opacity: 1, x: 0, scale: 1 }}
                    exit={{ opacity: 0, x: 10 }}
                    style={{
                      background: "rgba(10,10,9,0.9)",
                      border: "1px solid var(--signal)",
                      boxShadow: "0 4px 12px rgba(219,255,74,0.15)",
                      borderRadius: "6px",
                      padding: "5px 8px",
                      fontSize: "0.58rem",
                      fontWeight: 800,
                      color: "var(--signal)",
                      display: "flex",
                      alignItems: "center",
                      gap: "4px"
                    }}
                  >
                    <span>✔</span> ₹4,500 detected
                  </motion.div>
                )}
                {step >= 2 && (
                  <motion.div
                    initial={{ opacity: 0, x: 25, scale: 0.8 }}
                    animate={{ opacity: 1, x: 0, scale: 1 }}
                    exit={{ opacity: 0, x: 10 }}
                    style={{
                      background: "rgba(10,10,9,0.9)",
                      border: "1px solid var(--signal)",
                      boxShadow: "0 4px 12px rgba(219,255,74,0.15)",
                      borderRadius: "6px",
                      padding: "5px 8px",
                      fontSize: "0.58rem",
                      fontWeight: 800,
                      color: "var(--signal)",
                      display: "flex",
                      alignItems: "center",
                      gap: "4px"
                    }}
                  >
                    <span>✔</span> UPI ID verified
                  </motion.div>
                )}
                {step >= 3 && (
                  <motion.div
                    initial={{ opacity: 0, x: 25, scale: 0.8 }}
                    animate={{ opacity: 1, x: 0, scale: 1 }}
                    exit={{ opacity: 0, x: 10 }}
                    style={{
                      background: "rgba(20,5,5,0.92)",
                      border: "1px solid var(--ember)",
                      boxShadow: "0 4px 12px rgba(255,77,46,0.25)",
                      borderRadius: "6px",
                      padding: "5px 8px",
                      fontSize: "0.58rem",
                      fontWeight: 800,
                      color: "#ffb59d",
                      display: "flex",
                      alignItems: "center",
                      gap: "4px"
                    }}
                  >
                    <span>✖</span> QR mismatched
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* Step 4: Final Trust Score Escalation Circle */}
            <AnimatePresence>
              {step === 4 && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0 }}
                  style={{
                    position: "absolute",
                    inset: 0,
                    background: "rgba(5,5,5,0.94)",
                    borderRadius: "8px",
                    display: "flex",
                    flexDirection: "column",
                    justifyContent: "center",
                    alignItems: "center",
                    padding: "16px",
                    textAlign: "center",
                    border: "1.5px solid var(--ember)",
                    boxShadow: "inset 0 0 20px rgba(255,77,46,0.2), 0 0 30px rgba(255,77,46,0.15)",
                    zIndex: 8
                  }}
                >
                  <div style={{ position: "relative", width: "90px", height: "90px", display: "grid", placeItems: "center" }}>
                    <svg viewBox="0 0 100 100" style={{ width: "100%", height: "100%", transform: "rotate(-90deg)" }}>
                      <circle cx="50" cy="50" r="42" fill="none" stroke="rgba(255,77,46,0.1)" strokeWidth="8" />
                      <motion.circle
                        cx="50"
                        cy="50"
                        r="42"
                        fill="none"
                        stroke="var(--ember)"
                        strokeWidth="8"
                        strokeDasharray={263.8}
                        animate={{ strokeDashoffset: 263.8 - (263.8 * trustScore) / 100 }}
                        transition={{ duration: 1.2, ease: "easeOut" }}
                      />
                    </svg>
                    <div style={{ position: "absolute", fontSize: "1.5rem", fontWeight: 950, color: "var(--ember)" }}>
                      {trustScore}%
                    </div>
                  </div>
                  
                  <div style={{ marginTop: "12px", fontSize: "0.58rem", color: "var(--foreground-dim)", fontWeight: 800, letterSpacing: "0.08em" }}>
                    FINAL AUTHENTICITY SCORE
                  </div>

                  <motion.div
                    animate={{ scale: [1, 1.05, 1] }}
                    transition={{ repeat: Infinity, duration: 1.6 }}
                    style={{
                      marginTop: "10px",
                      background: "rgba(255,77,46,0.15)",
                      border: "1.5px solid var(--ember)",
                      borderRadius: "999px",
                      padding: "6px 14px",
                      fontSize: "0.64rem",
                      fontWeight: 900,
                      color: "#ffb59d",
                      letterSpacing: "0.04em",
                      textTransform: "uppercase"
                    }}
                  >
                    VERDICT: LIKELY FAKE
                  </motion.div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Phone Footer Scan mode banner */}
          <div className="phone-row forensic-footer" style={{ borderTop: "1px solid rgba(255,248,238,0.06)", paddingTop: "8px", marginTop: "auto", display: "flex", justifyContent: "space-between", alignItems: "center", fontSize: "0.58rem" }}>
            <span>UPI SECURE FORENSICS</span>
            <strong style={{ color: step === 4 ? "var(--ember)" : "var(--signal)", letterSpacing: "0.04em" }}>
              {step === 4 ? "THREAD DETECTED" : "SCANNING ACTIVE"}
            </strong>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
