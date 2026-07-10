"use client";

import { motion } from "framer-motion";

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
          47%
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
          3.2 Lakh
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
              className="scam-card reveal-up"
              whileHover={{
                y: -6,
                borderColor: card.borderColor,
                boxShadow: `0 18px 45px rgba(0,0,0,0.4), 0 0 25px ${card.badgeColor}`,
              }}
              transition={{ type: "tween", ease: "easeOut", duration: 0.25 }}
              style={{
                position: "relative",
                display: "flex",
                flexDirection: "column",
                overflow: "hidden"
              }}
            >
              {/* Evidence header / Tag */}
              <div
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
                <span>{card.exhibit}</span>
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
