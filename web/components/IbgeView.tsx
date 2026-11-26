"use client";

import { useReducedMotion, motion } from "motion/react";
import { useState } from "react";
import { formatMonthShort, formatMonthYear, formatPct, formatPp, formatRollingQuarter, formatSignedPct } from "@/lib/format";
import type { Ibge } from "@/lib/schema";
import { LineChart } from "./LineChart";
import { Card } from "./ui";

type Mode = "monthly" | "yoy";

/**
 * Economia brasileira (IBGE · SIDRA): inflação por grupo e desemprego.
 * Só descreve o dado publicado — sem projeção nem relação de causa.
 */
export function IbgeView({ data, start = 0, children }: { data: Ibge; start?: number; children?: React.ReactNode }) {
  return (
    <section aria-labelledby="economia-br" className="flex flex-col gap-3 lg:gap-4">
      <div className="px-5 lg:px-0">
        <h2 id="economia-br" className="font-display text-[18px] font-semibold lg:text-[20px]">
          Economia brasileira
        </h2>
        <p className="text-[12px] text-muted">Juros (Banco Central), inflação e desemprego (IBGE) · dados oficiais</p>
      </div>
      {children}
      <div className="flex flex-col gap-3 lg:grid lg:grid-cols-[minmax(0,3fr)_minmax(0,2fr)] lg:items-start lg:gap-4">
        <InflationByGroup data={data} i={start} />
        <Unemployment data={data} i={start + 1} />
      </div>
    </section>
  );
}

