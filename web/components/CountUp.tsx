"use client";

import { animate, useReducedMotion } from "motion/react";
import { useEffect, useRef } from "react";

/**
 * Contagem curta (0,6 s) até o valor. A pré-renderização já traz o valor final
 * (sem JS, leitores de tela e buscadores leem o número certo); a animação só
 * roda uma vez, no primeiro valor, e respeita prefers-reduced-motion.
 */
export function CountUp({ value, format, className }: { value: number; format: (v: number) => string; className?: string }) {
  const ref = useRef<HTMLSpanElement>(null);
  const reduce = useReducedMotion();
  const done = useRef(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    if (reduce || done.current) {
      el.textContent = format(value);
      return;
    }
    done.current = true;
    const from = value * 0.85;
    const controls = animate(from, value, {
      duration: 0.6,
      ease: [0.2, 0.7, 0.2, 1],
      onUpdate: (v) => {
        el.textContent = format(v);
      },
    });
    return () => controls.stop();
  }, [value, format, reduce]);

  return (
    <span ref={ref} className={className}>
      {format(value)}
    </span>
  );
}
