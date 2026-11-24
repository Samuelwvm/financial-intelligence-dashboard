"use client";

import { motion, useReducedMotion } from "motion/react";
import { useLayoutEffect, useMemo, useRef, useState } from "react";
import { formatSignedPct } from "@/lib/format";

export type ScatterPoint = { id: string; label: string; risk: number; ret: number; reference?: boolean };

const useIsoLayoutEffect = typeof window === "undefined" ? () => {} : useLayoutEffect;
const pct = (v: number) => `${Math.round(v)}%`.replace("-0%", "0%");

/** Escala "bonita" (passos de 1, 2, 2,5, 5 × 10^n) cobrindo [min, max]. */
function niceTicks(min: number, max: number, count = 4): number[] {
  const span = max - min || 1;
  const raw = span / count;
  const pow = 10 ** Math.floor(Math.log10(raw));
  const step = [1, 2, 2.5, 5, 10].map((m) => m * pow).find((s) => s >= raw) ?? raw;
  const start = Math.floor(min / step) * step;
  const ticks: number[] = [];
  for (let v = start; v <= max + step * 0.001; v += step) ticks.push(Number(v.toFixed(6)));
  if (ticks[ticks.length - 1] < max) ticks.push(ticks[ticks.length - 1] + step);
  return ticks;
}

/**
 * Risco (volatilidade anualizada, eixo x) × retorno no período (eixo y).
 * Eixos com valores, linha do 0%, Ibovespa como referência (ponto vazado),
 * rótulos sem sobreposição e detalhe ao tocar/passar o mouse.
 */
