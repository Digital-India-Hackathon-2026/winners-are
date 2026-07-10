"use client";

export function WhatsappSection() {
  return (
    <section className="tl-section whatsapp-section">
      <div className="tl-section-inner" style={{ display: "flex", flexDirection: "column", gap: "2rem", alignItems: "center", textAlign: "center" }}>
        <div className="verdict-header reveal-up">
          <span className="section-tag" style={{ background: "var(--signal-glow)", color: "var(--signal)", border: "1px solid var(--signal)" }}>BETA FEATURE</span>
          <h2>Scan Directly From WhatsApp</h2>
          <p style={{ color: "var(--foreground-dim)", maxWidth: "600px", margin: "1rem auto", lineHeight: 1.6 }}>
            A kirana store owner is not opening a web app. Forward the screenshot to TrustLayer's WhatsApp Business number and get the full verdict in 10 seconds — without leaving the app where the fake screenshot was sent.
          </p>
        </div>

        <div className="whatsapp-mockup reveal-up" style={{
          background: "var(--bg-elevated)",
          border: "1px solid var(--border)",
          padding: "1.5rem",
          borderRadius: "16px",
          textAlign: "left",
          maxWidth: "400px",
          width: "100%",
          boxShadow: "0 10px 30px rgba(var(--shadow-rgb), 0.15)",
          position: "relative",
          overflow: "hidden"
        }}>
          <div style={{
            fontSize: "0.85rem",
            fontFamily: "var(--font-mono)",
            background: "rgba(var(--shadow-rgb), 0.05)",
            padding: "1rem",
            borderRadius: "8px",
            border: "1px solid var(--border)",
            color: "var(--foreground)"
          }}>
            <strong style={{ color: "var(--foreground)" }}>TrustLayer AI</strong><br/>
            ━━━━━━━━━━━━━━━━━<br/>
            Trust Score: 18 / 100<br/>
            <span style={{ color: "var(--ember)" }}>🚨 HIGH RISK — Likely Fake</span><br/><br/>
            • UTR has 8 digits, must be 12<br/>
            • Header color doesn't match PhonePe<br/>
            • Edited in Canva 2.0 (EXIF)<br/>
            • Screenshot flagged 3× before<br/><br/>
            ⛔ Do NOT release goods<br/>
            📞 Call 1930 if pressured<br/>
            ━━━━━━━━━━━━━━━━━
          </div>
        </div>
        <p style={{ color: "var(--foreground-muted)", fontSize: "0.85rem", marginTop: "1rem" }}>This is India-scale distribution. Zero app download. Zero learning curve.</p>
      </div>
    </section>
  );
}
