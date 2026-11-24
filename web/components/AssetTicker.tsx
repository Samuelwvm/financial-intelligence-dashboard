"use client";

import Link from "next/link";
import { useEffect, useMemo, useRef, useState, type MouseEvent } from "react";
import { formatPrice } from "@/lib/format";
import { usePortfolio } from "@/lib/hooks";
import type { AssetSummary } from "@/lib/schema";
import { AssetLogo } from "./AssetLogo";
import { Chip } from "./ui";

const PAUSE_MS = 20_000; // pausa ao tocar/arrastar: tempo para ler com calma
const SPEED_PX_S = 30; // devagar
const DRAG_PX = 8; // acima disso o gesto é arraste, não toque

/**
 * Carrossel automático com todos os ativos — uma faixa de rolagem de verdade:
 * - anda sozinho devagar, em loop (duas cópias; ao passar da metade volta sem emenda);
 * - arrastar com o dedo / trackpad / roda do mouse funciona em qualquer tela e pausa por 20 s;
 * - um toque com ele andando só pausa (20 s); parado, tocar num ativo abre a tela dele;
 * - mouse em cima ou foco do teclado pausam; botão de pausar sem prazo (WCAG 2.2.2);
 * - movimento reduzido: não anda sozinho (rolagem manual continua);
 * - ativos da "minha carteira" ganham borda verde e selo de check.
 */
