"use client";

import { useReducedMotion } from "motion/react";
import { useEffect, useRef, useState } from "react";

const INTERVAL_MS = 9000;
const SWIPE_PX = 40;

/**
 * "Em linguagem simples" com dicas que se alternam. Experiência por tamanho de tela:
 * - celular/tablet (variant "mobile", < 1024px): arrastar para o lado troca; pontinhos só indicam;
 * - computador (variant "web"): setas ‹ › (pontinhos só indicam); mouse em cima pausa; sem arrastar.
 * Comum: troca a cada 9 s, sem layout shift (frases empilhadas na mesma célula do grid),
 * setas do teclado com foco no card, e nada gira sozinho com movimento reduzido.
 */
export function PlainTips({ tips, variant }: { tips: string[]; variant: "mobile" | "web" }) {
  const reduce = useReducedMotion();
  const [i, setI] = useState(0);
  const [hover, setHover] = useState(false);
  const [tick, setTick] = useState(0); // reinicia a contagem depois de uma troca manual
  const start = useRef<{ x: number; y: number } | null>(null);
  const web = variant === "web";
  const running = !hover && !reduce && tips.length > 1;

  useEffect(() => {
    if (!running) return;
    const t = setInterval(() => {
      if (document.visibilityState === "visible") setI((n) => (n + 1) % tips.length);
    }, INTERVAL_MS);
    return () => clearInterval(t);
  }, [running, tips.length, tick]);

  const go = (to: number) => {
    setI(((to % tips.length) + tips.length) % tips.length);
    setTick((t) => t + 1);
  };

  const id = `simples-${variant}`;
  const arrow = "flex size-8 items-center justify-center rounded-lg text-hl-muted transition-colors hover:bg-white/10 hover:text-hl-fg";

  return (
    <section
      style={{ "--i": web ? 7 : 6, touchAction: web ? undefined : "pan-y" } as React.CSSProperties}
      className={
        web
          ? "rise lift hidden flex-[2_1_320px] rounded-[18px] bg-hl p-5 text-hl-fg lg:block"
          : "rise mx-5 rounded-2xl border border-line bg-card p-4 lg:hidden"
      }
      aria-labelledby={id}
      aria-roledescription="carrossel"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === "ArrowRight") go(i + 1);
        if (e.key === "ArrowLeft") go(i - 1);
      }}
      onFocus={(e) => (e.target as HTMLElement).matches(":focus-visible") && setHover(true)}
      onBlur={() => setHover(false)}
      {...(web
        ? {
            // Computador: o mouse em cima pausa.
            onPointerEnter: (e: React.PointerEvent) => e.pointerType === "mouse" && setHover(true),
            onPointerLeave: (e: React.PointerEvent) => e.pointerType === "mouse" && setHover(false),
          }
        : {
            // Celular: arrastar para o lado (só toque/caneta).
            onPointerDown: (e: React.PointerEvent) => {
              start.current = e.pointerType === "mouse" ? null : { x: e.clientX, y: e.clientY };
            },
            onPointerUp: (e: React.PointerEvent) => {
              const s = start.current;
              start.current = null;
              if (!s) return;
              const dx = e.clientX - s.x;
              if (Math.abs(dx) > SWIPE_PX && Math.abs(dx) > Math.abs(e.clientY - s.y)) go(dx < 0 ? i + 1 : i - 1);
            },
            onPointerCancel: () => (start.current = null),
          })}
    >
      <div className="flex min-h-8 items-center justify-between gap-2">
        <h2 id={id} className={`whitespace-nowrap ${web ? "text-[12px] font-bold tracking-[0.04em] text-hl-accent" : "text-[13px] font-bold text-pos"}`}>
          EM LINGUAGEM SIMPLES
        </h2>
        {tips.length > 1 &&
          (web ? (
            <div className="flex items-center gap-1">
              <button type="button" className={arrow} onClick={() => go(i - 1)} aria-label="Dica anterior">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <path d="M15 6l-6 6 6 6" />
                </svg>
              </button>
              <span className="flex gap-1 px-1" aria-hidden="true">
                {tips.map((_, n) => (
                  <span
                    key={n}
                    className={`h-1.5 rounded-full transition-all duration-300 motion-reduce:transition-none ${
                      n === i ? "w-3.5 bg-hl-accent" : "w-1.5 bg-hl-line"
                    }`}
                  />
                ))}
              </span>
              <button type="button" className={arrow} onClick={() => go(i + 1)} aria-label="Próxima dica">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <path d="M9 6l6 6-6 6" />
                </svg>
              </button>
            </div>
          ) : (
            <span className="flex gap-1" aria-hidden="true">
              {tips.map((_, n) => (
                <span
                  key={n}
                  className={`h-1.5 rounded-full transition-all duration-300 motion-reduce:transition-none ${
                    n === i ? "w-3.5 bg-pos" : "w-1.5 bg-line"
                  }`}
                />
              ))}
            </span>
          ))}
      </div>
      <div className={`grid select-none ${web ? "mt-2" : "mt-1.5"}`} aria-live={running ? "off" : "polite"}>
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
      {!web && tips.length > 1 && <p className="mt-2 text-[11px] text-muted">Arraste para o lado para ver outras dicas</p>}
      <span className="sr-only">
        Dica {i + 1} de {tips.length}. {web ? "Use as setas para trocar." : "Arraste para o lado ou use as setas do teclado."}
      </span>
    </section>
  );
}