export function ScatterChart({ points, label, height = 220 }: { points: ScatterPoint[]; label: string; height?: number }) {
  const reduce = useReducedMotion();
  const wrap = useRef<HTMLDivElement>(null);
  const [w, setW] = useState(320);
  const [active, setActive] = useState<string | null>(null);

  useIsoLayoutEffect(() => {
    const el = wrap.current;
    if (!el) return;
    const ro = new ResizeObserver(([e]) => setW(Math.max(220, Math.round(e.contentRect.width))));
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  const g = useMemo(() => {
    if (points.length === 0) return null;
    const L = 38; // rótulos do eixo y
    const R = 8;
    const T = 18;
    const B = 34; // rótulos do eixo x + título
    const xT = niceTicks(0, Math.max(...points.map((p) => p.risk)) * 1.05);
    const ys = points.map((p) => p.ret);
    const yT = niceTicks(Math.min(0, ...ys), Math.max(0, ...ys));
    const x0 = xT[0];
    const x1 = xT[xT.length - 1];
    const y0 = yT[0];
    const y1 = yT[yT.length - 1];
    const x = (v: number) => L + ((v - x0) / (x1 - x0 || 1)) * (w - L - R);
    const y = (v: number) => height - B - ((v - y0) / (y1 - y0 || 1)) * (height - B - T);
    // Rótulos à direita do ponto (à esquerda perto da borda); quem colide desce.
    const placed = points
      .map((p) => {
        const cx = x(p.risk);
        const cy = y(p.ret);
        return { p, cx, cy, ly: cy, right: cx < w - 72 };
      })
      .sort((a, b) => a.cy - b.cy);
    placed.forEach((cur, i) => {
      for (let j = 0; j < i; j++) {
        const prev = placed[j];
        if (prev.right === cur.right && Math.abs(prev.cx - cur.cx) < 64 && cur.ly - prev.ly < 13) cur.ly = prev.ly + 13;
      }
    });
    return { L, R, T, B, xT, yT, x, y, placed };
  }, [points, w, height]);

  if (!g) {
    return <div className="flex h-[200px] items-center justify-center text-[13px] text-muted">Escolha ativos para comparar</div>;
  }

  const desc = points
    .map((p) => `${p.label}: retorno ${formatSignedPct(p.ret)}, volatilidade ${p.risk.toFixed(1).replace(".", ",")}%`)
    .join("; ");
  const act = g.placed.find((q) => q.p.id === active);
  const plotLeft = g.L;
  const plotRight = w - g.R;
  const plotTop = g.T;
  const plotBottom = height - g.B;

  return (
    <div ref={wrap} className="relative mt-3 mb-6 w-full select-none" onPointerLeave={() => setActive(null)}>
      <svg viewBox={`0 0 ${w} ${height}`} width="100%" height={height} role="img" aria-label={`${label}. ${desc}`} className="block overflow-visible">
        {/* grade e eixos */}
        {g.yT.map((t) => (
          <g key={`y${t}`}>
            <line
              x1={plotLeft}
              x2={plotRight}
              y1={g.y(t)}
              y2={g.y(t)}
              stroke={t === 0 ? "var(--muted)" : "var(--line)"}
              strokeOpacity={t === 0 ? 0.5 : 1}
              strokeWidth={1}
              strokeDasharray={t === 0 ? undefined : "2 4"}
            />
            <text x={plotLeft - 6} y={g.y(t) + 4} fontSize={10} fill="var(--muted)" textAnchor="end">
              {pct(t)}
            </text>
          </g>
        ))}
        {g.xT.map((t) => (
          <text key={`x${t}`} x={g.x(t)} y={plotBottom + 14} fontSize={10} fill="var(--muted)" textAnchor="middle">
            {pct(t)}
          </text>
        ))}
        <line x1={plotLeft} x2={plotLeft} y1={plotTop} y2={plotBottom} stroke="var(--line)" strokeWidth={1.5} />
        <text x={plotRight} y={height - 3} fontSize={11} textAnchor="end" fill="var(--muted)">
          Volatilidade (risco) →
        </text>
        <text x={2} y={9} fontSize={11} fill="var(--muted)">
          Retorno ↑
        </text>
        {/* pontos */}
        {g.placed.map(({ p, cx, cy, ly, right }, i) => {
          const color = p.reference ? "var(--fg)" : p.ret >= 0 ? "var(--pos)" : "var(--neg)";
          const dim = active !== null && active !== p.id;
          return (
            <motion.g
              key={p.id}
              initial={{ opacity: 0, scale: 0.6 }}
              animate={{ opacity: dim ? 0.35 : 1, scale: 1 }}
              transition={{ duration: reduce ? 0 : 0.3, delay: reduce ? 0 : i * 0.04 }}
              style={{ transformOrigin: `${cx}px ${cy}px` }}
              onPointerEnter={() => setActive(p.id)}
              onPointerDown={() => setActive(p.id)}
            >
              <circle cx={cx} cy={cy} r={14} fill="transparent" />
              {p.reference ? (
                <circle cx={cx} cy={cy} r={6} fill="var(--card)" stroke={color} strokeWidth={2} />
              ) : (
                <circle cx={cx} cy={cy} r={6.5} fill={color} stroke="var(--card)" strokeWidth={1.5} />
              )}
              <text x={right ? cx + 10 : cx - 10} y={ly + 4} fontSize={11.5} fontWeight={p.reference ? 500 : 600} fill="var(--fg)" textAnchor={right ? "start" : "end"}>
                {p.label}
              </text>
            </motion.g>
          );
        })}
      </svg>
      {act && (
        <div
          aria-hidden="true"
          className="pointer-events-none absolute z-10 whitespace-nowrap rounded-lg border border-line bg-card px-2 py-1 text-[12px] shadow-sm"
          style={{ left: Math.min(Math.max(act.cx, 90), w - 90), top: act.cy - 10, transform: "translate(-50%, -100%)" }}
        >
          <div className="font-bold">{act.p.label}</div>
          <div className="num text-muted">
            Retorno <span className={act.p.ret >= 0 ? "font-semibold text-pos" : "font-semibold text-neg"}>{formatSignedPct(act.p.ret)}</span> ·
            Volatilidade {act.p.risk.toFixed(1).replace(".", ",")}%
          </div>
        </div>
      )}
      <p className="mt-2 border-t border-line pt-2 text-[12px] leading-snug text-muted">
        Quanto mais <strong className="font-semibold text-fg">para cima e para a esquerda</strong>, mais retorno com menos risco.
      </p>
    </div>
  );
}

/** Legenda do risco x retorno — fica ao lado do título do card. */
export function ScatterLegend({ reference = true }: { reference?: boolean }) {
  return (
    <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-[11px] text-muted">
      <span>
        <span className="mr-1 inline-block size-2 rounded-full bg-pos align-middle" aria-hidden="true" />
        em alta
      </span>
      <span>
        <span className="mr-1 inline-block size-2 rounded-full bg-neg align-middle" aria-hidden="true" />
        em queda
      </span>
      {reference && (
        <span>
          <span className="mr-1 inline-block size-2 rounded-full border-2 border-fg align-middle" aria-hidden="true" />
          Ibovespa
        </span>
      )}
    </div>
  );
}
