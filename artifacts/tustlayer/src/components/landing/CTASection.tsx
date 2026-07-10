"use client";
import Link from "next/link";

export function CTASection() {
  return (
    <section className="tl-section cta-section">
      <div className="tl-section-inner">
        <h2 className="reveal-up">Protect Your Business</h2>
        <p className="reveal-up">
          Stop accepting fake UPI proofs. TrustLayer AI verifies every payment screenshot in seconds.
        </p>
        <div className="cta-actions reveal-up">
          <Link href="/product" className="btn-primary">
            Try TrustLayer Scanner
          </Link>
          <a href="https://github.com/Kittu2007/TrustLayer/blob/main/PRODUCT.md" target="_blank" rel="noopener noreferrer" className="btn-ghost">
            View Documentation
          </a>
        </div>
        <div className="cta-footer-note reveal-up">
          Powered by NVIDIA Nemotron-VL + Qwen 3.5-122B reasoning
        </div>
      </div>
    </section>
  );
}
