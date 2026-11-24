"use client";

import { motion, useReducedMotion } from "motion/react";
import { useId, useLayoutEffect, useMemo, useRef, useState } from "react";
import { formatShortDate } from "@/lib/format";

export type ChartSeries = {
  id: string;
  label: string;
  points: [string, number][];
  tone: "pos" | "fg" | "accent" | "cdi" | "ipca";
  dashed?: boolean | string; // true = "6 4"; string = padrão próprio (ex.: "2 3")
  area?: boolean;
  width?: number;
};

const STROKE = { pos: "var(--pos)", fg: "var(--fg)", accent: "var(--hl-accent)", cdi: "var(--series-cdi)", ipca: "var(--series-ipca)" } as const;

const useIsoLayoutEffect = typeof window === "undefined" ? () => {} : useLayoutEffect;

/**
 * Gráfico de linha em SVG próprio (visual idêntico ao mockup).
 * - largura medida (ResizeObserver) → viewBox na proporção real, traço sem distorção;
 * - linha desenhada com pathLength na primeira exibição e a cada troca de período (animKey);
 * - role="img" + descrição textual; ponteiro/toque mostra data e valor.
 */
export function LineChart({
  series,
  height = 130,
  label,
  description,
  animKey,
  formatValue,
  baseline,
  heightClass,
}: {
  series: ChartSeries[];
  height?: number;
  label: string;
  description?: string;
  animKey?: string;
  formatValue: (v: number) => string;
  baseline?: number;
  /** Altura responsiva via CSS (ex.: "h-[130px] lg:h-[260px]"); medida e aplicada ao viewBox. */
  heightClass?: string;
}) {
  const wrap = useRef<HTMLDivElement>(null);
  const [w, setW] = useState(342);
  const [mh, setMh] = useState<number | null>(null);
  const [hover, setHover] = useState<number | null>(null);
  const reduce = useReducedMotion();
  const gid = useId();

  useIsoLayoutEffect(() => {
    const el = wrap.current;
    if (!el) return;
    const ro = new ResizeObserver(([e]) => {
      setW(Math.max(120, Math.round(e.contentRect.width)));
      if (heightClass) setMh(Math.max(60, Math.round(e.contentRect.height)));
    });
    ro.observe(el);
    return () => ro.disconnect();
  }, [heightClass]);
  height = heightClass && mh ? mh : height;

  const geo = useMemo(() => {
    const all = series.flatMap((s) => s.points.map((p) => p[1]));
    if (baseline !== undefined) all.push(baseline);
    if (all.length === 0) return null;
    let min = Math.min(...all);
    let max = Math.max(...all);
    if (min === max) {
      min -= 1;
      max += 1;
    }
    const pad = (max - min) * 0.08;
    min -= pad;
    max += pad;
    const top = 4;
    const bottom = height - 4;
    // eixo x por índice de data comum (todas as séries compartilham o calendário mais longo)
    const longest = series.reduce((a, s) => (s.points.length > a.length ? s.points : a), series[0]?.points ?? []);
    const dates = longest.map((p) => p[0]);
    const xIndex = new Map(dates.map((d, i) => [d, i] as const));
    const n = Math.max(1, dates.length - 1);
    const x = (d: string, fallbackIdx: number) => ((xIndex.get(d) ?? fallbackIdx) / n) * (w - 4) + 2;
    const y = (v: number) => bottom - ((v - min) / (max - min)) * (bottom - top);
    const paths = series.map((s) => {
      const pts = s.points.map((p, i) => [x(p[0], i), y(p[1])] as const);
      const line = pts.map(([px, py], i) => `${i ? "L" : "M"}${px.toFixed(1)},${py.toFixed(1)}`).join(" ");
      const area = pts.length ? `${line} L${pts[pts.length - 1][0].toFixed(1)},${height} L${pts[0][0].toFixed(1)},${height} Z` : "";
      return { s, pts, line, area };
    });
    return { paths, dates, x, y };
  }, [series, w, height, baseline]);

  if (!geo || geo.dates.length < 2) {
    return (
      <div role="img" aria-label={`${label}: sem dados suficientes no período`} className="flex items-center justify-center rounded-xl bg-soft text-[13px] text-muted" style={{ height }}>
        Sem dados suficientes no período
      </div>
    );
  }

  const onMove = (clientX: number) => {
    const r = wrap.current?.getBoundingClientRect();
    if (!r) return;
    const ratio = Math.min(1, Math.max(0, (clientX - r.left) / r.width));
    setHover(Math.round(ratio * (geo.dates.length - 1)));
  };

  const hd = hover !== null ? geo.dates[hover] : null;
  const hx = hd ? geo.x(hd, hover!) : 0;

  return (
    <div
      ref={wrap}
      className={`relative w-full touch-pan-y select-none ${heightClass ?? ""}`}
      onPointerMove={(e) => onMove(e.clientX)}
      onPointerDown={(e) => onMove(e.clientX)}
      onPointerLeave={() => setHover(null)}
    >
      <svg
        viewBox={`0 0 ${w} ${height}`}
        preserveAspectRatio="none"
        width="100%"
        height={heightClass ? "100%" : height}
        role="img"
        aria-label={label}
        aria-describedby={description ? `${gid}-d` : undefined}
        className="block overflow-visible"
      >
        {geo.paths.map(({ s, area }) =>
          s.area ? (
            <motion.path
              key={`${s.id}-area-${animKey}`}
              d={area}
              fill={s.tone === "pos" ? "var(--pos-soft)" : "transparent"}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: reduce ? 0 : 0.5, delay: reduce ? 0 : 0.3 }}
            />
          ) : null,
        )}
        {baseline !== undefined && (
          <line x1={0} x2={w} y1={geo.y(baseline)} y2={geo.y(baseline)} stroke="var(--line)" strokeWidth={1} strokeDasharray="3 4" />
        )}
        {geo.paths.map(({ s, line }) => (
          <motion.path
            key={`${s.id}-${animKey}`}
            d={line}
            fill="none"
            stroke={STROKE[s.tone]}
            strokeWidth={s.width ?? 2.5}
            strokeLinejoin="round"
            strokeLinecap="round"
            strokeDasharray={s.dashed === true ? "6 4" : s.dashed || undefined}
            initial={s.dashed ? false : { pathLength: 0 }}
            animate={s.dashed ? undefined : { pathLength: 1 }}
            transition={{ duration: reduce ? 0 : 0.8, ease: [0.2, 0.7, 0.2, 1] }}
          />
        ))}
        {hd && (
          <g aria-hidden="true">
            <line x1={hx} x2={hx} y1={0} y2={height} stroke="var(--muted)" strokeWidth={1} />
            {geo.paths.map(({ s, pts }) => {
              const i = s.points.findIndex((p) => p[0] === hd);
              if (i < 0) return null;
              return <circle key={s.id} cx={pts[i][0]} cy={pts[i][1]} r={4} fill={STROKE[s.tone]} stroke="var(--card)" strokeWidth={2} />;
            })}
          </g>
        )}
      </svg>
      {hd && (
        <div
          aria-hidden="true"
          className="pointer-events-none absolute -top-2 z-10 whitespace-nowrap rounded-lg border border-line bg-card px-2 py-1 text-[12px] shadow-sm"
          style={{ left: Math.min(Math.max(hx, 60), w - 60), transform: "translate(-50%, -100%)" }}
        >
          <div className="font-semibold text-muted">{formatShortDate(hd)}</div>
          {series.map((s) => {
            const p = s.points.find((q) => q[0] === hd);
            return p ? (
              <div key={s.id} className="num font-bold">
                {series.length > 1 ? `${s.label}: ` : ""}
                {formatValue(p[1])}
              </div>
            ) : null;
          })}
        </div>
      )}
      {description && (
        <p id={`${gid}-d`} className="sr-only">
          {description}
        </p>
      )}
    </div>
  );
}
