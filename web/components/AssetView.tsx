"use client";

import { useCallback, useMemo, useState } from "react";
import { PERIOD_LONG, formatPrice, formatSignedPct } from "@/lib/format";
import { usePortfolio } from "@/lib/hooks";
import type { AssetSeries, AssetSummary, Period } from "@/lib/schema";
import { LineChart } from "./LineChart";
import { PeriodPicker } from "./PeriodPicker";
import { Card, Chip, Stat } from "./ui";

function meaning(a: AssetSummary, period: Period) {
  const s = a.stats[period];
  const vol = s.vol.toFixed(1).replace(".", ",");
  const level = s.vol < 15 ? "baixa" : s.vol < 35 ? "moderada" : "alta";
  const move = period === "1d" ? `${formatSignedPct(s.ret, 2)} no último pregão` : `${formatSignedPct(s.ret)} ${PERIOD_LONG[period]}`;
  return {
    base: "Volatilidade mede o quanto o preço balança. Quanto maior, maior o risco de variações bruscas, para cima ou para baixo.",
    detail: `${a.name} variou ${move}, com volatilidade ${level} (${vol}% ao ano).`,
  };
}

export function AssetView({
  asset,
  series,
  portfolio,
}: {
  asset: AssetSummary;
  series: AssetSeries;
  portfolio: { candidates: string[]; defaults: string[] } | null;
}) {
  const [period, setPeriod] = useState<Period>("30d");
  const stats = asset.stats[period];
  const points = series.periods[period].points as [string, number][];
  const fmt = useCallback((v: number) => formatPrice(v, asset.currency), [asset.currency]);
  const m = meaning(asset, period);
  const chipDigits = period === "1d" ? 2 : 1;

  return (
    <div className="flex flex-col gap-3 lg:grid lg:grid-cols-[minmax(0,2fr)_minmax(280px,1fr)] lg:items-start lg:gap-4">
      <Card i={0} className="mx-5 lg:mx-0" aria-label={`Preço de ${asset.name}`}>
        <div className="flex items-center justify-between gap-3">
          {/* Sem contagem animada aqui: o preço é o maior elemento da tela (LCP). */}
          <div className="num font-display text-[30px] font-semibold">{fmt(asset.price)}</div>
          <Chip value={stats.ret} digits={chipDigits} />
        </div>
        <div className="mt-3 mb-1 lg:mt-4">
          <LineChart
            series={[{ id: asset.slug, label: asset.name, points, tone: "pos", area: true }]}
            height={130}
            heightClass="h-[130px] lg:h-[260px]"
            label={`Gráfico do preço de ${asset.name} ${PERIOD_LONG[period]}`}
            description={`De ${fmt(points[0][1])} para ${fmt(points[points.length - 1][1])}; máxima ${fmt(stats.high)}, mínima ${fmt(stats.low)}.`}
            animKey={period}
            formatValue={fmt}
          />
        </div>
        <div className="mt-2">
          <PeriodPicker value={period} onChange={setPeriod} stretch label={`Período do gráfico de ${asset.name}`} />
        </div>
      </Card>

      <div className="flex flex-col gap-3 lg:gap-4">
        <div className="flex gap-2 px-5 lg:px-0" style={{ "--i": 1 } as React.CSSProperties}>
          <Stat label="Máxima" value={fmt(stats.high)} />
          <Stat label="Mínima" value={fmt(stats.low)} />
          <Stat label="Volatilidade" value={`${stats.vol.toFixed(1).replace(".", ",")}%`} />
        </div>
        <Card i={2} className="mx-5 lg:mx-0" aria-labelledby="significa">
          <h2 id="significa" className="text-[13px] font-bold text-pos">
            O QUE ISSO SIGNIFICA?
          </h2>
          <p className="mt-1.5 text-[15px] leading-[1.45]">{m.base}</p>
          <p className="mt-2 text-[14px] leading-[1.45] text-muted">{m.detail}</p>
        </Card>
        {portfolio && <AddToPortfolio slug={asset.slug} {...portfolio} />}
      </div>
    </div>
  );
}

function AddToPortfolio({ slug, candidates, defaults }: { slug: string; candidates: string[]; defaults: string[] }) {
  const stableCandidates = useMemo(() => candidates, [candidates]);
  const [slugs, save] = usePortfolio(stableCandidates, defaults);
  const inside = slugs.includes(slug);
  const only = inside && slugs.length === 1;
  return (
    <div className="px-5 lg:px-0">
      <button
        type="button"
        disabled={only}
        aria-pressed={inside}
        onClick={() => save(inside ? slugs.filter((s) => s !== slug) : candidates.filter((c) => c === slug || slugs.includes(c)))}
        className={`min-h-12 w-full rounded-[14px] text-[15px] font-bold transition-colors disabled:opacity-60 ${
          inside ? "border border-line bg-card text-fg" : "bg-primary text-primary-fg"
        }`}
      >
        {inside ? "Remover da minha carteira" : "Adicionar à minha carteira"}
      </button>
      <p className="sr-only" aria-live="polite">
        {inside ? (only ? "É o único ativo da sua carteira." : "Este ativo está na sua carteira.") : "A carteira fica salva neste navegador."}
      </p>
    </div>
  );
}
