import type { Metadata, Viewport } from "next";
import { Inter, Space_Grotesk } from "next/font/google";
import { MotionConfig } from "motion/react";
import { Footer } from "@/components/Footer";
import { Sidebar, TabBar } from "@/components/Nav";
import { themeScript } from "@/components/ThemeToggle";
import { getSummary } from "@/lib/data";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], weight: ["400", "500", "600", "700"], variable: "--font-inter", display: "swap" });
const grotesk = Space_Grotesk({ subsets: ["latin"], weight: ["600", "700"], variable: "--font-space-grotesk", display: "swap" });

const SITE = process.env.NEXT_PUBLIC_SITE_URL ?? "https://samuelwvm.github.io/financial-intelligence-dashboard";

export const metadata: Metadata = {
  metadataBase: new URL(SITE.endsWith("/") ? SITE : `${SITE}/`),
  title: { default: "Radar Financeiro", template: "%s · Radar Financeiro" },
  description:
    "Dashboard de mercado para investidor iniciante: Ibovespa, S&P 500, dólar, ações, cripto, SELIC, CDI e IPCA com dados reais e linguagem simples. Atualizado diariamente.",
  applicationName: "Radar Financeiro",
  openGraph: { type: "website", locale: "pt_BR", siteName: "Radar Financeiro" },
  robots: { index: true, follow: true },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  viewportFit: "cover",
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#F6F7F4" },
    { media: "(prefers-color-scheme: dark)", color: "#0B1210" },
  ],
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  const groups = Object.fromEntries(getSummary().assets.map((a) => [a.slug, a.group]));
  return (
    <html lang="pt-BR" className={`${inter.variable} ${grotesk.variable}`} suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeScript }} />
      </head>
      <body className="min-h-dvh antialiased">
        <a
          href="#conteudo"
          className="sr-only focus:not-sr-only focus:fixed focus:left-3 focus:top-3 focus:z-50 focus:rounded-lg focus:bg-card focus:px-3 focus:py-2"
        >
          Pular para o conteúdo
        </a>
        <MotionConfig reducedMotion="user">
          <Sidebar groups={groups} />
          <div className="lg:pl-[248px]">
            <main
              id="conteudo"
              className="mx-auto flex w-full max-w-[1200px] flex-col pb-[calc(88px+env(safe-area-inset-bottom))] lg:px-8 lg:py-8 lg:pb-10"
            >
              {children}
              <Footer />
            </main>
          </div>
          <TabBar groups={groups} />
        </MotionConfig>
      </body>
    </html>
  );
}
