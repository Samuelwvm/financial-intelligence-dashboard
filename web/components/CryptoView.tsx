"use client";

import Link from "next/link";
import { useState } from "react";
import { PERIOD_LONG, formatPlain, formatPrice, formatSignedPct } from "@/lib/format";
import type { AssetSeries, AssetSummary, Period } from "@/lib/schema";
import { AssetLogo } from "./AssetLogo";
import { LineChart } from "./LineChart";
import { PeriodPicker } from "./PeriodPicker";
import { Card, Chip, Stat } from "./ui";

type Coin = { asset: AssetSummary; series: AssetSeries };

const b100 = (s: AssetSeries, p: Period) => {
  const { base, points } = s.periods[p];
  return points.map(([d, v]) => [d, (v / base) * 100] as [string, number]);
};

export function CryptoView({ btc, eth }: { btc: Coin; eth: Coin }) {
  const [period, setPeriod] = useState<Period>("30d");
  const digits = period === "1d" ? 2 : 1;
  const bc = b100(btc.series, period);
  const ec = b100(eth.series, period);
  const last = (c: [string, number][]) => (c.length ? c[c.length - 1][1] - 100 : 0);

  return (
    <>
      <div className="px-5 lg:px-0">
        <PeriodPicker value={period} onChange={setPeriod} variant="pill" label="Período das criptomoedas" />
      </div>
      <div className="flex flex-col gap-3 lg:grid lg:grid-cols-2 lg:gap-4">
        {[btc, eth].map(({ asset: a }, i) => {
          const st = a.stats[period];
          return (
            <Card key={a.slug} i={i + 1} className="mx-5 lg:mx-0" aria-labelledby={`c-${a.slug}`}>
              <div className="flex items-center justify-between gap-3">
                <AssetLogo logo={a.logo} ticker={a.ticker} />
                <div className="mr-auto">
                  <h2 id={`c-${a.slug}`} className="text-[16px] font-bold">
                    <Link href={`/ativo/${a.slug}/`} className="hover:underline">
                      {a.name}
                    </Link>
                  </h2>
                  <div className="text-[12px] text-muted">{a.ticker}</div>
                </div>
                <div className="text-right">
                  <div className="num font-display text-[20px] font-semibold lg:text-[24px]">{formatPrice(a.price, a.currency)}</div>
                  <Chip value={st.ret} digits={digits} />
                </div>
              </div>
              <div className="mt-3 flex gap-2">
                <Stat label="Máxima" value={formatPlain(st.high, a.currency)} />
                <Stat label="Mínima" value={formatPlain(st.low, a.currency)} />
                <Stat label="Volatil." value={`${st.vol.toFixed(1).replace(".", ",")}%`} />
              </div>
            </Card>
          );
        })}
      </div>
      <Card i={3} className="mx-5 lg:mx-0" aria-labelledby="cmp">
        <h2 id="cmp" className="text-[15px] font-bold">
          Desempenho comparado (base 100)
        </h2>
        <div className="my-1 flex gap-3.5 text-[12px] text-muted">
          <span className="font-bold text-pos">— Bitcoin</span>
          <span className="font-bold text-fg">- - Ethereum</span>
        </div>
        <LineChart
          series={[
            { id: "btc", label: "Bitcoin", points: bc, tone: "pos" },
            { id: "eth", label: "Ethereum", points: ec, tone: "fg", dashed: true },
          ]}
          height={130}
          label="Bitcoin e Ethereum comparados, base 100"
          description={`${PERIOD_LONG[period]}: Bitcoin ${formatSignedPct(last(bc))}, Ethereum ${formatSignedPct(last(ec))}.`}
          animKey={period}
          formatValue={(v) => formatSignedPct(v - 100)}
        />
      </Card>
    </>
  );
}
