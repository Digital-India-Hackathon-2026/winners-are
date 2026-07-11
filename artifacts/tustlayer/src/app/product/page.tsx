"use client";

import { useState } from "react";
import { PhonePreview } from "@/components/product/PhonePreview";
import { ResultsPanel } from "@/components/product/ResultsPanel";
import { useLenisScroll } from "@/hooks/useLenisScroll";

export default function ProductPage() {
  useLenisScroll();

  const [messageText, setMessageText] = useState<string>("");
  const [activeTab, setActiveTab] = useState<"file" | "message">("file");
  const [uploadedImage, setUploadedImage] = useState<string | null>(null);
  const [selectedFile,  setSelectedFile]  = useState<File | null>(null);
  const [uploadedName,  setUploadedName]  = useState<string>("");
  const [isScanning,    setIsScanning]    = useState<boolean>(false);
  const [scanResults,   setScanResults]   = useState<any>(null);
  const [errorMsg,      setErrorMsg]      = useState<string | null>(null);

  const handleFileSelect = (file: File) => {
    const ext = file.name.split('.').pop()?.toLowerCase();
    const isDoc = ["doc", "docx", "docm"].includes(ext || "");
    const allowedTypes = [
      "image/jpeg", "image/png", "image/webp", "image/svg+xml", "application/pdf",
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      "application/vnd.ms-word.document.macroEnabled.12",
      "application/msword"
    ];
    if (!allowedTypes.includes(file.type) && !isDoc) {
      setErrorMsg("Unsupported format. Please upload a receipt image, PDF, or Word document.");
      setSelectedFile(null);
      setUploadedImage(null);
      setUploadedName("");
      setScanResults(null);
      return;
    }

    if (file.size > 50 * 1024 * 1024) {
      setErrorMsg("File exceeds 50MB size limit. Please upload a smaller document.");
      setSelectedFile(null);
      setUploadedImage(null);
      setUploadedName("");
      setScanResults(null);
      return;
    }
    
    setErrorMsg(null);
    setSelectedFile(file);
    setUploadedName(file.name);
    setScanResults(null);
    
    if (file.type === "application/pdf") {
      setUploadedImage("pdf-placeholder");
    } else if (file.type.includes("word") || isDoc) {
      setUploadedImage("doc-placeholder");
    } else {
      const reader = new FileReader();
      reader.onload = (e) => {
        if (e.target?.result && typeof e.target.result === "string") {
          setUploadedImage(e.target.result);
        }
      };
      reader.readAsDataURL(file);
    }
  };

  const handleClear = () => {
    setSelectedFile(null);
    setUploadedImage(null);
    setUploadedName("");
    setScanResults(null);
    setErrorMsg(null);
    setMessageText("");
  };

  const handleScan = async () => {
    if (!selectedFile && !uploadedImage) return;
    setIsScanning(true);
    setErrorMsg(null);
    try {
      const formData = new FormData();
      if (selectedFile) {
        formData.append("file", selectedFile, selectedFile.name);
      } else {
        if (uploadedImage!.startsWith("data:")) {
          const parts = uploadedImage!.split(',');
          const mime = parts[0].match(/:(.*?);/)?.[1] || 'image/png';
          const bstr = atob(parts[1]);
          let n = bstr.length;
          const u8arr = new Uint8Array(n);
          while (n--) {
            u8arr[n] = bstr.charCodeAt(n);
          }
          const blob = new Blob([u8arr], { type: mime });
          formData.append("file", blob, uploadedName || "screenshot.png");
        } else {
          const blob = await (await fetch(uploadedImage!)).blob();
          formData.append("file", blob, uploadedName || "screenshot.png");
        }
      }

      const response = await fetch("/api/v1/scan/unified", { method: "POST", body: formData });
      if (response.status === 413) {
        throw new Error("File exceeds upload limit (max 4.5 MB via API). Try a smaller image.");
      }
      if (!response.ok) {
        const errBody = await response.text();
        let detail = `HTTP ${response.status}`;
        try { detail = JSON.parse(errBody).detail || detail; } catch {}
        throw new Error(detail);
      }
      setScanResults(await response.json());
    } catch (err: any) {
      console.error("Forensic scan failed:", err);
      setErrorMsg(err.message || "Forensic scan failed. Please try again.");
    } finally {
      setIsScanning(false);
    }
  };

  const handleMessageScan = async () => {
    if (!messageText || !messageText.trim()) return;
    setIsScanning(true);
    setErrorMsg(null);
    setScanResults(null);
    try {
      const response = await fetch("/api/v1/scan/message", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: messageText })
      });
      if (!response.ok) {
        const errBody = await response.text();
        let detail = `HTTP ${response.status}`;
        try { detail = JSON.parse(errBody).detail || detail; } catch {}
        throw new Error(detail);
      }
      const data = await response.json();
      setScanResults({ file_type: "message", message_result: data });
    } catch (err: any) {
      console.error("Message scan failed:", err);
      setErrorMsg(err.message || "Message scan failed. Please try again.");
    } finally {
      setIsScanning(false);
    }
  };

  const handleLoadDemo = () => {
    setSelectedFile(null);
    setUploadedName("phonepe_receipt_demo.svg");
    setScanResults(null);
    setErrorMsg(null);
    const demoSvg = `<svg xmlns="http://www.w3.org/2000/svg" width="360" height="640" viewBox="0 0 360 640">
  <rect width="360" height="640" fill="#0f0f15"/>
  <rect width="360" height="56" fill="#5f259f"/>
  <text x="20" y="34" font-family="sans-serif" font-size="16" font-weight="bold" fill="white">Transaction Successful</text>
  <circle cx="180" cy="140" r="30" fill="#12b76a"/>
  <path d="M168 140l8 8 16-16" stroke="white" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
  <text x="180" y="205" font-family="sans-serif" font-size="13" fill="#9ca3af" text-anchor="middle">Paid to</text>
  <text x="180" y="232" font-family="sans-serif" font-size="20" font-weight="bold" fill="white" text-anchor="middle">ONNARAM SHIVA</text>
  <text x="180" y="285" font-family="sans-serif" font-size="36" font-weight="900" fill="#dbff4a" text-anchor="middle">&#8377;150</text>
  <rect x="20" y="325" width="320" height="1" fill="#ffffff" opacity="0.1"/>
  <text x="20" y="360" font-family="sans-serif" font-size="12" fill="#9ca3af">Banking Name</text>
  <text x="340" y="360" font-family="sans-serif" font-size="12" font-weight="bold" fill="white" text-anchor="end">ONNARAM SHIVA</text>
  <text x="20" y="398" font-family="sans-serif" font-size="12" fill="#9ca3af">UPI ID</text>
  <text x="340" y="398" font-family="sans-serif" font-size="12" font-weight="bold" fill="white" text-anchor="end">7702799024@ybl</text>
  <text x="20" y="436" font-family="sans-serif" font-size="12" fill="#9ca3af">UTR (Transaction ID)</text>
  <text x="340" y="436" font-family="sans-serif" font-size="12" font-weight="bold" fill="#34e6ff" text-anchor="end">261490247702</text>
  <text x="20" y="474" font-family="sans-serif" font-size="12" fill="#9ca3af">Date &amp; Time</text>
  <text x="340" y="474" font-family="sans-serif" font-size="12" font-weight="bold" fill="white" text-anchor="end">26 May 2026, 1:23 PM</text>
  <rect x="20" y="510" width="320" height="1" fill="#ffffff" opacity="0.1"/>
  <circle cx="180" cy="550" r="14" fill="#5f259f"/>
  <text x="180" y="554" font-family="sans-serif" font-size="10" font-weight="bold" fill="white" text-anchor="middle">PP</text>
  <text x="180" y="582" font-family="sans-serif" font-size="11" fill="#9ca3af" text-anchor="middle">Powered by PhonePe</text>
</svg>`;
    setUploadedImage(`data:image/svg+xml;base64,${btoa(unescape(encodeURIComponent(demoSvg)))}`);
  };

  return (
    <div className="product-page">
      <div className="product-layout">
        <PhonePreview
          uploadedImage={uploadedImage}
          uploadedName={uploadedName}
          isScanning={isScanning}
          onFileSelect={handleFileSelect}
          onScan={handleScan}
          onLoadDemo={handleLoadDemo}
          onClear={handleClear}
          errorMsg={errorMsg}
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          messageText={messageText}
          setMessageText={setMessageText}
          onMessageScan={handleMessageScan}
        />
        <ResultsPanel results={scanResults} isScanning={isScanning} onClear={handleClear} />
      </div>
    </div>
  );
}
