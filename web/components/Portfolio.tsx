"use client";

import { useCallback, useMemo, useState } from "react";
import { PERIOD_LABEL, PERIOD_LONG, formatSignedPct } from "@/lib/format";
import { usePortfolio, usePortfolioData } from "@/lib/hooks";
import { curveReturn, portfolioCurve, seriesCurve } from "@/lib/portfolio";
import type { AssetSummary, Period, PortfolioData } from "@/lib/schema";
import { AssetLogo } from "./AssetLogo";
import { CountUp } from "./CountUp";
import { IconCheck } from "./icons";
import { LineChart, type ChartSeries } from "./LineChart";
import { PeriodPicker } from "./PeriodPicker";
import { ScatterChart } from "./ScatterChart";
import { Sheet } from "./Sheet";
import { Card, Chip, ErrorNote } from "./ui";

type Props = {
  candidates: AssetSummary[];
  defaults: string[];
  benchmark: { slug: string; name: string };
  initial: PortfolioData;
};

const fmtB100 = (v: number) => formatSignedPct(v - 100);

export function Portfolio({ candidates, defaults, benchmark, initial }: Props) {
  const candidateSlugs = useMemo(() => candidates.map((c) => c.slug), [candidates]);
  const [slugs, save] = usePortfolio(candidateSlugs, defaults);
  const [period, setPeriod] = useState<Period>(initial.period);
  const [editing, setEditing] = useState(false);
  const [riskOpen, setRiskOpen] = useState(false);
  const state = usePortfolioData(period, initial);
  const bySlug = useMemo(() => Object.fromEntries(candidates.map((c) => [c.slug, c])), [candidates]);
  const selected = slugs.map((s) => bySlug[s]).filter(Boolean);

  const curve = useMemo(() => (state.status === "ready" ? portfolioCurve(state.data, slugs) : []), [state, slugs]);
  const bench = useMemo(() => (state.status === "ready" ? seriesCurve(state.data, benchmark.slug) : []), [state, benchmark.slug]);
  const ret =
    period === "1d"
      ? selected.reduce((a, s) => a + s.stats["1d"].ret, 0) / Math.max(1, selected.length)
      : curveReturn(curve);
  const scatter = selected.map((s) => ({ id: s.slug, label: s.ticker, risk: s.stats[period].vol, ret: s.stats[period].ret }));

  const perfSeries: ChartSeries[] = [
    { id: "carteira", label: "Minha carteira", points: curve, tone: "pos", area: true, width: 3 },
    { id: benchmark.slug, label: benchmark.name, points: bench, tone: "fg", dashed: true },
  ];
  const perfDesc = `Minha carteira ${formatSignedPct(ret)} ${PERIOD_LONG[period]}; ${benchmark.name} ${formatSignedPct(curveReturn(bench))}.`;
  const fmtRet = useCallback((v: number) => formatSignedPct(v), []);

  const chart = (h: number) =>
    state.status === "error" ? (
      <ErrorNote>Não foi possível carregar o período. Tente outro período ou recarregue a página.</ErrorNote>
    ) : state.status === "loading" ? (
      <div className="skeleton w-full" style={{ height: h }} aria-label="Carregando gráfico" />
    ) : (
      <LineChart series={perfSeries} height={h} label={`Carteira comparada ao ${benchmark.name}, base 100`} description={perfDesc} animKey={`${period}-${slugs.join()}`} formatValue={fmtB100} />
    );

  const legend = (
    <div className="mt-2 flex gap-4 text-[13px] text-muted">
      <span className="font-bold text-pos">— Minha carteira</span>
      <span className="font-bold text-fg">- - {benchmark.name}</span>
    </div>
  );

  return (
    <>
      {/* ── Mobile: card de destaque ─────────────────────────────── */}
      <section
        style={{ "--i": 2 } as React.CSSProperties}
        className="rise mx-5 rounded-[20px] bg-hl p-[18px] text-hl-fg lg:hidden"
        aria-labelledby="carteira-m"
      >
        <h2 id="carteira-m" className="text-[13px] font-semibold text-hl-muted">
          Minha carteira
        </h2>
        <div className="num mt-1 mb-0.5 font-display text-[32px] font-semibold">
          <CountUp value={ret} format={fmtRet} />
        </div>
        <div className="text-[13px] text-hl-muted">
          {PERIOD_LONG[period]}, base 100 · {selected.length} {selected.length === 1 ? "ativo" : "ativos"}
        </div>
        {state.status === "ready" ? (
          <LineChart
            series={[{ id: "carteira", label: "Minha carteira", points: curve, tone: "accent" }]}
            height={70}
            label={ret >= 0 ? "Carteira em alta no período" : "Carteira em queda no período"}
            animKey={`${period}-${slugs.join()}`}
            formatValue={fmtB100}
          />
        ) : (
          <div className="h-[70px]" />
        )}
        <div className="mt-2 flex gap-2">
          <button
            type="button"
            onClick={() => setEditing(true)}
            className="min-h-11 flex-1 rounded-xl bg-hl-accent text-[14px] font-bold text-[#0E2A22]"
          >
            Editar ativos
          </button>
          <button
            type="button"
            onClick={() => setRiskOpen(true)}
            className="min-h-11 flex-1 rounded-xl border border-hl-line text-[14px] font-semibold text-hl-fg"
          >
            Risco x retorno
          </button>
        </div>
      </section>

      {/* ── Web: desempenho (2/3) + risco x retorno (1/3) ────────── */}
      <div className="hidden flex-wrap gap-4 lg:flex">
        <Card i={5} className="min-w-0 flex-[2_1_420px]" aria-labelledby="perf-w">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 id="perf-w" className="text-[13px] font-semibold text-muted">
                Desempenho relativo (base 100)
              </h2>
              <div className="num mt-0.5 flex items-center gap-2 font-display text-[30px] font-semibold">
                <CountUp value={ret} format={fmtRet} />
                <Chip value={ret} suffix={PERIOD_LABEL[period]} />
              </div>
            </div>
            <PeriodPicker value={period} onChange={setPeriod} label="Período da carteira" />
          </div>
          <div className="mt-4">{chart(200)}</div>
          {legend}
        </Card>
        <Card i={6} className="flex min-w-0 flex-[1_1_280px] flex-col" aria-labelledby="risk-w">
          <h2 id="risk-w" className="text-[13px] font-semibold text-muted">
            Risco x retorno
          </h2>
          <ScatterChart points={scatter} label={`Risco contra retorno dos ativos da carteira, ${PERIOD_LONG[period]}`} />
          <button
            type="button"
            onClick={() => setEditing(true)}
            className="mt-auto min-h-11 w-full rounded-xl bg-primary text-[14px] font-bold text-primary-fg"
          >
            Editar ativos da carteira
          </button>
        </Card>
      </div>

      {/* ── Mobile: risco x retorno e desempenho em painel ───────── */}
      <Sheet open={riskOpen} onClose={() => setRiskOpen(false)} title="Risco x retorno">
        <PeriodPicker value={period} onChange={setPeriod} variant="pill" label="Período da carteira" />
        <div className="mt-4 text-[13px] font-semibold text-muted">Desempenho relativo (base 100)</div>
        <div className="num mt-0.5 flex items-center gap-2 font-display text-[24px] font-semibold">
          {formatSignedPct(ret)} <Chip value={ret} suffix={PERIOD_LABEL[period]} />
        </div>
        <div className="mt-3">{chart(150)}</div>
        {legend}
        <div className="mt-5 text-[13px] font-semibold text-muted">Volatilidade x retorno {PERIOD_LONG[period]}</div>
        <ScatterChart points={scatter} label={`Risco contra retorno dos ativos da carteira, ${PERIOD_LONG[period]}`} />
      </Sheet>

      <Sheet open={editing} onClose={() => setEditing(false)} title="Editar ativos da carteira">
        <EditList candidates={candidates} selected={slugs} onSave={save} />
      </Sheet>
    </>
  );
}

