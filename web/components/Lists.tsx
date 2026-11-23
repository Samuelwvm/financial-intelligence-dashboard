"use client";

import Link from "next/link";
import { useCallback, useState } from "react";
import { PERIOD_LONG, formatPrice } from "@/lib/format";
import type { AssetSeries, AssetSummary, Period } from "@/lib/schema";
import { LineChart } from "./LineChart";
import { AssetRowLink } from "./Market";
import { PeriodPicker } from "./PeriodPicker";
import { Card, Chip } from "./ui";

/** Lista de ativos com seletor de período (o chip mostra o retorno do período). */
export function AssetList({ title, assets, start = 0, id }: { title: string; assets: AssetSummary[]; start?: number; id: string }) {
  const [period, setPeriod] = useState<Period>("30d");
  return (
    <section aria-labelledby={id} className="flex flex-col gap-3">
      <div className="flex flex-wrap items-center justify-between gap-2 px-5 lg:px-0">
        <h2 id={id} className="font-display text-[18px] font-semibold lg:text-[20px]">
          {title}
        </h2>
        <span className="text-[12px] text-muted">Retorno {PERIOD_LONG[period]}</span>
      </div>
      <div className="px-5 lg:px-0">
        <PeriodPicker value={period} onChange={setPeriod} variant="pill" label={`Período — ${title}`} />
      </div>
      <ul className="flex flex-col gap-2 px-5 lg:grid lg:grid-cols-2 lg:gap-3 lg:px-0">
        {assets.map((a, i) => (
          <AssetRowLink key={a.slug} a={a} ret={a.stats[period].ret} digits={period === "1d" ? 2 : 1} i={start + i} />
        ))}
      </ul>
    </section>
  );
}

/** Card de evolução (Ibovespa, câmbio): preço, chip do período, gráfico e seletor. */
export function SeriesCard({ asset, series, i = 0, heading }: { asset: AssetSummary; series: AssetSeries; i?: number; heading: string }) {
  const [period, setPeriod] = useState<Period>("30d");
  const fmt = useCallback((v: number) => formatPrice(v, asset.currency), [asset.currency]);
  const points = series.periods[period].points as [string, number][];
  const st = asset.stats[period];
  return (
    <Card i={i} className="mx-5 min-w-0 lg:mx-0" aria-labelledby={`h-${asset.slug}`}>
      <div className="flex items-start justify-between gap-3">
        <div>
          <h2 id={`h-${asset.slug}`} className="text-[13px] font-semibold text-muted">
            <Link href={`/ativo/${asset.slug}/`} className="hover:text-fg">
              {heading}
            </Link>
          </h2>
          <div className="num mt-0.5 font-display text-[24px] font-semibold lg:text-[30px]">{fmt(asset.price)}</div>
        </div>
        <Chip value={st.ret} digits={period === "1d" ? 2 : 1} className="mt-1" />
      </div>
      <div className="mt-3">
        <LineChart
          series={[{ id: asset.slug, label: asset.name, points, tone: "pos", area: true }]}
          height={130}
          heightClass="h-[130px] lg:h-[200px]"
          label={`Evolução de ${asset.name} ${PERIOD_LONG[period]}`}
          description={`De ${fmt(points[0][1])} para ${fmt(points[points.length - 1][1])}.`}
          animKey={period}
          formatValue={fmt}
        />
      </div>
      <div className="mt-2">
        <PeriodPicker value={period} onChange={setPeriod} stretch label={`Período — ${asset.name}`} />
      </div>
    </Card>
  );
}
