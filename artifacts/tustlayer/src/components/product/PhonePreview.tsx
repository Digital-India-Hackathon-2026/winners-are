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
        <div className="phone-shell">
          <div className="phone-screen">
            <div className="phone-notch" />
            <div className="phone-topbar">
              <span>TrustLayer AI Scanner</span>
              <span className="live-dot">● ONLINE</span>
            </div>
            
            {uploadedImage ? (
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
                </div>
              </div>
            )}
          </div>
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
