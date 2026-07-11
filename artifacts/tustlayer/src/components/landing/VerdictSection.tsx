"use client";

import { motion, useInView } from "framer-motion";
import { useRef, useEffect, useState } from "react";

export function VerdictSection() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const ringRef = useRef<HTMLDivElement>(null);
  const isRingInView = useInView(ringRef, { once: true, margin: "-100px" });

  const [score, setScore] = useState(100);

  useEffect(() => {
    if (!isRingInView) return;
    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (prefersReducedMotion) {
      setScore(26);
      return;
    }

    let start = 100;
    const end = 26;
    const duration = 1200; // ms
    const stepTime = 16;
    const stepsCount = duration / stepTime;
    const decrement = (start - end) / stepsCount;

    const timer = setInterval(() => {
      start -= decrement;
      if (start <= end) {
        setScore(end);
        clearInterval(timer);
      } else {
        setScore(Math.floor(start));
      }
    }, stepTime);
    return () => clearInterval(timer);
  }, [isRingInView]);

  const getScoreColor = (val: number) => {
    if (val > 70) return "var(--success)"; // Green
    if (val > 40) return "var(--warn)";    // Amber
    return "var(--ember)";                 // Red
  };

  return (
    <section ref={sectionRef} className="tl-section verdict-section">
      <div className="tl-section-inner">
        <div className="verdict-header reveal-up">
          <span className="section-tag">Trust Engine</span>
          <h2>The Verdict Is Instant</h2>
        </div>

        <div className="verdict-layout">
          <div className="verdict-score-card reveal-left">
            <div ref={ringRef} className="verdict-score-ring">
              <svg viewBox="0 0 180 180">
                <circle className="ring-bg" cx="90" cy="90" r="80" />
                <motion.circle
                  className="ring-fill"
                  cx="90"
                  cy="90"
                  r="80"
                  animate={{
                    strokeDashoffset: 502 - (502 * score) / 100,
                    stroke: getScoreColor(score)
                  }}
                  transition={{ duration: 0.1 }}
                  style={{
                    fill: "none",
                    strokeWidth: 10,
                    strokeLinecap: "round",
                    strokeDasharray: 502,
                  }}
                />
              </svg>
              <div 
                className="verdict-score-number"
                style={{ color: getScoreColor(score), transition: "color 0.2s ease" }}
              >
                {score}
              </div>
            </div>
            <div className="verdict-score-label">Authenticity Score</div>
            <div className="verdict-pill">
              <span>Verdict</span>
              <strong>Likely Fake Proof</strong>
            </div>
          </div>

          <div className="verdict-details reveal-right">
            <div className="verdict-detail-card">
              <h4>AI Reasoning</h4>
              <p>Known scam template pattern detected. QR payload mismatch with claimed UPI ID. WhatsApp pressure messaging flow identified.</p>
            </div>
            <div className="verdict-detail-card">
              <h4>Recommended Actions</h4>
              <p>Do not release goods. Request live bank transfer verification. Report to cyber crime portal.</p>
            </div>
            <div className="verdict-detail-card">
              <h4>Trust Breakdown</h4>
              <div className="verdict-trust-bar">
                <span style={{ transition: "background 0.5s ease 0.4s" }} />
                <span style={{ transition: "background 0.5s ease 0.6s" }} />
                <span style={{ transition: "background 0.5s ease 0.8s" }} />
                <span style={{ transition: "background 0.5s ease 1.0s" }} />
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
