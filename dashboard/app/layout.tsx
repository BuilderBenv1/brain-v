import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Link from "next/link";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Brain-V | Voynich Manuscript Decipherment",
  description:
    "An autonomous cognitive architecture attempting to decipher the Voynich Manuscript through statistical analysis, hypothesis generation, and iterative testing.",
};

const NAV_LINKS = [
  { href: "/", label: "Dashboard" },
  { href: "/hypotheses", label: "Hypotheses" },
  { href: "/beliefs", label: "Beliefs" },
  { href: "/stats", label: "Corpus Stats" },
  { href: "/scores", label: "Score History" },
  { href: "/failed", label: "Failed Approaches" },
  { href: "/about", label: "About" },
];

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-background text-foreground">
        <header className="border-b border-border bg-surface">
          <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
            <Link href="/" className="flex items-center gap-3">
              <span className="text-2xl font-bold text-accent font-mono">
                Brain-V
              </span>
              <span className="text-muted text-sm hidden sm:block">
                VoynichMind
              </span>
            </Link>
            <nav className="flex gap-1 text-sm overflow-x-auto">
              {NAV_LINKS.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  className="px-3 py-1.5 rounded hover:bg-surface-2 text-muted hover:text-foreground transition-colors whitespace-nowrap"
                >
                  {link.label}
                </Link>
              ))}
            </nav>
          </div>
        </header>
        <main className="flex-1 max-w-7xl mx-auto px-4 py-8 w-full">
          {children}
        </main>
        <footer className="border-t border-border bg-surface py-6">
          <div className="max-w-7xl mx-auto px-4 text-center text-sm text-muted">
            <p>
              Brain-V is an open-source cognitive architecture. Every hypothesis
              is tested. Every failure is published.
            </p>
            <p className="mt-1">
              Agents on SKALE via{" "}
              <a
                href="https://agentproof.sh"
                className="text-accent hover:underline"
              >
                AgentProof
              </a>
              . All reasoning on-chain from day 1.
            </p>
            <p className="mt-1">
              Preprint:{" "}
              <a
                href="https://doi.org/10.5281/zenodo.19610118"
                className="text-accent hover:underline"
              >
                doi.org/10.5281/zenodo.19610118
              </a>
            </p>
          </div>
        </footer>
      </body>
    </html>
  );
}
