"use client";

import { useReducedMotion } from "motion/react";
import { useEffect, useRef, useState } from "react";

const INTERVAL_MS = 8000;
const SWIPE_PX = 40;

/**
 * "Em linguagem simples" com dicas que se alternam.
 * - todas as frases ficam empilhadas na mesma célula do grid: o card assume a
 *   altura da maior e não "pula" ao trocar (sem layout shift);
 * - troca a cada 8 s; pausa com o mouse em cima, com foco de teclado ou com a aba em segundo plano;
 * - arrastar para o lado troca de dica (qualquer tela; pensado para o toque);
 * - pontinhos discretos mostram a posição; com movimento reduzido não gira sozinho.
 */
export function PlainTips({ tips, variant }: { tips: string[]; variant: "mobile" | "web" }) {
  const reduce = useReducedMotion();
  const [i, setI] = useState(0);
  const [hover, setHover] = useState(false);
  const [tick, setTick] = useState(0); // reinicia o intervalo depois de um arraste
  const start = useRef<{ x: number; y: number } | null>(null);
  const running = !hover && !reduce && tips.length > 1;

  useEffect(() => {
    if (!running) return;
    const t = setInterval(() => {
      if (document.visibilityState === "visible") setI((n) => (n + 1) % tips.length);
    }, INTERVAL_MS);
    return () => clearInterval(t);
  }, [running, tips.length, tick]);

  const go = (d: number) => {
    setI((n) => (n + d + tips.length) % tips.length);
    setTick((t) => t + 1);
  };

  const web = variant === "web";
  const id = `simples-${variant}`;

  return (
    <section
      style={{ "--i": web ? 7 : 6, touchAction: "pan-y" } as React.CSSProperties}
      className={
        web
          ? "rise lift hidden flex-[2_1_320px] rounded-[18px] bg-hl p-5 text-hl-fg lg:block"
          : "rise lift mx-5 rounded-2xl border border-line bg-card p-4 lg:hidden"
      }
      aria-labelledby={id}
      aria-roledescription="carrossel"
      onPointerEnter={(e) => e.pointerType === "mouse" && setHover(true)}
      onPointerLeave={(e) => e.pointerType === "mouse" && setHover(false)}
      onFocus={(e) => (e.target as HTMLElement).matches(":focus-visible") && setHover(true)}
      onBlur={() => setHover(false)}
      onPointerDown={(e) => {
        start.current = { x: e.clientX, y: e.clientY };
      }}
      onPointerUp={(e) => {
        const s = start.current;
        start.current = null;
        if (!s) return;
        const dx = e.clientX - s.x;
        if (Math.abs(dx) > SWIPE_PX && Math.abs(dx) > Math.abs(e.clientY - s.y)) go(dx < 0 ? 1 : -1);
      }}
      onPointerCancel={() => (start.current = null)}
      onKeyDown={(e) => {
        if (e.key === "ArrowRight") go(1);
        if (e.key === "ArrowLeft") go(-1);
      }}
      tabIndex={0}
    >
      <div className="flex items-center justify-between gap-2">
        <h2 id={id} className={web ? "text-[12px] font-bold tracking-[0.04em] text-hl-accent" : "text-[13px] font-bold text-pos"}>
          EM LINGUAGEM SIMPLES
        </h2>
        {tips.length > 1 && (
          <span className="flex gap-1" aria-hidden="true">
            {tips.map((_, n) => (
              <span
                key={n}
                className={`h-1.5 rounded-full transition-all duration-300 motion-reduce:transition-none ${
                  n === i ? `w-3.5 ${web ? "bg-hl-accent" : "bg-pos"}` : `w-1.5 ${web ? "bg-hl-line" : "bg-line"}`
                }`}
              />
            ))}
          </span>
        )}
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
      <span className="sr-only">
        Dica {i + 1} de {tips.length}. Arraste para o lado ou use as setas do teclado para trocar.
      </span>
    </section>
  );
}