function InflationByGroup({ data, i }: { data: Ibge; i: number }) {
  const [mode, setMode] = useState<Mode>("yoy");
  const reduce = useReducedMotion();
  const { month, general, groups } = data.ipca;
  const sorted = [...groups].sort((a, b) => b[mode] - a[mode]);
  const max = Math.max(...groups.map((g) => Math.abs(g[mode])), Math.abs(general[mode]), 0.01);
  const hasNeg = groups.some((g) => g[mode] < 0);

  // Frase descritiva: no mês, quem mais pressionou/aliviou (impacto = peso × variação);
  // em 12 meses, quem mais subiu e quem menos subiu.
  const byImpact = [...groups].sort((a, b) => b.impact - a.impact);
  const up = byImpact[0];
  const down = byImpact[byImpact.length - 1];
  const sentence =
    mode === "monthly" ? (
      <>
        Em {formatMonthYear(month)}, <strong className="font-semibold text-fg">{up.name}</strong> foi o grupo que mais pressionou o IPCA do mês (
        {formatPp(up.impact, 2)})
        {down.impact < 0 && (
          <>
            {" "}
            e <strong className="font-semibold text-fg">{down.name}</strong> o que mais aliviou ({formatPp(down.impact, 2)})
          </>
        )}
        .
      </>
    ) : (
      <>
        Em 12 meses, o que mais subiu foi <strong className="font-semibold text-fg">{sorted[0].name}</strong> (
        {formatSignedPct(sorted[0].yoy, 2)}) e o que menos subiu foi{" "}
        <strong className="font-semibold text-fg">{sorted[sorted.length - 1].name}</strong> ({formatSignedPct(sorted[sorted.length - 1].yoy, 2)}).
      </>
    );

  const bar = (value: number) => {
    const w = (Math.abs(value) / max) * 100;
    return hasNeg ? (
      // eixo no meio: negativos à esquerda, positivos à direita
      <span className="relative flex h-2.5 flex-1">
        <span className="absolute inset-y-0 left-1/2 w-px bg-line" aria-hidden="true" />
        <motion.span
          key={`${mode}`}
          initial={{ scaleX: 0 }}
          animate={{ scaleX: 1 }}
          transition={{ duration: reduce ? 0 : 0.4, ease: [0.2, 0.7, 0.2, 1] }}
          className="absolute inset-y-0 rounded-full bg-muted/60"
          style={value >= 0 ? { left: "50%", width: `${w / 2}%`, transformOrigin: "left" } : { right: "50%", width: `${w / 2}%`, transformOrigin: "right" }}
        />
      </span>
    ) : (
      <span className="flex h-2.5 flex-1">
        <motion.span
          key={`${mode}`}
          initial={{ scaleX: 0 }}
          animate={{ scaleX: 1 }}
          transition={{ duration: reduce ? 0 : 0.4, ease: [0.2, 0.7, 0.2, 1] }}
          className="h-full rounded-full bg-muted/60"
          style={{ width: `${w}%`, transformOrigin: "left" }}
        />
      </span>
    );
  };

  return (
    <Card i={i} className="mx-5 lg:mx-0" aria-labelledby="ipca-grupos">
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div>
          <h3 id="ipca-grupos" className="text-[15px] font-bold">
            Inflação por grupo
          </h3>
          <p className="text-[12px] text-muted">IPCA · {formatMonthYear(month)} · Fonte: IBGE</p>
        </div>
        <div role="group" aria-label="Período da inflação" className="flex rounded-[10px] bg-soft p-0.5">
          {(
            [
              ["monthly", "No mês"],
              ["yoy", "Em 12 meses"],
            ] as const
          ).map(([m, label]) => (
            <button
              key={m}
              type="button"
              aria-pressed={mode === m}
              onClick={() => setMode(m)}
              className={`min-h-9 rounded-[8px] px-3 text-[13px] font-semibold transition-colors ${mode === m ? "bg-fg text-inverse-fg" : "text-fg hover:bg-line"}`}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      <div className="mt-3 flex items-baseline justify-between gap-3 rounded-xl bg-soft px-3 py-2">
        <span className="text-[13px] font-semibold">Índice geral</span>
        <span className="num font-display text-[18px] font-semibold">{formatSignedPct(general[mode], 2)}</span>
      </div>

      <ul className="mt-3 flex flex-col gap-2.5" aria-label={`Variação por grupo, ${mode === "monthly" ? "no mês" : "em 12 meses"}`}>
        {sorted.map((g) => (
          // Celular: nome e valor na 1ª linha, barra com a largura toda embaixo. Web: 3 colunas.
          <li
            key={g.code}
            className="grid grid-cols-[minmax(0,1fr)_auto] items-center gap-x-2 gap-y-1 lg:grid-cols-[minmax(0,12rem)_1fr_4.5rem] lg:gap-y-0"
          >
            <span className="col-start-1 row-start-1 min-w-0">
              <span className="block truncate text-[13px] font-semibold">{g.name}</span>
              <span className="block text-[11px] text-muted">peso {formatPct(g.weight, 1)} do orçamento</span>
            </span>
            <span className="col-span-2 row-start-2 flex lg:col-span-1 lg:col-start-2 lg:row-start-1">{bar(g[mode])}</span>
            <span className="num col-start-2 row-start-1 text-right text-[13px] font-semibold lg:col-start-3">{formatSignedPct(g[mode], 2)}</span>
          </li>
        ))}
      </ul>

      <p className="mt-3 border-t border-line pt-2.5 text-[13px] leading-snug text-muted">{sentence}</p>
    </Card>
  );
}

function Unemployment({ data, i }: { data: Ibge; i: number }) {
  const u = data.unemployment;
  const diff = u.yearAgo === null ? null : u.value - u.yearAgo;
  const points = u.series as [string, number][];
  return (
    <Card i={i} className="mx-5 lg:mx-0" aria-labelledby="desemprego">
      <h3 id="desemprego" className="text-[15px] font-bold">
        Desemprego
      </h3>
      <p className="text-[12px] text-muted">PNAD Contínua · trimestre {formatRollingQuarter(u.date)} · Fonte: IBGE</p>
      <div className="mt-2 flex flex-wrap items-baseline gap-x-3 gap-y-1">
        <span className="num font-display text-[30px] font-semibold">{formatPct(u.value, 1)}</span>
        {diff !== null && (
          <span className="text-[13px] text-muted">
            {diff < 0 ? "menor" : diff > 0 ? "maior" : "igual"} que há um ano ({formatPct(u.yearAgo!, 1)}
            {diff !== 0 && <>, {formatPp(diff)}</>})
          </span>
        )}
      </div>
      <div className="mt-3">
        <LineChart
          series={[{ id: "desocupacao", label: "Desemprego", points, tone: "fg" }]}
          height={130}
          heightClass="h-[130px] lg:h-[180px]"
          label="Taxa de desemprego nos últimos 24 meses"
          description={`De ${formatPct(points[0][1], 1)} (${formatMonthShort(points[0][0])}) para ${formatPct(u.value, 1)} (${formatMonthShort(u.date)}).`}
          formatValue={(v) => formatPct(v, 1)}
          formatDate={formatMonthShort}
        />
      </div>
      <p className="mt-2 text-[12px] leading-snug text-muted">
        Percentual de pessoas de 14 anos ou mais que procuraram trabalho e não encontraram. Cada ponto é a média de três meses.
      </p>
    </Card>
  );
}
