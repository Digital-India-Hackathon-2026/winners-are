"use client";

import { ChangeEvent, DragEvent, useRef } from "react";

type UploadPanelProps = {
  onFileSelect: (file: File) => void;
  uploadedImage: string | null;
  uploadedName: string;
  onScan: () => void;
  isScanning: boolean;
  hasResults: boolean;
  onLoadDemo: () => void;
  errorMsg?: string | null;
};

export function UploadPanel({
  onFileSelect,
  uploadedImage,
  uploadedName,
  onScan,
  isScanning,
  hasResults,
  onLoadDemo,
  errorMsg,
}: UploadPanelProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    const file = e.dataTransfer.files?.[0];
    if (file && (file.type.startsWith("image/") || file.type === "application/pdf")) {
      onFileSelect(file);
    }
  };

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
  };

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && (file.type.startsWith("image/") || file.type === "application/pdf")) {
      onFileSelect(file);
    }
    // Reset input so the same file can be selected again
    e.target.value = "";
  };

  return (
    <div className="product-panel">
      <div className="product-panel-header">
        <span className="dot" /> Upload Zone
      </div>
      <div className="product-panel-body">
        <div
          className="upload-dropzone"
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onClick={() => fileInputRef.current?.click()}
        >
          <div className="upload-dropzone-icon">↑</div>
          <p>
            <strong>Drop transaction proof</strong> or click to upload
          </p>
          <div className="format-hint">Supports payment screenshots, PDFs, & QR codes</div>
          <input
            type="file"
            ref={fileInputRef}
            className="hidden"
            style={{ display: "none" }}
            accept="image/*,application/pdf"
            onChange={handleFileChange}
          />
        </div>

        {/* Try with sample receipt UX link */}
        <div style={{ marginTop: "14px", textAlign: "center", marginBottom: "8px" }}>
          <span style={{ fontSize: "0.74rem", color: "var(--foreground-dim)" }}>Want to inspect right now? </span>
          <button 
            type="button"
            onClick={(e) => {
              e.stopPropagation(); // Avoid triggering dropzone click
              onLoadDemo();
            }}
            disabled={isScanning}
            style={{
              background: "none",
              border: "none",
              color: "var(--signal)",
              fontSize: "0.74rem",
              fontWeight: 800,
              textDecoration: "underline",
              cursor: "pointer",
              padding: 0
            }}
          >
            One-Click Interactive Demo
          </button>
        </div>

        {uploadedImage && (
          <div className="upload-preview">
            {uploadedImage === "pdf-placeholder" ? (
              <div style={{
                padding: "24px",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                background: "rgba(255, 255, 255, 0.02)",
                borderRadius: "var(--radius-sm)",
                border: "1px solid var(--border)"
              }}>
                <span style={{ fontSize: "2.5rem" }}>📄</span>
                <span style={{ fontSize: "0.8rem", color: "var(--foreground-muted)", marginTop: "8px", fontWeight: "bold", wordBreak: "break-all" }}>
                  {uploadedName}
                </span>
              </div>
            ) : (
              <img src={uploadedImage} alt="Uploaded proof" />
            )}
          </div>
        )}

        <button
          className="scan-btn"
          onClick={onScan}
          disabled={!uploadedImage || isScanning}
        >
          {isScanning ? "Scanning..." : "Execute Forensic Scan"}
        </button>

        {errorMsg && (
          <p style={{ marginTop: "12px", fontSize: "0.78rem", color: "#ff4d2e", textAlign: "center", fontWeight: 700, background: "rgba(255, 77, 46, 0.08)", border: "1px solid rgba(255, 77, 46, 0.16)", borderRadius: "8px", padding: "10px" }}>
            {errorMsg}
          </p>
        )}
      </div>
    </div>
  );
}
