"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { QRCodeSVG } from "qrcode.react";

const WA_LINK = "https://wa.me/14155238886?text=join%20choose-factory";
const WA_NUMBER = "+1 415 523 8886";
const WA_CODE = "join choose-factory";

function CopyButton({ text, label }: { text: string; label: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback
      const ta = document.createElement("textarea");
      ta.value = text;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand("copy");
      document.body.removeChild(ta);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <button
      onClick={handleCopy}
      className="wa-copy-btn"
      aria-label={`Copy ${label}`}
      title={`Copy ${label}`}
    >
      {copied ? (
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--signal)" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="20 6 9 17 4 12" />
        </svg>
      ) : (
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
          <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1" />
        </svg>
      )}
    </button>
  );
}

const steps = [
  {
    num: "01",
    title: "Open WhatsApp",
    desc: (
      <>
        Tap the button below or scan the QR code to open WhatsApp with TrustLayer&apos;s verification bot.
      </>
    ),
  },
  {
    num: "02",
    title: "Send the activation code",
    desc: (
      <span style={{ display: "flex", alignItems: "center", gap: "6px", flexWrap: "wrap" }}>
        Send{" "}
        <code className="wa-code-inline">{WA_CODE}</code>
        <CopyButton text={WA_CODE} label="activation code" />
        {" "}to connect your number.
      </span>
    ),
  },
  {
    num: "03",
    title: "Forward & get verdicts",
    desc: "Forward any payment screenshot. Get a forensic fraud verdict in under 10 seconds — right inside the chat.",
  },
];

export function WhatsappScanSection() {
  return (
    <section id="whatsapp-scan" className="tl-section wa-scan-section">
      <div className="tl-section-inner">
        {/* Header */}
        <div className="wa-scan-header reveal-up">
          <div style={{ display: "flex", alignItems: "center", gap: "12px", justifyContent: "center", flexWrap: "wrap" }}>
            <span
              className="section-tag"
              style={{
                background: "rgba(37, 211, 102, 0.08)",
                color: "#25d366",
                border: "1px solid rgba(37, 211, 102, 0.3)",
              }}
            >
              WhatsApp Integration
            </span>
            <span className="wa-live-pill">
              <span className="wa-live-dot" />
              LIVE
            </span>
          </div>
          <h2>
            No app. No download.
            <br />
            <span style={{ color: "#25d366" }}>Just WhatsApp.</span>
          </h2>
          <p>
            A kirana store owner won&apos;t open a web app mid-transaction. Forward the screenshot to TrustLayer&apos;s WhatsApp number — get a full forensic verdict in 10 seconds without leaving the chat.
          </p>
        </div>

        {/* Two-column layout */}
        <div className="wa-scan-grid reveal-up">
          {/* Left: Steps */}
          <div className="wa-scan-steps">
            {steps.map((step, idx) => (
              <motion.div
                key={step.num}
                className="wa-step-card"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-40px" }}
                transition={{ delay: idx * 0.12, duration: 0.5, ease: "easeOut" }}
              >
                <span className="wa-step-num">{step.num}</span>
                <div>
                  <strong className="wa-step-title">{step.title}</strong>
                  <div className="wa-step-desc">{step.desc}</div>
                </div>
              </motion.div>
            ))}

            {/* Phone number line */}
            <div className="wa-number-line">
              <span style={{ color: "var(--foreground-dim)", fontSize: "0.72rem", fontFamily: "var(--font-mono)", letterSpacing: "0.04em" }}>
                BOT NUMBER
              </span>
              <span style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                <code className="wa-code-inline" style={{ fontSize: "0.88rem" }}>{WA_NUMBER}</code>
                <CopyButton text="+14155238886" label="phone number" />
              </span>
            </div>

            {/* CTA */}
            <motion.a
              href={WA_LINK}
              target="_blank"
              rel="noopener noreferrer"
              className="btn-primary"
              style={{ marginTop: "8px", display: "inline-flex", gap: "10px", width: "fit-content" }}
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.97 }}
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z" />
              </svg>
              Open WhatsApp
            </motion.a>
          </div>

          {/* Divider */}
          <div className="wa-scan-divider">
            <div className="wa-scan-divider-line" />
            <span className="wa-scan-divider-or">OR</span>
            <div className="wa-scan-divider-line" />
          </div>

          {/* Right: QR */}
          <motion.div
            className="wa-scan-qr-card"
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true, margin: "-40px" }}
            transition={{ duration: 0.5, ease: "easeOut" }}
          >
            <span className="wa-qr-label">SCAN TO CONNECT</span>
            <div className="wa-qr-wrap">
              <QRCodeSVG
                value={WA_LINK}
                size={180}
                bgColor="transparent"
                fgColor="#dbff4a"
                level="M"
                style={{ width: "100%", height: "auto", maxWidth: "180px" }}
              />
            </div>
            <span className="wa-qr-sublabel">
              Point your phone camera at the QR code to open WhatsApp instantly.
            </span>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
