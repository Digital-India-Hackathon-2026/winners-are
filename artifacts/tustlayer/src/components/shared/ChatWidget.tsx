"use client";

import { useState, useRef, useEffect, useCallback } from "react";

interface Message {
  role: "user" | "assistant";
  content: string;
}

const GREETING: Message = {
  role: "assistant",
  content:
    "Hi! 👋 I'm the TrustLayer assistant. Ask me anything about UPI payments, payment scams, or how this site works — I'm here to help!",
};

export function ChatWidget() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([GREETING]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [mounted, setMounted] = useState(false);

  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const panelRef = useRef<HTMLDivElement>(null);

  useEffect(() => setMounted(true), []);

  // Scroll to bottom on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  // Focus input when panel opens
  useEffect(() => {
    if (open) {
      setTimeout(() => inputRef.current?.focus(), 150);
    }
  }, [open]);

  // Close on outside click
  const handleOutsideClick = useCallback(
    (e: MouseEvent) => {
      if (
        open &&
        panelRef.current &&
        !panelRef.current.contains(e.target as Node)
      ) {
        // Don't close if clicking the toggle button (it has its own handler)
        const toggle = document.getElementById("chat-widget-toggle");
        if (toggle && toggle.contains(e.target as Node)) return;
        setOpen(false);
      }
    },
    [open]
  );

  useEffect(() => {
    document.addEventListener("mousedown", handleOutsideClick);
    return () => document.removeEventListener("mousedown", handleOutsideClick);
  }, [handleOutsideClick]);

  const sendMessage = async () => {
    const text = input.trim();
    if (!text || loading) return;

    const userMsg: Message = { role: "user", content: text };
    const history = messages.filter((m) => m !== GREETING || messages.length > 1);
    const newMessages = [...messages, userMsg];
    setMessages(newMessages);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("/api/v1/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text,
          history: history.slice(-10).map((m) => ({
            role: m.role,
            content: m.content,
          })),
        }),
      });

      if (!res.ok) throw new Error("API error");
      const data = await res.json();
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.reply },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "I'm having a little trouble connecting right now — please try again in a moment! 🙏",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  if (!mounted) return null;

  return (
    <>
      <style>{`
        /* ── Chat Widget — scoped styles ── */
        .cw-fab {
          position: fixed;
          bottom: 24px;
          right: 24px;
          z-index: 9999;
          width: 56px;
          height: 56px;
          border-radius: 50%;
          border: 1.5px solid var(--border-active, rgba(219,255,74,0.4));
          background: var(--bg-elevated, #0a0a09);
          box-shadow: 0 4px 24px rgba(219,255,74,0.18), 0 2px 8px rgba(0,0,0,0.5);
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: transform 0.18s ease, box-shadow 0.18s ease;
          color: var(--signal, #dbff4a);
        }
        .cw-fab:hover {
          transform: scale(1.1);
          box-shadow: 0 6px 32px rgba(219,255,74,0.32), 0 2px 8px rgba(0,0,0,0.6);
        }
        .cw-fab svg { width: 26px; height: 26px; }

        .cw-panel {
          position: fixed;
          bottom: 92px;
          right: 24px;
          z-index: 9998;
          width: 380px;
          max-width: calc(100vw - 48px);
          height: 560px;
          max-height: calc(100dvh - 120px);
          border-radius: var(--radius-lg, 22px);
          border: 1px solid var(--border, rgba(255,248,238,0.1));
          background: var(--bg-glass, rgba(10,10,9,0.92));
          backdrop-filter: blur(20px);
          -webkit-backdrop-filter: blur(20px);
          box-shadow: 0 24px 64px rgba(0,0,0,0.6), 0 0 0 1px rgba(219,255,74,0.06);
          display: flex;
          flex-direction: column;
          overflow: hidden;
          transform-origin: bottom right;
          transition: opacity 0.18s ease, transform 0.18s ease;
        }
        .cw-panel[data-open="false"] {
          opacity: 0;
          transform: scale(0.88) translateY(12px);
          pointer-events: none;
        }
        .cw-panel[data-open="true"] {
          opacity: 1;
          transform: scale(1) translateY(0);
          pointer-events: all;
        }

        /* Header */
        .cw-header {
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 14px 16px 12px;
          border-bottom: 1px solid var(--border, rgba(255,248,238,0.08));
          flex-shrink: 0;
        }
        .cw-avatar {
          width: 34px;
          height: 34px;
          border-radius: 50%;
          background: linear-gradient(135deg, var(--signal, #dbff4a) 0%, var(--cyan, #34e6ff) 100%);
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 16px;
          flex-shrink: 0;
        }
        .cw-header-text { flex: 1; min-width: 0; }
        .cw-header-title {
          font-size: 14px;
          font-weight: 600;
          color: var(--foreground, #fff8ee);
          line-height: 1.2;
        }
        .cw-header-sub {
          font-size: 11px;
          color: var(--foreground-dim, rgba(255,248,238,0.42));
          line-height: 1.3;
          margin-top: 1px;
        }
        .cw-close {
          background: none;
          border: none;
          cursor: pointer;
          color: var(--foreground-dim, rgba(255,248,238,0.42));
          padding: 4px;
          border-radius: 6px;
          line-height: 0;
          transition: color 0.15s;
        }
        .cw-close:hover { color: var(--foreground, #fff8ee); }

        /* Messages */
        .cw-messages {
          flex: 1;
          overflow-y: auto;
          padding: 14px 14px 8px;
          display: flex;
          flex-direction: column;
          gap: 10px;
          scrollbar-width: thin;
          scrollbar-color: var(--border, rgba(255,248,238,0.1)) transparent;
        }
        .cw-messages::-webkit-scrollbar { width: 4px; }
        .cw-messages::-webkit-scrollbar-thumb {
          background: var(--border, rgba(255,248,238,0.1));
          border-radius: 4px;
        }

        .cw-bubble-wrap {
          display: flex;
          flex-direction: column;
        }
        .cw-bubble-wrap.user { align-items: flex-end; }
        .cw-bubble-wrap.assistant { align-items: flex-start; }

        .cw-bubble {
          max-width: 85%;
          padding: 9px 13px;
          border-radius: 16px;
          font-size: 13.5px;
          line-height: 1.55;
          white-space: pre-wrap;
          word-break: break-word;
        }
        .cw-bubble.user {
          background: var(--signal, #dbff4a);
          color: var(--text-inverse, #0a0b06);
          border-bottom-right-radius: 4px;
          font-weight: 500;
        }
        .cw-bubble.assistant {
          background: var(--bg-card, rgba(255,248,238,0.05));
          border: 1px solid var(--border, rgba(255,248,238,0.08));
          color: var(--foreground, #fff8ee);
          border-bottom-left-radius: 4px;
        }

        /* Typing indicator */
        .cw-typing {
          display: flex;
          align-items: center;
          gap: 4px;
          padding: 10px 13px;
          background: var(--bg-card, rgba(255,248,238,0.05));
          border: 1px solid var(--border, rgba(255,248,238,0.08));
          border-radius: 16px;
          border-bottom-left-radius: 4px;
          width: fit-content;
        }
        .cw-typing span {
          width: 6px;
          height: 6px;
          border-radius: 50%;
          background: var(--foreground-dim, rgba(255,248,238,0.42));
          animation: cw-bounce 1.2s ease infinite;
        }
        .cw-typing span:nth-child(2) { animation-delay: 0.2s; }
        .cw-typing span:nth-child(3) { animation-delay: 0.4s; }
        @keyframes cw-bounce {
          0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
          30% { transform: translateY(-5px); opacity: 1; }
        }

        /* Input area */
        .cw-input-area {
          display: flex;
          align-items: flex-end;
          gap: 8px;
          padding: 10px 12px 12px;
          border-top: 1px solid var(--border, rgba(255,248,238,0.08));
          flex-shrink: 0;
        }
        .cw-textarea {
          flex: 1;
          resize: none;
          background: var(--bg-card, rgba(255,248,238,0.04));
          border: 1px solid var(--border, rgba(255,248,238,0.1));
          border-radius: 12px;
          color: var(--foreground, #fff8ee);
          font-family: var(--font-sans, Inter, sans-serif);
          font-size: 13.5px;
          line-height: 1.5;
          padding: 9px 12px;
          max-height: 100px;
          min-height: 38px;
          outline: none;
          transition: border-color 0.15s;
        }
        .cw-textarea::placeholder { color: var(--foreground-dim, rgba(255,248,238,0.42)); }
        .cw-textarea:focus { border-color: var(--border-active, rgba(219,255,74,0.4)); }

        .cw-send {
          flex-shrink: 0;
          width: 38px;
          height: 38px;
          border-radius: 10px;
          border: none;
          background: var(--signal, #dbff4a);
          color: var(--text-inverse, #0a0b06);
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: opacity 0.15s, transform 0.15s;
        }
        .cw-send:disabled { opacity: 0.4; cursor: not-allowed; }
        .cw-send:not(:disabled):hover { transform: scale(1.06); }
        .cw-send svg { width: 18px; height: 18px; }

        /* Light theme overrides */
        [data-theme="light"] .cw-fab {
          background: #ffffff;
          border-color: rgba(14,165,233,0.5);
          box-shadow: 0 4px 20px rgba(14,165,233,0.18), 0 2px 8px rgba(15,23,42,0.12);
          color: var(--signal, #0ea5e9);
        }
        [data-theme="light"] .cw-panel {
          background: rgba(255,255,255,0.97);
          border-color: #e2e8f0;
          box-shadow: 0 24px 64px rgba(15,23,42,0.15);
        }
        [data-theme="light"] .cw-bubble.user {
          background: var(--signal, #0ea5e9);
          color: #ffffff;
        }
        [data-theme="light"] .cw-bubble.assistant {
          background: #f8fafc;
          border-color: #e2e8f0;
          color: #0f172a;
        }
        [data-theme="light"] .cw-textarea {
          background: #f8fafc;
          border-color: #e2e8f0;
          color: #0f172a;
        }
        [data-theme="light"] .cw-send {
          background: var(--signal, #0ea5e9);
          color: #ffffff;
        }
        [data-theme="light"] .cw-typing span {
          background: #94a3b8;
        }

        /* Mobile: full-width sheet pinned to bottom */
        @media (max-width: 480px) {
          .cw-panel {
            width: 100vw;
            max-width: 100vw;
            right: 0;
            bottom: 0;
            border-radius: var(--radius-lg, 22px) var(--radius-lg, 22px) 0 0;
            height: 70dvh;
          }
          .cw-fab { bottom: 16px; right: 16px; }
        }
      `}</style>

      {/* Floating action button */}
      <button
        id="chat-widget-toggle"
        className="cw-fab"
        aria-label={open ? "Close chat" : "Open chat assistant"}
        onClick={() => setOpen((v) => !v)}
      >
        {open ? (
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        ) : (
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
          </svg>
        )}
      </button>

      {/* Chat panel */}
      <div ref={panelRef} className="cw-panel" data-open={String(open)} role="dialog" aria-label="TrustLayer chat assistant">
        {/* Header */}
        <div className="cw-header">
          <div className="cw-avatar">🛡️</div>
          <div className="cw-header-text">
            <div className="cw-header-title">TrustLayer Assistant</div>
            <div className="cw-header-sub">UPI &amp; payment fraud help</div>
          </div>
          <button className="cw-close" aria-label="Close" onClick={() => setOpen(false)}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>

        {/* Messages */}
        <div className="cw-messages" role="log" aria-live="polite">
          {messages.map((msg, i) => (
            <div key={i} className={`cw-bubble-wrap ${msg.role}`}>
              <div className={`cw-bubble ${msg.role}`}>{msg.content}</div>
            </div>
          ))}
          {loading && (
            <div className="cw-bubble-wrap assistant">
              <div className="cw-typing" aria-label="Thinking…">
                <span /><span /><span />
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <div className="cw-input-area">
          <textarea
            ref={inputRef}
            className="cw-textarea"
            placeholder="Ask about UPI, scams, or TrustLayer…"
            rows={1}
            value={input}
            onChange={(e) => {
              setInput(e.target.value);
              // Auto-grow textarea
              e.target.style.height = "auto";
              e.target.style.height = Math.min(e.target.scrollHeight, 100) + "px";
            }}
            onKeyDown={handleKeyDown}
            disabled={loading}
          />
          <button
            className="cw-send"
            aria-label="Send"
            disabled={!input.trim() || loading}
            onClick={sendMessage}
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="22" y1="2" x2="11" y2="13" />
              <polygon points="22 2 15 22 11 13 2 9 22 2" />
            </svg>
          </button>
        </div>
      </div>
    </>
  );
}