function EditList({ candidates, selected, onSave }: { candidates: AssetSummary[]; selected: string[]; onSave: (s: string[]) => void }) {
  const toggle = (slug: string) => {
    const on = selected.includes(slug);
    if (on && selected.length === 1) return; // ao menos 1 ativo
    const next = on ? selected.filter((s) => s !== slug) : [...selected, slug];
    onSave(candidates.map((c) => c.slug).filter((s) => next.includes(s)));
  };
  const groups = [
    { title: "Brasil", items: candidates.filter((c) => c.group === "brasil") },
    { title: "Mundo", items: candidates.filter((c) => c.group === "mundo") },
    { title: "Cripto", items: candidates.filter((c) => c.group === "cripto") },
  ];
  return (
    <div className="flex flex-col gap-4">
      <p className="text-[14px] text-muted">
        Escolha os ativos que entram na sua carteira. A seleção fica salva neste navegador. Pesos iguais, base 100.
      </p>
      {groups.map((g) => (
        <fieldset key={g.title}>
          <legend className="mb-2 text-[12px] font-bold tracking-[0.04em] text-pos">{g.title.toUpperCase()}</legend>
          <div className="flex flex-col gap-1">
            {g.items.map((c) => {
              const on = selected.includes(c.slug);
              return (
                <label key={c.slug} className="flex min-h-11 cursor-pointer items-center gap-3 rounded-xl px-2 hover:bg-soft">
                  <input type="checkbox" className="peer sr-only" checked={on} onChange={() => toggle(c.slug)} />
                  <span
                    aria-hidden="true"
                    className={`flex size-6 items-center justify-center rounded-md border peer-focus-visible:outline-2 peer-focus-visible:outline-pos ${
                      on ? "border-pos bg-pos text-card" : "border-line"
                    }`}
                  >
                    {on && <IconCheck size={16} />}
                  </span>
                  <AssetLogo logo={c.logo} ticker={c.ticker} size={32} />
                  <span className="flex-1 text-[15px] font-semibold">{c.name}</span>
                  <span className="text-[13px] text-muted">{c.ticker}</span>
                </label>
              );
            })}
          </div>
        </fieldset>
      ))}
    </div>
  );
}
