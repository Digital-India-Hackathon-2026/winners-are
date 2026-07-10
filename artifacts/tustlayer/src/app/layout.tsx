import type { Metadata } from "next";
import "./globals.css";
import { Navigation } from "@/components/shared/Navigation";
import { ThemeProvider } from "@/components/shared/ThemeProvider";

export const metadata: Metadata = {
  title: "TrustLayer AI — UPI Payment Proof Forensics",
  description:
    "AI-powered forensic analysis for verifying UPI payment screenshots. Detect fake proofs before they reach the counter.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="min-h-full bg-[var(--bg)]">
        <ThemeProvider attribute="data-theme" defaultTheme="dark" enableSystem={false}>
          <Navigation />
          {children}
          <footer className="site-footer">
            <p>
              Built for the Hackathon. Powered by{" "}
              <a href="https://build.nvidia.com" target="_blank" rel="noopener">
                NVIDIA NIMs
              </a>{" "}
              &amp;{" "}
              <a href="https://supabase.com" target="_blank" rel="noopener">
                Supabase
              </a>
              .
            </p>
          </footer>
        </ThemeProvider>
      </body>
    </html>
  );
}