export function AssetTicker({ assets, candidates, defaults }: { assets: AssetSummary[]; candidates: string[]; defaults: string[] }) {
  const [portfolio] = usePortfolio(candidates, defaults);
  const mine = useMemo(() => new Set(portfolio), [portfolio]);
  const [pausedUntil, setPausedUntil] = useState(0);
  const [held, setHeld] = useState(false);
  const [hover, setHover] = useState(false);
  const [now, setNow] = useState(0);
  const viewport = useRef<HTMLDivElement>(null);
  const pos = useRef(0);
  const lastSet = useRef(-1);
  const down = useRef<{ x: number; y: number; wasMoving: boolean; dragged: boolean } | null>(null);
  const pausedRef = useRef(false);

  const tapPaused = pausedUntil > now;
  const paused = held || hover || tapPaused;
  useEffect(() => {
    pausedRef.current = paused; // lido pelo laço de animação, fora do render
  }, [paused]);

  // Volta a andar quando a pausa de 20 s termina.
  useEffect(() => {
    if (!pausedUntil) return;
    const t = setTimeout(() => setNow(Date.now()), Math.max(0, pausedUntil - Date.now()) + 50);
    return () => clearTimeout(t);
  }, [pausedUntil]);

  const pauseFor = () => {
    const t = Date.now();
    setNow(t);
    setPausedUntil(t + PAUSE_MS);
  };

  // Laço de animação: avança o scrollLeft (sem JS quando parado ou com movimento reduzido).
  useEffect(() => {
    const el = viewport.current;
    if (!el || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    let raf = 0;
    let prev = performance.now();
    const step = (t: number) => {
      const dt = Math.min(64, t - prev);
      prev = t;
      const half = el.scrollWidth / 2;
      if (!pausedRef.current && document.visibilityState === "visible" && half > el.clientWidth) {
        pos.current += (SPEED_PX_S * dt) / 1000;
        if (pos.current >= half) pos.current -= half;
        const v = Math.round(pos.current);
        if (v !== lastSet.current) {
          lastSet.current = v;
          el.scrollLeft = v;
        }
      }
      raf = requestAnimationFrame(step);
    };
    raf = requestAnimationFrame(step);
    return () => cancelAnimationFrame(raf);
  }, []);

  // Rolagem feita pela pessoa (arraste, trackpad, roda): sincroniza, mantém o loop e pausa.
  function onScroll() {
    const el = viewport.current;
    if (!el) return;
    if (Math.abs(el.scrollLeft - lastSet.current) <= 1) return; // fomos nós
    const half = el.scrollWidth / 2;
    if (el.scrollLeft >= half) el.scrollLeft -= half;
    else if (el.scrollLeft <= 0 && half > 0) el.scrollLeft += half;
    pos.current = el.scrollLeft;
    lastSet.current = Math.round(el.scrollLeft);
    pauseFor();
  }

  function onClickCapture(e: MouseEvent) {
    const d = down.current;
    down.current = null;
    if (d && (d.wasMoving || d.dragged)) {
      e.preventDefault(); // 1º toque com ele andando (ou fim de arraste): só pausa
      e.stopPropagation();
    }
  }

  const status = held ? "Pausado" : tapPaused ? "Pausado por 20 s · toque num ativo para abrir" : null;

  const item = (a: AssetSummary, copy: boolean) => {
    const inPortfolio = mine.has(a.slug);
    return (
      <li key={`${copy ? "b" : "a"}-${a.slug}`} className="w-[176px] shrink-0">
        <Link
          href={`/ativo/${a.slug}/`}
          tabIndex={copy ? -1 : undefined}
          draggable={false}
          className={`flex h-full flex-col gap-2 rounded-[14px] border bg-card p-3 transition-colors hover:border-muted ${
            inPortfolio ? "border-pos" : "border-line"
          }`}
        >
          <span className="flex items-center gap-2">
            <span className="relative">
              <AssetLogo logo={a.logo} ticker={a.ticker} size={32} />
              {inPortfolio && (
                <span className="absolute -right-1 -bottom-1 flex size-4 items-center justify-center rounded-full border-2 border-card bg-pos text-card">
                  <svg width="8" height="8" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={4} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                    <path d="M5 12l5 5L20 7" />
                  </svg>
                </span>
              )}
            </span>
            <span className="min-w-0">
              <span className="block truncate text-[13px] font-bold">{a.name}</span>
              <span className="block text-[11px] text-muted">
                {a.ticker}
                {inPortfolio && <span className="sr-only">, na sua carteira</span>}
              </span>
            </span>
          </span>
          <span className="flex items-center justify-between gap-2">
            <span className="num truncate font-display text-[15px] font-semibold">{formatPrice(a.price, a.currency)}</span>
            <Chip value={a.change} />
          </span>
        </Link>
      </li>
    );
  };

  return (
    <section aria-labelledby="todos-ativos" style={{ "--i": 8 } as React.CSSProperties} className="rise flex flex-col gap-2">
      <div className="flex items-center justify-between gap-2 px-5 lg:px-0">
        <div className="min-w-0">
          <h2 id="todos-ativos" className="font-display text-[18px] font-semibold lg:text-[20px]">
            Todos os ativos
          </h2>
          <p className="text-[12px] text-muted" aria-live="polite">
            {status ?? (
              <>
                <span className="mr-1 inline-block size-2 rounded-full bg-pos align-middle" aria-hidden="true" />
                borda verde = na sua carteira · toque ou arraste para pausar
              </>
            )}
          </p>
        </div>
        <button
          type="button"
          onClick={() => {
            setHeld((h) => !h);
            setPausedUntil(0);
          }}
          aria-pressed={held}
          aria-label={held ? "Retomar o carrossel de ativos" : "Pausar o carrossel de ativos"}
          className="flex size-11 shrink-0 items-center justify-center rounded-xl text-muted hover:text-fg"
        >
          {held ? (
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
              <path d="M8 5v14l11-7z" />
            </svg>
          ) : (
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
              <path d="M7 5h3.5v14H7zM13.5 5H17v14h-3.5z" />
            </svg>
          )}
        </button>
      </div>
      <div
        ref={viewport}
        className="marquee-viewport no-scrollbar relative overflow-x-auto overscroll-x-contain lg:rounded-[18px]"
        onScroll={onScroll}
        onClickCapture={onClickCapture}
        onPointerDown={(e) => {
          down.current = { x: e.clientX, y: e.clientY, wasMoving: !pausedRef.current, dragged: false };
          pauseFor();
        }}
        onPointerMove={(e) => {
          const d = down.current;
          if (d && Math.hypot(e.clientX - d.x, e.clientY - d.y) > DRAG_PX) d.dragged = true;
        }}
        // Só mouse de verdade (no toque, "mouseenter" ficaria preso) e só foco de teclado.
        onPointerEnter={(e) => e.pointerType === "mouse" && setHover(true)}
        onPointerLeave={(e) => e.pointerType === "mouse" && setHover(false)}
        onFocus={(e) => (e.target as HTMLElement).matches(":focus-visible") && setHover(true)}
        onBlur={() => setHover(false)}
      >
        <div className="marquee-track flex w-max gap-2.5 px-5 py-0.5 lg:px-0">
          <ul className="flex gap-2.5" aria-label="Ativos">
            {assets.map((a) => item(a, false))}
          </ul>
          {/* Cópia para o loop sem emenda: invisível para leitores de tela e fora do Tab. */}
          <ul className="marquee-copy flex gap-2.5" aria-hidden="true">
            {assets.map((a) => item(a, true))}
          </ul>
        </div>
      </div>
    </section>
  );
}
