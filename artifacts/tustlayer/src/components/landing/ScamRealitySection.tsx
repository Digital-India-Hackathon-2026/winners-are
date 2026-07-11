"use client";

import { motion, useInView } from "framer-motion";
import { useRef, useEffect, useState } from "react";

function CountUp({ value, suffix = "" }: { value: number; suffix?: string }) {
  const [count, setCount] = useState(0);
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-50px" });

  useEffect(() => {
    if (!isInView) return;
    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (prefersReducedMotion) {
      setCount(value);
      return;
    }

    let start = 0;
    const end = value;
    const duration = 1200; // ms
    const increment = end / (duration / 16);
    const timer = setInterval(() => {
      start += increment;
      if (start >= end) {
        setCount(end);
        clearInterval(timer);
      } else {
        setCount(Math.floor(start));
      }
    }, 16);
    return () => clearInterval(timer);
  }, [isInView, value]);

  return <span ref={ref}>{count}{suffix}</span>;
}

function CountUpDecimal({ value, decimals = 1, suffix = "" }: { value: number; decimals?: number; suffix?: string }) {
  const [count, setCount] = useState(0);
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-50px" });

  useEffect(() => {
    if (!isInView) return;
    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (prefersReducedMotion) {
      setCount(value);
      return;
    }

    let start = 0;
    const end = value;
    const duration = 1200; // ms
    const increment = end / (duration / 16);
    const timer = setInterval(() => {
      start += increment;
      if (start >= end) {
        setCount(end);
        clearInterval(timer);
      } else {
        setCount(Number(start.toFixed(decimals)));
      }
    }, 16);
    return () => clearInterval(timer);
  }, [isInView, value, decimals]);

  return <span ref={ref}>{count.toFixed(decimals)}{suffix}</span>;
}

const evidenceCards = [
  {
    id: "01",
    exhibit: "EXHIBIT #WA-209",
    status: "EXPLOITED",
    title: "WhatsApp Screenshot Fraud",
    desc: "Shopkeepers are shown cloned payment screens via chat conversations, using high-pressure urgency patterns.",
    badgeColor: "rgba(255, 77, 46, 0.4)",
    borderColor: "rgba(255, 77, 46, 0.3)",
    element: (
      <motion.div
        animate={{ y: [0, -4, 0] }}
        transition={{ repeat: Infinity, duration: 3.2, ease: "easeInOut" }}
        className="wa-bubble-demo"
        style={{
          marginTop: "16px",
          background: "linear-gradient(135deg, #0f4f46, #073831)",
          borderLeft: "3px solid #25d366",
          padding: "10px 14px",
          borderRadius: "10px",
          fontSize: "0.78rem"
        }}
      >
        <span style={{ fontSize: "0.58rem", color: "#25d366", display: "block", marginBottom: "4px", fontWeight: 800 }}>
          CHAT EVIDENCE // RECEIVED
        </span>
        Bhaiya payment ho gaya, server delay hai. Goods release immediately.
      </motion.div>
    )
  },
  {
    id: "02",
    exhibit: "EXHIBIT #QR-942",
    status: "HIGH RISK",
    title: "QR Code Manipulation",
    desc: "Scanned QR codes resolve to a completely different malicious UPI ID than the one printed on the physical standee.",
    badgeColor: "rgba(52, 230, 255, 0.4)",
    borderColor: "rgba(52, 230, 255, 0.3)",
    element: (
      <div className="scam-stat" style={{ borderTop: "1px solid rgba(255,248,238,0.06)", marginTop: "16px", paddingTop: "14px" }}>
        <motion.strong
          animate={{ scale: [1, 1.05, 1], textShadow: ["0 0 4px rgba(52,230,255,0)", "0 0 10px rgba(52,230,255,0.6)", "0 0 4px rgba(52,230,255,0)"] }}
          transition={{ repeat: Infinity, duration: 2.5 }}
          style={{ color: "var(--cyan)", fontSize: "1.8rem", fontWeight: 950 }}
        >
          <CountUp value={47} suffix="%" />
        </motion.strong>
        <span style={{ fontSize: "0.72rem", color: "var(--foreground-muted)", marginLeft: "8px" }}>
          of retail UPI fraud cases involve physical sticker QR swapping
        </span>
      </div>
    )
  },
  {
    id: "03",
    exhibit: "EXHIBIT #UI-112",
    status: "CLONED",
    title: "Fake App Interfaces",
    desc: "Cloned payment application packages (APKs) that perfectly simulate successful transaction animations and sound cues.",
    badgeColor: "rgba(219, 255, 74, 0.4)",
    borderColor: "rgba(219, 255, 74, 0.3)",
    element: (
      <div className="scam-stat" style={{ borderTop: "1px solid rgba(255,248,238,0.06)", marginTop: "16px", paddingTop: "14px" }}>
        <motion.strong
          animate={{ opacity: [0.7, 1, 0.7] }}
          transition={{ repeat: Infinity, duration: 1.8 }}
          style={{ color: "var(--signal)", fontSize: "1.8rem", fontWeight: 950 }}
        >
          <CountUpDecimal value={3.2} decimals={1} suffix=" Lakh" />
        </motion.strong>
        <span style={{ fontSize: "0.72rem", color: "var(--foreground-muted)", marginLeft: "8px" }}>
          reported fake-wallet instances recorded annually across India
        </span>
      </div>
    )
  },
  {
    id: "04",
    exhibit: "EXHIBIT #PT-008",
    status: "ACTIVE",
    title: "Social Pressure Tactics",
    desc: "Intentional signal jamming at counters or distraction methods to pressure operators into bypassing live bank verification.",
    badgeColor: "rgba(255, 77, 46, 0.4)",
    borderColor: "rgba(255, 77, 46, 0.3)",
    element: (
      <motion.div
        animate={{ y: [0, 4, 0] }}
        transition={{ repeat: Infinity, duration: 3.2, ease: "easeInOut", delay: 0.5 }}
        className="wa-bubble-demo"
        style={{
          marginTop: "16px",
          background: "rgba(255, 77, 46, 0.04)",
          border: "1px solid rgba(255, 77, 46, 0.25)",
          padding: "10px 14px",
          borderRadius: "10px",
          fontSize: "0.78rem",
          color: "rgba(255, 248, 238, 0.7)"
        }}
      >
        <span style={{ fontSize: "0.58rem", color: "var(--ember)", display: "block", marginBottom: "4px", fontWeight: 800 }}>
          TACTICAL ANOMALY // REGISTERED
        </span>
        &quot;Look bhaiya, message will come soon. I am running late. Let me go.&quot;
      </motion.div>
    )
  }
];

