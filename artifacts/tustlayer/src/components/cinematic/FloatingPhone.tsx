import { RefObject } from "react";

type FloatingPhoneProps = {
  phoneRef: RefObject<HTMLDivElement | null>;
  screenRef: RefObject<HTMLDivElement | null>;
  uploadedImage: null | string;
};

const verificationRows = [
  ["UPI ID", "9876543210@ybl"],
  ["Payment app", "Google Pay"],
  ["QR payload", "MISMATCH"],
  ["Bank SMS", "MISSING"],
];

export function FloatingPhone({
  phoneRef,
  screenRef,
  uploadedImage,
}: FloatingPhoneProps) {
  return (
    <div ref={phoneRef} className="phone-shell" aria-hidden="true">
      <div className="phone-depth phone-depth-a" />
      <div className="phone-depth phone-depth-b" />
      <div ref={screenRef} className="phone-screen">
        <div className="phone-sensor" />
        <div className="phone-row phone-topline">
          <span>TrustLayer AI</span>
          <span>LIVE</span>
        </div>
        <div className="phone-row receipt-card">
          <span className="receipt-label">UPI screenshot intelligence</span>
          <strong>Payment proof sent on WhatsApp</strong>
          <div className="receipt-amount">&#8377;4,500</div>
          <div className="receipt-meta">
            <span>Ramesh Kirana Store</span>
            <span>26 May, 1:23 PM</span>
          </div>
          <div className="phone-screenshot scan-layer">
            <div className="uploaded-shot-wrap">
              <div
                className={`uploaded-shot ${uploadedImage ? "has-upload" : ""}`}
                style={
                  uploadedImage
                    ? { backgroundImage: `url(${uploadedImage})` }
                    : undefined
                }
              />
              <span>{uploadedImage ? "Uploaded payment proof" : "Sample proof"}</span>
            </div>
            <div className="upi-app-row">
              <span className="upi-app-pill gpay">Google Pay</span>
              <span className="upi-app-pill phonepe">PhonePe</span>
              <span className="upi-app-pill paytm">Paytm</span>
            </div>
            <div className="screenshot-status">Payment successful</div>
            <div className="screenshot-bank">Paid to Ramesh Kirana Store</div>
            <div className="screenshot-amount">&#8377;4,500</div>
            <div className="screenshot-line" />
            <div className="screenshot-field">
              <span>UPI ID</span>
              <strong>9876543210@ybl</strong>
            </div>
            <div className="screenshot-field">
              <span>Paid from</span>
              <strong>Arjun Mehta | HDFC Bank</strong>
            </div>
            <div className="screenshot-field suspicious-text">
              <span>Timestamp</span>
              <strong>26 May, 1:23 PM</strong>
            </div>
            <div className="upi-qr-proof">
              <span className="qr-code">
                {Array.from({ length: 25 }).map((_, index) => (
                  <i key={index} />
                ))}
              </span>
              <div>
                <span>QR scanned at counter</span>
                <strong>rameshkirana@okaxis</strong>
              </div>
            </div>
          </div>
          <div className="ocr-overlay scan-layer">
            <span className="ocr-box ocr-amount" />
            <span className="ocr-box ocr-receiver" />
            <span className="ocr-box ocr-id" />
            <span className="ocr-box ocr-time" />
            <span className="ocr-box ocr-qr" />
            <span className="suspicion-highlight suspicion-time" />
            <span className="suspicion-highlight suspicion-id" />
          </div>
        </div>
        <div className="phone-row proof-strip">
          <span />
          <span />
          <span />
          <span />
          <span />
        </div>
        <div className="phone-row scan-card">
          <div>
            <span>Payment authenticity</span>
            <strong>41%</strong>
          </div>
          <div className="scan-ring">
            <span />
          </div>
        </div>
        <div className="phone-row verification-list">
          {verificationRows.map(([label, status]) => (
            <div key={label}>
              <span>{label}</span>
              <strong>{status}</strong>
            </div>
          ))}
        </div>
        <div className="phone-row forensic-footer">
          <span>UPI fraud patterns</span>
          <strong>3 signals</strong>
        </div>
        <div className="whatsapp-thread scan-layer">
          <div className="wa-bubble incoming">Check once bro</div>
          <div className="wa-bubble incoming">Server delay hai</div>
          <div className="wa-bubble outgoing">Amount not received</div>
          <div className="wa-bubble incoming danger">Money will reflect</div>
        </div>
        <div className="scan-mode scan-layer">
          <span>SCAN MODE</span>
          <strong>ACTIVE</strong>
        </div>
      </div>
    </div>
  );
}
