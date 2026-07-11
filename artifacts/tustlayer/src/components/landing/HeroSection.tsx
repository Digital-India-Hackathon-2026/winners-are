"use client";
import Link from "next/link";
import { ForensicPhone } from "@/components/cinematic/ForensicPhone";

export function HeroSection() {
  return (
    <section className="tl-section hero-section">
      <div className="hero-vignette" />
      <div className="hero-grain" />
      <div className="hero-grid" />
      <div className="hero-scanline" />
      
      <div className="tl-section-inner">
        <div className="hero-copy">
          <p className="hero-eyebrow reveal-up">AI forensic UPI fraud detection</p>
          <h1 className="hero-headline reveal-up">
            Every UPI <span className="accent">screenshot</span> looks real.
          </h1>
          <p className="hero-sub reveal-up">
            Stop accepting fake UPI proofs. TrustLayer AI verifies every payment screenshot in seconds.
          </p>
          <div className="hero-actions reveal-up">
            <Link href="/product" className="btn-primary">
              Try Scanner
            </Link>
            <Link href="#forensic-scan" className="btn-ghost">
              See How It Works
            </Link>
          </div>
        </div>

        <div className="hero-phone-wrap reveal-scale">
          <ForensicPhone />
        </div>
      </div>
    </section>
  );
}

