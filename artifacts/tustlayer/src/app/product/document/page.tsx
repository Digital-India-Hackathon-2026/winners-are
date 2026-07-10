"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function RedirectPage() {
  const router = useRouter();
  useEffect(() => {
    router.replace("/product");
  }, [router]);

  return (
    <div style={{
      minHeight: "100vh",
      display: "grid",
      placeItems: "center",
      background: "var(--bg)",
      color: "var(--foreground-dim)",
      fontFamily: "var(--font-sans)"
    }}>
      <p>Redirecting to Unified Scanner...</p>
    </div>
  );
}
