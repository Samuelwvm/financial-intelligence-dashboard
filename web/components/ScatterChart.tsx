"use client";

import { motion, useReducedMotion } from "motion/react";
import { formatSignedPct } from "@/lib/format";

export type ScatterPoint = { id: string; label: string; risk: number; ret: number };

/** Risco (volatilidade) × retorno — mesma geometria do mockup web (viewBox 300×200). */
export function ScatterChart({ points, label }: { points: ScatterPoint[]; label: string }) {
  const reduce = useReducedMotion();
  const W = 300;
  const H = 200;
  const left = 30;
  const bottom = 180;
  const right = 280;
  const top = 18;
  if (points.length === 0) {
    return <div className="flex h-[200px] items-center justify-center text-[13px] text-muted">Escolha ativos para comparar</div>;
  }
  const xs = points.map((p) => p.risk);
  const ys = points.map((p) => p.ret);
  const xMax = Math.max(...xs) * 1.1 || 1;
  const yMin = Math.min(0, ...ys);
  const yMax = Math.max(0, ...ys);
  const ySpan = yMax - yMin || 1;
  const x = (v: number) => left + 14 + (v / xMax) * (right - left - 28);
  const y = (v: number) => bottom - 12 - ((v - yMin) / ySpan) * (bottom - top - 24);
  // Rótulos sem sobreposição: empurra para baixo os que colidem (mesma faixa horizontal).
  const placed = points
    .map((p) => ({ p, cx: x(p.risk), cy: y(p.ret), ly: y(p.ret) }))
    .sort((a, b) => a.cy - b.cy);
  placed.forEach((cur, i) => {
    for (let j = 0; j < i; j++) {
      const prev = placed[j];
      if (Math.abs(prev.cx - cur.cx) < 70 && cur.ly - prev.ly < 14) cur.ly = prev.ly + 14;
    }
  });
  const desc = points.map((p) => `${p.label}: volatilidade ${p.risk.toFixed(1).replace(".", ",")}%, retorno ${formatSignedPct(p.ret)}`).join("; ");

  return (
    <svg viewBox={`0 0 ${W} ${H}`} width="100%" height={H} role="img" aria-label={`${label}. ${desc}`} className="mt-3 block overflow-visible">
      <path d={`M${left},10 V${bottom} H290`} fill="none" stroke="var(--line)" strokeWidth={2} />
      {yMin < 0 && (
        <line x1={left} x2={290} y1={y(0)} y2={y(0)} stroke="var(--line)" strokeWidth={1} strokeDasharray="3 4" />
      )}
      {placed.map(({ p, cx, cy, ly }, i) => {
        const anchor = cx > 230 ? "end" : "start";
        return (
          <motion.g
            key={p.id}
            initial={{ opacity: 0, scale: 0.6 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: reduce ? 0 : 0.35, delay: reduce ? 0 : i * 0.05 }}
            style={{ transformOrigin: `${cx}px ${cy}px` }}
          >
            <circle cx={cx} cy={cy} r={7} fill={p.ret >= 0 ? "var(--pos)" : "var(--neg)"} />
            <text x={anchor === "end" ? cx - 12 : cx + 12} y={ly + 4} fontSize={12} fontWeight={600} fill="var(--fg)" textAnchor={anchor}>
              {p.label}
            </text>
          </motion.g>
        );
      })}
      <text x={290} y={196} fontSize={11} textAnchor="end" fill="var(--muted)">
        Risco →
      </text>
      <text x={4} y={14} fontSize={11} fill="var(--muted)">
        Retorno ↑
      </text>
    </svg>
  );
}
