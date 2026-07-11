"use client";

import { useRef, DragEvent, ChangeEvent, useState } from "react";

type PhonePreviewProps = {
  uploadedImage: string | null;
  uploadedName: string;
  isScanning: boolean;
  onFileSelect: (file: File) => void;
  onScan: () => void;
  onLoadDemo: () => void;
  onClear: () => void;
  errorMsg: string | null;
  activeTab: "file" | "message";
  setActiveTab: (tab: "file" | "message") => void;
  messageText: string;
  setMessageText: (txt: string) => void;
  onMessageScan: () => void;
};

export function PhonePreview({
  uploadedImage,
  uploadedName,
  isScanning,
  onFileSelect,
  onScan,
  onLoadDemo,
  onClear,
  errorMsg,
  activeTab,
  setActiveTab,
  messageText,
  setMessageText,
  onMessageScan,
}: PhonePreviewProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file && (file.type.startsWith("image/") || file.type === "application/pdf")) {
      onFileSelect(file);
    }
  };

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && (file.type.startsWith("image/") || file.type === "application/pdf")) {
      onFileSelect(file);
    }
  };

  return (
    <div className="preview-panel">
      <div className="preview-phone-wrap">
        <div className="preview-phone-glow" />
        <div className="product-phone-shell">
          <div className="product-phone-screen">
            <div className="phone-notch" />
            <div className="product-phone-topbar">
              <span>TrustLayer AI Scanner</span>
              <span className="live-dot">● ONLINE</span>
            </div>

            {/* Cinematic Selection Tabs */}
            <div style={{
              display: "flex",
              background: "rgba(255, 255, 255, 0.03)",
              borderBottom: "1px solid rgba(255,255,255,0.06)",
              padding: "4px"
            }}>
              <button
                onClick={() => setActiveTab("file")}
                style={{
                  flex: 1,
                  background: activeTab === "file" ? "rgba(219, 255, 74, 0.08)" : "transparent",
                  border: "none",
                  color: activeTab === "file" ? "var(--signal)" : "var(--foreground-dim)",
                  padding: "8px",
                  fontSize: "0.72rem",
                  fontWeight: 800,
                  borderRadius: "8px",
                  cursor: "pointer",
                  transition: "all 0.2s"
                }}
              >
                📂 Media Scanner
              </button>
              <button
                onClick={() => setActiveTab("message")}
                style={{
                  flex: 1,
                  background: activeTab === "message" ? "rgba(219, 255, 74, 0.08)" : "transparent",
                  border: "none",
                  color: activeTab === "message" ? "var(--signal)" : "var(--foreground-dim)",
                  padding: "8px",
                  fontSize: "0.72rem",
                  fontWeight: 800,
                  borderRadius: "8px",
                  cursor: "pointer",
                  transition: "all 0.2s"
                }}
              >
                💬 Message Scanner
              </button>
            </div>
            
            {activeTab === "file" ? (
              uploadedImage ? (
                /* Active Upload / Preview State inside the Phone screen */
                <div style={{ position: "relative", width: "100%", flexGrow: 1, display: "flex", flexDirection: "column", padding: "10px 14px 10px", minHeight: 0 }}>
                  <div style={{ position: "relative", flexGrow: 1, height: 0, minHeight: 0, overflow: "hidden", borderRadius: "12px", background: "rgba(0,0,0,0.35)", border: "1px solid var(--border)", display: "flex", alignItems: "center", justifyContent: "center" }}>
                    {uploadedImage === "pdf-placeholder" ? (
                      <div style={{
                        display: "flex",
                        flexDirection: "column",
                        alignItems: "center",
                        justifyContent: "center",
                        padding: "20px",
                        textAlign: "center"
                      }}>
                        <span style={{ fontSize: "3rem" }}>📄</span>
                        <span style={{ fontSize: "0.8rem", color: "var(--foreground-muted)", marginTop: "12px", fontWeight: "bold", wordBreak: "break-all" }}>
                          {uploadedName}
                        </span>
                        <span style={{ fontSize: "0.64rem", color: "var(--foreground-dim)", marginTop: "4px" }}>
                          PDF Security Forensic Ready
                        </span>
                      </div>
                    ) : (
                      <img 
                        src={uploadedImage} 
                        alt="Uploaded proof" 
                        style={{ maxWidth: "100%", maxHeight: "100%", objectFit: "contain" }} 
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
                        <div style={{
                          position: "absolute",
                          bottom: "20px",
                          left: "50%",
                          transform: "translateX(-50%)",
                          background: "rgba(10, 10, 9, 0.88)",
                          border: "1px solid var(--signal)",
                          borderRadius: "20px",
                          padding: "6px 14px",
                          color: "var(--signal)",
                          fontSize: "0.68rem",
                          fontFamily: "var(--font-mono)",
                          fontWeight: 900,
                          letterSpacing: "0.06em",
                          boxShadow: "0 0 12px rgba(219, 255, 74, 0.3)",
                          display: "flex",
                          alignItems: "center",
                          gap: "6px",
                          zIndex: 20
                        }}>
                          <span className="wa-live-dot" style={{ width: "6px", height: "6px", background: "var(--signal)", boxShadow: "0 0 6px var(--signal)" }} />
                          ANALYZING PIXELS
                        </div>
                      </>
                    )}
                  </div>

                  {/* Scan & Clear action button triggers aligned inside the phone mockup interface */}
                  <div style={{ display: "flex", gap: "8px", padding: "12px 10px", background: "transparent", zIndex: 10 }}>
                    <button
                      className="scan-btn"
                      onClick={onScan}
                      disabled={isScanning}
                      style={{ margin: 0, padding: "10px", fontSize: "0.74rem", flexGrow: 2, height: "38px" }}
                    >
                      {isScanning ? "Scanning..." : "Execute Scan"}
                    </button>
                    <button
                      onClick={onClear}
                      disabled={isScanning}
                      style={{
                        padding: "0 14px",
                        background: "rgba(255, 255, 255, 0.05)",
                        border: "1px solid var(--border)",
                        borderRadius: "var(--radius-md)",
                        color: "var(--foreground-dim)",
                        fontSize: "0.74rem",
                        fontWeight: 800,
                        cursor: "pointer",
                        height: "38px",
                        transition: "all 0.2s ease"
                      }}
                      onMouseEnter={(e) => e.currentTarget.style.background = "rgba(255, 255, 255, 0.1)"}
                      onMouseLeave={(e) => e.currentTarget.style.background = "rgba(255, 255, 255, 0.05)"}
                    >
                      Clear
                    </button>
                  </div>
                </div>
              ) : (
                /* Drag & Drop Upload Zone inside the Phone screen */
                <div 
                  className={`phone-upload-zone ${isDragging ? "dragging" : ""}`}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={handleDrop}
                  onClick={() => fileInputRef.current?.click()}
                  style={{
                    flexGrow: 1,
                    minHeight: 0,
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    justifyContent: "center",
                    padding: "24px 16px",
                    cursor: "pointer",
                    textAlign: "center",
                    transition: "all 0.3s ease",
                    margin: "12px",
                    borderRadius: "16px",
                    border: isDragging ? "2px dashed var(--signal)" : "1px dashed rgba(255, 248, 238, 0.15)",
                    background: isDragging ? "rgba(219, 255, 74, 0.03)" : "transparent"
                  }}
                >
                  <input 
                    type="file" 
                    ref={fileInputRef} 
                    onChange={handleFileChange} 
                    accept="image/*,application/pdf" 
                    style={{ display: "none" }} 
                  />
                  
                  <div style={{
                    width: "56px",
                    height: "56px",
                    borderRadius: "50%",
                    background: "rgba(219, 255, 74, 0.05)",
                    border: "1px solid rgba(219, 255, 74, 0.15)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: "1.5rem",
                    marginBottom: "16px",
                    boxShadow: "0 8px 24px rgba(0,0,0,0.2)"
                  }}>
                    📤
                  </div>
                  
                  <strong style={{ fontSize: "0.86rem", color: "var(--signal)", letterSpacing: "0.02em" }}>
                    Upload Receipt Proof
                  </strong>
                  <p style={{ fontSize: "0.72rem", color: "var(--foreground-muted)", margin: "6px 0 0 0", lineHeight: 1.4, padding: "0 10px" }}>
                    Drag &amp; drop payment screenshot/PDF, or click to browse
                  </p>

                  <div style={{ marginTop: "32px", display: "flex", flexDirection: "column", gap: "8px", width: "100%" }}>
                    <button 
                      onClick={(e) => { e.stopPropagation(); onLoadDemo(); }} 
                      className="demo-button-pulse"
                      style={{
                        background: "rgba(255, 255, 255, 0.04)",
                        border: "1px solid var(--border)",
                        borderRadius: "20px",
                        padding: "8px 16px",
                        fontSize: "0.7rem",
                        fontWeight: 800,
                        color: "var(--foreground-dim)",
                        cursor: "pointer",
                        transition: "all 0.2s ease"
                      }}
                      onMouseEnter={(e) => e.currentTarget.style.background = "rgba(255, 255, 255, 0.08)"}
                      onMouseLeave={(e) => e.currentTarget.style.background = "rgba(255, 255, 255, 0.04)"}
                    >
                      Load Sample Demo
                    </button>
                    
                    <a 
                      href="https://wa.me/14155238886?text=join%20choose-factory"
                      target="_blank"
                      rel="noopener noreferrer"
                      onClick={(e) => e.stopPropagation()}
                      style={{
                        fontSize: "0.70rem",
                        color: "#25d366",
                        textDecoration: "none",
                        display: "inline-flex",
                        alignItems: "center",
                        justifyContent: "center",
                        gap: "4px",
                        opacity: 0.85,
                        transition: "opacity 0.2s",
                        fontWeight: 700,
                        marginTop: "16px"
                      }}
                      onMouseEnter={(e) => e.currentTarget.style.opacity = "1"}
                      onMouseLeave={(e) => e.currentTarget.style.opacity = "0.85"}
                    >
                      Prefer WhatsApp? Scan without uploading here →
                    </a>
                  </div>
                </div>
              )
            ) : (
              /* Message Scanner Plain Text Area inside the Phone screen */
              <div style={{
                flexGrow: 1,
                display: "flex",
                flexDirection: "column",
                padding: "16px 14px 10px",
                minHeight: 0,
                gap: "12px"
              }}>
                <strong style={{ fontSize: "0.8rem", color: "var(--foreground)", letterSpacing: "0.02em" }}>
                  Scan Message Text
                </strong>
                <textarea
                  value={messageText}
                  onChange={(e) => setMessageText(e.target.value)}
                  placeholder="Paste a WhatsApp message, SMS bank alert, lottery notification, or text with links/UPI IDs here..."
                  disabled={isScanning}
                  style={{
                    flexGrow: 1,
                    resize: "none",
                    background: "rgba(0,0,0,0.35)",
                    border: "1px solid var(--border)",
                    borderRadius: "12px",
                    padding: "12px",
                    fontSize: "0.76rem",
                    color: "var(--foreground)",
                    fontFamily: "var(--font-sans)",
                    lineHeight: 1.4,
                    outline: "none"
                  }}
                />
                
                {/* Sample quick loader buttons */}
                <div style={{ display: "flex", gap: "6px", overflowX: "auto", paddingBottom: "4px" }}>
                  <button
                    disabled={isScanning}
                    onClick={() => setMessageText("Dear customer, your SBI account is blocked due to PAN card updates. Verify immediately at: http://bit.ly/sbi-kyc-check Call helpline +91 99887 76655")}
                    style={{
                      background: "rgba(255,255,255,0.03)",
                      border: "1px solid rgba(255,255,255,0.06)",
                      borderRadius: "14px",
                      padding: "4px 10px",
                      fontSize: "0.6rem",
                      color: "var(--foreground-dim)",
                      whiteSpace: "nowrap",
                      cursor: "pointer"
                    }}
                  >
                    💡 Sample Scam SMS
                  </button>
                  <button
                    disabled={isScanning}
                    onClick={() => setMessageText("Scan this QR code to claim ₹5,000 refund/cashback! Direct transfer to your bank wallet: upi://pay?pa=refund-helper@okaxis&pn=Cashback%20Refund&am=5000")}
                    style={{
                      background: "rgba(255,255,255,0.03)",
                      border: "1px solid rgba(255,255,255,0.06)",
                      borderRadius: "14px",
                      padding: "4px 10px",
                      fontSize: "0.6rem",
                      color: "var(--foreground-dim)",
                      whiteSpace: "nowrap",
                      cursor: "pointer"
                    }}
                  >
                    💡 Sample UPI Scam
                  </button>
                </div>

                <div style={{ display: "flex", gap: "8px", padding: "4px 0", background: "transparent", zIndex: 10 }}>
                  <button
                    className="scan-btn"
                    onClick={onMessageScan}
                    disabled={isScanning || !messageText.trim()}
                    style={{ margin: 0, padding: "10px", fontSize: "0.74rem", flexGrow: 2, height: "38px" }}
                  >
                    {isScanning ? "Scanning message..." : "Scan Message Text"}
                  </button>
                  <button
                    onClick={onClear}
                    disabled={isScanning}
                    style={{
                      padding: "0 14px",
                      background: "rgba(255, 255, 255, 0.05)",
                      border: "1px solid var(--border)",
                      borderRadius: "var(--radius-md)",
                      color: "var(--foreground-dim)",
                      fontSize: "0.74rem",
                      fontWeight: 800,
                      cursor: "pointer",
                      height: "38px",
                      transition: "all 0.2s ease"
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.background = "rgba(255, 255, 255, 0.1)"}
                    onMouseLeave={(e) => e.currentTarget.style.background = "rgba(255, 255, 255, 0.05)"}
                  >
                    Clear
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>          </div>
        </div>
      </div>

      {errorMsg && (
        <p style={{
          marginTop: "16px",
          fontSize: "0.78rem",
          color: "#ff4d2e",
          textAlign: "center",
          fontWeight: 700,
          background: "rgba(255, 77, 46, 0.08)",
          border: "1px solid rgba(255, 77, 46, 0.16)",
          borderRadius: "8px",
          padding: "10px",
          maxWidth: "320px",
          width: "100%"
        }}>
          {errorMsg}
        </p>
      )}
    </div>
  );
}
