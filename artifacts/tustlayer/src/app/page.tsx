"use client";
import { HeroSection } from "@/components/landing/HeroSection";
import { WhatsappScanSection } from "@/components/landing/WhatsappScanSection";
import { ScamRealitySection } from "@/components/landing/ScamRealitySection";
import { ForensicScanSection } from "@/components/landing/ForensicScanSection";
import { VerdictSection } from "@/components/landing/VerdictSection";
import { CTASection } from "@/components/landing/CTASection";
import { useLenisScroll } from "@/hooks/useLenisScroll";
import { useSectionReveal } from "@/hooks/useSectionReveal";

export default function Home() {
  useLenisScroll();
  useSectionReveal();
  return (
    <main>
      <HeroSection />
      <WhatsappScanSection />
      <ScamRealitySection />
      <ForensicScanSection />
      <VerdictSection />
      <CTASection />
    </main>
  );
}
