"use client";

import { useReducedMotion } from "motion/react";
import { useEffect, useState } from "react";

const INTERVAL_MS = 8000;

/**
 * "Em linguagem simples" com dicas que se alternam.
 * - todas as frases ficam empilhadas na mesma célula do grid: o card assume a
 *   altura da maior e não "pula" ao trocar (sem layout shift);
 * - troca a cada 8 s; pausa com mouse/foco em cima ou com a aba em segundo plano;
 * - botões de pausar e avançar (conteúdo que se move sozinho precisa de controle — WCAG 2.2.2);
 * - com movimento reduzido não gira sozinho (só pelo botão "próxima").
 */
export function PlainTips({ tips, variant }: { tips: string[]; variant: "mobile" | "web" }) {
  const reduce = useReducedMotion();
  const [i, setI] = useState(0);
  const [paused, setPaused] = useState(false);
  const [hover, setHover] = useState(false);
  const running = !paused && !hover && !reduce && tips.length > 1;

  useEffect(() => {
    if (!running) return;
    const t = setInterval(() => {
      if (document.visibilityState === "visible") setI((n) => (n + 1) % tips.length);
    }, INTERVAL_MS);
    return () => clearInterval(t);
  }, [running, tips.length]);

  const web = variant === "web";
  const id = `simples-${variant}`;
  const btn = `flex size-11 items-center justify-center rounded-xl ${web ? "text-hl-muted hover:text-hl-fg" : "text-muted hover:text-fg"}`;

  return (
    <section
      style={{ "--i": web ? 7 : 6 } as React.CSSProperties}
      className={
        web
          ? "rise lift hidden flex-[2_1_320px] rounded-[18px] bg-hl p-5 text-hl-fg lg:block"
          : "rise lift mx-5 rounded-2xl border border-line bg-card p-4 lg:hidden"
      }
      aria-labelledby={id}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      onFocus={() => setHover(true)}
      onBlur={() => setHover(false)}
    >
      <div className="-my-2.5 -mr-2.5 flex items-center justify-between gap-2">
        <h2 id={id} className={web ? "text-[12px] font-bold tracking-[0.04em] text-hl-accent" : "text-[13px] font-bold text-pos"}>
          EM LINGUAGEM SIMPLES
        </h2>
        {tips.length > 1 && (
          <div className="flex items-center">
            <span className={`num mr-1 text-[11px] ${web ? "text-hl-muted" : "text-muted"}`} aria-hidden="true">
              {i + 1}/{tips.length}
            </span>
            <button
              type="button"
              className={btn}
              onClick={() => setPaused((p) => !p)}
              aria-label={paused || reduce ? "Retomar troca automática das dicas" : "Pausar troca automática das dicas"}
              aria-pressed={paused}
            >
              {paused || reduce ? (
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                  <path d="M8 5v14l11-7z" />
                </svg>
              ) : (
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                  <path d="M7 5h3.5v14H7zM13.5 5H17v14h-3.5z" />
                </svg>
              )}
            </button>
            <button type="button" className={btn} onClick={() => setI((n) => (n + 1) % tips.length)} aria-label="Próxima dica">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <path d="M9 6l6 6-6 6" />
              </svg>
            </button>
          </div>
        )}
      </div>
      <div className={`grid ${web ? "mt-2" : "mt-1.5"}`} aria-live={running ? "off" : "polite"}>
        {tips.map((t, n) => (
          <p
            key={n}
            aria-hidden={n !== i}
            className={`col-start-1 row-start-1 transition-opacity duration-500 motion-reduce:transition-none ${
              n === i ? "opacity-100" : "pointer-events-none opacity-0"
            } ${web ? "text-[16px] leading-normal" : "text-[15px] leading-[1.45]"}`}
          >
            {t}
          </p>
        ))}
      </div>
    </section>
  );
}