export function ScamRealitySection() {
  return (
    <section id="scam-reality" className="tl-section scam-section">
      <div className="tl-section-inner">
        <div className="scam-header reveal-up">
          <span className="section-tag">The Problem</span>
          <h2>India&apos;s &#8377;14,000 Cr UPI Fraud Crisis</h2>
          <p>
            UPI screenshot and interface manipulation is a sophisticated counter exploit. Shopkeepers face cloned systems, altered QR payloads, and active pressure flows daily.
          </p>
        </div>

        <div className="scam-grid">
          {evidenceCards.map((card, idx) => (
            <motion.div
              key={card.id}
              className="scam-card"
              initial={{ opacity: 0, y: 35 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-40px" }}
              whileHover={{
                y: -8,
                scale: 1.02,
                borderColor: "var(--ember)",
                boxShadow: "0 22px 52px rgba(0,0,0,0.48), 0 0 25px var(--ember-glow)",
              }}
              transition={{
                layout: { duration: 0.2 },
                default: { type: "spring", stiffness: 100, damping: 15 },
                opacity: { duration: 0.5, delay: idx * 0.12 },
                y: { duration: 0.5, delay: idx * 0.12 }
              }}
              style={{
                position: "relative",
                display: "flex",
                flexDirection: "column",
                overflow: "hidden"
              }}
            >
              {/* Evidence header / Tag */}
              <div
                className="scam-card-header"
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  fontSize: "0.58rem",
                  fontFamily: "var(--font-mono)",
                  color: "var(--foreground-dim)",
                  letterSpacing: "0.1em",
                  marginBottom: "14px",
                  paddingBottom: "8px",
                  borderBottom: "1px solid rgba(255,248,238,0.04)"
                }}
              >
                <span className="exhibit-tag" style={{ transition: "color 0.25s ease, opacity 0.25s ease" }}>
                  {card.exhibit}
                </span>
                <span
                  style={{
                    color: card.status === "EXPLOITED" || card.status === "HIGH RISK" ? "var(--ember)" : "var(--cyan)",
                    fontWeight: 900,
                    display: "flex",
                    alignItems: "center",
                    gap: "4px"
                  }}
                >
                  <span style={{
                    display: "inline-block",
                    width: "4px",
                    height: "4px",
                    borderRadius: "50%",
                    background: "currentColor",
                    animation: "pulse 1s infinite"
                  }} />
                  {card.status}
                </span>
              </div>

              {/* Title & Description */}
              <h3 style={{ fontSize: "1.15rem", fontWeight: 850 }}>{card.title}</h3>
              <p style={{ flexGrow: 1, minHeight: "68px" }}>{card.desc}</p>

              {/* Interactive micro-element */}
              {card.element}

              {/* Subtle background scanner layout graphics */}
              <div
                style={{
                  position: "absolute",
                  bottom: -15,
                  right: -10,
                  opacity: 0.03,
                  pointerEvents: "none",
                  fontSize: "4rem",
                  fontWeight: 900
                }}
              >
                {card.id}
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
