"use client";

export function VerdictSection() {
  return (
    <section className="tl-section verdict-section">
      <div className="tl-section-inner">
        <div className="verdict-header reveal-up">
          <span className="section-tag">Trust Engine</span>
          <h2>The Verdict Is Instant</h2>
        </div>

        <div className="verdict-layout">
          <div className="verdict-score-card reveal-left">
            <div className="verdict-score-ring">
              <svg viewBox="0 0 180 180">
                <circle className="ring-bg" cx="90" cy="90" r="80" />
                <circle
                  className="ring-fill"
                  cx="90"
                  cy="90"
                  r="80"
                  style={{ strokeDashoffset: 502 - (502 * 26) / 100 }}
                />
              </svg>
              <div className="verdict-score-number">26</div>
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
                <span />
                <span />
                <span />
                <span />
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
