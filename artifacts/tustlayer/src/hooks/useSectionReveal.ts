"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

/**
 * Simple section-based GSAP entrance animation.
 * Each element with a `.reveal-*` class animates in
 * when it enters the viewport. No pinning, no stacking.
 */
export function useSectionReveal() {
  const initialized = useRef(false);

  useEffect(() => {
    if (initialized.current) return;
    initialized.current = true;

    const prefersReducedMotion = window.matchMedia(
      "(prefers-reduced-motion: reduce)",
    ).matches;

    if (prefersReducedMotion) {
      gsap.utils
        .toArray<HTMLElement>(".reveal-up, .reveal-left, .reveal-right, .reveal-scale")
        .forEach((el) => {
          gsap.set(el, { opacity: 1, x: 0, y: 0, scale: 1 });
        });
      return;
    }

    // Reveal UP
    gsap.utils.toArray<HTMLElement>(".reveal-up").forEach((el, i) => {
      gsap.to(el, {
        opacity: 1,
        y: 0,
        duration: 0.9,
        delay: i * 0.08,
        ease: "power3.out",
        scrollTrigger: {
          trigger: el,
          start: "top 88%",
          toggleActions: "play none none none",
        },
      });
    });

    // Reveal LEFT
    gsap.utils.toArray<HTMLElement>(".reveal-left").forEach((el) => {
      gsap.to(el, {
        opacity: 1,
        x: 0,
        duration: 0.9,
        ease: "power3.out",
        scrollTrigger: {
          trigger: el,
          start: "top 88%",
          toggleActions: "play none none none",
        },
      });
    });

    // Reveal RIGHT
    gsap.utils.toArray<HTMLElement>(".reveal-right").forEach((el) => {
      gsap.to(el, {
        opacity: 1,
        x: 0,
        duration: 0.9,
        ease: "power3.out",
        scrollTrigger: {
          trigger: el,
          start: "top 88%",
          toggleActions: "play none none none",
        },
      });
    });

    // Reveal SCALE
    gsap.utils.toArray<HTMLElement>(".reveal-scale").forEach((el) => {
      gsap.to(el, {
        opacity: 1,
        scale: 1,
        duration: 1,
        ease: "power3.out",
        scrollTrigger: {
          trigger: el,
          start: "top 88%",
          toggleActions: "play none none none",
        },
      });
    });

    return () => {
      ScrollTrigger.getAll().forEach((t) => t.kill());
    };
  }, []);
}
