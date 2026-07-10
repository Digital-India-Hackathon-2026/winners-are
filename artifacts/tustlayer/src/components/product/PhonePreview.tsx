"use client";

type PhonePreviewProps = {
  uploadedImage: string | null;
  isScanning?: boolean;
};

export function PhonePreview({ uploadedImage, isScanning }: PhonePreviewProps) {
  return (
    <div className="preview-panel">
      <div className="product-panel-header" style={{ width: "100%", justifyContent: "center", borderBottom: "none", opacity: 0.6 }}>
        <span className="dot" /> Live Preview
      </div>
      
      <div className="preview-phone-wrap">
        <div className="preview-phone-glow" />
        <div className="phone-shell" style={{ visibility: "visible", opacity: 1 }}>
          <div className="phone-screen">
            <div className="phone-notch" />
            <div className="phone-topbar">
              <span>TrustLayer AI</span>
              <span className="live-dot">● LIVE</span>
            </div>
            
            {uploadedImage ? (
              <div style={{ position: "relative", width: "100%", height: "85%", marginTop: "10px", overflow: "hidden", borderRadius: "8px" }}>
                {uploadedImage === "pdf-placeholder" ? (
                  <div style={{
                    width: "100%",
                    height: "100%",
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    justifyContent: "center",
                    background: "rgba(255, 255, 255, 0.02)",
                    border: "1px dashed var(--border)",
                    borderRadius: "8px",
                    padding: "20px"
                  }}>
                    <span style={{ fontSize: "3.5rem" }}>📄</span>
                    <span style={{ fontSize: "0.85rem", color: "var(--foreground-muted)", marginTop: "12px", fontWeight: "bold", textAlign: "center" }}>
                      Document Active
                    </span>
                    <span style={{ fontSize: "0.68rem", color: "var(--foreground-dim)", marginTop: "4px", textAlign: "center" }}>
                      PDF Security Forensic Ready
                    </span>
                  </div>
                ) : (
                  <img 
                    src={uploadedImage} 
                    alt="Preview" 
                    style={{ width: "100%", height: "100%", objectFit: "contain" }} 
                  />
                )}
                {isScanning && (
                  <>
                    <div className="scanning-laser-line" />
                    <div style={{
                      position: "absolute",
                      inset: 0,
                      background: "linear-gradient(to bottom, rgba(219, 255, 74, 0.04), rgba(219, 255, 74, 0.12))",
                      mixBlendMode: "overlay",
                      animation: "pulseScan 2s infinite alternate"
                    }} />
                  </>
                )}
              </div>
            ) : (
              <div className="phone-receipt">
                <span className="phone-receipt-label">Sample Proof</span>
                <strong className="phone-receipt-title">Ramesh Kirana Store</strong>
                <div className="phone-receipt-amount">&#8377;4,500</div>
                <div className="phone-receipt-meta">
                  <span>9876543210@ybl</span>
                  <span>26 May</span>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
