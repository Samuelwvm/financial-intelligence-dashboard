"use client";

import { formatMonthShort, formatMonthYear, formatPct, formatPp } from "@/lib/format";
import type { Macro } from "@/lib/schema";
import { LineChart } from "./LineChart";
import { Card } from "./ui";

const pct2 = (v: number) => formatPct(v, 1);

/** Tela Mundo: juro real Brasil × EUA (ex-post, Fisher). Só descreve — sem afirmar causa. */
export function RealRateCard({ data, i = 0 }: { data: Macro["realRate"]; i?: number }) {
  const { br, us, series } = data;
  const brPts = series.filter((r) => r[1] !== null).map((r) => [r[0], r[1]!] as [string, number]);
  const usPts = series.filter((r) => r[2] !== null).map((r) => [r[0], r[2]!] as [string, number]);
  const gap = br.real - us.real;
  const missing = data.usGaps.filter((m) => m >= series[0][0]);
  return (
    <Card i={i} className="mx-5 lg:mx-0" aria-labelledby="juro-real">
      <h2 id="juro-real" className="text-[15px] font-bold">
        Juro real: Brasil × EUA
      </h2>
      <p className="text-[12px] text-muted">Juro básico descontada a inflação dos últimos 12 meses</p>

      <div className="mt-3 grid grid-cols-2 gap-2 lg:grid-cols-3">
        <div className="rounded-xl bg-soft p-2.5">
          <div className="text-[11px] font-semibold text-muted">Brasil · {formatMonthShort(br.month)}</div>
          <div className="num font-display text-[22px] font-semibold text-pos">{pct2(br.real)}</div>
          <div className="text-[11px] text-muted">
            SELIC {formatPct(br.nominal, 2)} − IPCA {formatPct(br.inflation, 2)}
          </div>
        </div>
        <div className="rounded-xl bg-soft p-2.5">
          <div className="text-[11px] font-semibold text-muted">EUA · {formatMonthShort(us.month)}</div>
          <div className="num font-display text-[22px] font-semibold">{pct2(us.real)}</div>
          <div className="text-[11px] text-muted">
            Fed {formatPct(us.nominal, 2)} − CPI {formatPct(us.inflation, 2)}
          </div>
        </div>
        <div className="col-span-2 rounded-xl bg-soft p-2.5 lg:col-span-1">
          <div className="text-[11px] font-semibold text-muted">Diferença</div>
          <div className="num font-display text-[22px] font-semibold">{formatPp(Math.abs(gap)).replace("+", "")}</div>
          <div className="text-[11px] text-muted">{gap >= 0 ? "juro real maior no Brasil" : "juro real maior nos EUA"}</div>
        </div>
      </div>

      <div className="mt-2 flex gap-4 text-[13px]">
        <span className="font-bold text-pos">— Brasil</span>
        <span className="font-bold text-fg">- - EUA</span>
      </div>
      <div className="mt-1">
        <LineChart
          series={[
            { id: "br", label: "Brasil", points: brPts, tone: "pos" },
            { id: "us", label: "EUA", points: usPts, tone: "fg", dashed: true },
          ]}
          height={150}
          heightClass="h-[150px] lg:h-[200px]"
          baseline={0}
          label="Juro real do Brasil e dos EUA nos últimos 24 meses"
          description={`Brasil de ${pct2(brPts[0][1])} para ${pct2(br.real)}; EUA de ${pct2(usPts[0][1])} para ${pct2(us.real)}.`}
          formatValue={pct2}
          formatDate={formatMonthShort}
        />
      </div>

      <p className="mt-3 border-t border-line pt-2.5 text-[13px] leading-snug text-muted">
        Descontada a inflação dos últimos 12 meses, o juro no Brasil está em{" "}
        <strong className="font-semibold text-fg">{pct2(br.real)} ao ano</strong> e nos EUA em{" "}
        <strong className="font-semibold text-fg">{pct2(us.real)}</strong>. Juro real mais alto tende a atrair investimento
        estrangeiro — um dos fatores que influenciam o dólar, não o único.
      </p>
      <p className="mt-2 text-[11px] leading-snug text-muted">
        Fontes: {data.sources}. Conta de Fisher: (1 + juro) ÷ (1 + inflação) − 1.
        {missing.length > 0 && (
          <> Sem CPI de 12 meses em {missing.map(formatMonthShort).join(" e ")} (mês não publicado pela BLS).</>
        )}
      </p>
    </Card>
  );
}

/** Tela Brasil: IPCA 12 meses contra a meta contínua do CMN (faixa de tolerância). */
export function InflationTargetCard({ data, i = 0 }: { data: Macro["inflationTarget"]; i?: number }) {
  const { center, lower, upper, latest } = data;
  const pts = data.series as [string, number][];
  const v = latest.value;
  const status =
    v > upper
      ? { text: `acima do teto da meta (${formatPct(upper, 1)})`, cls: "text-neg" }
      : v < lower
        ? { text: `abaixo do piso da meta (${formatPct(lower, 1)})`, cls: "text-neg" }
        : { text: `dentro do intervalo da meta (${formatPct(lower, 1)} a ${formatPct(upper, 1)})`, cls: "text-pos" };
  return (
    <Card i={i} className="mx-5 lg:mx-0" aria-labelledby="meta-inflacao">
      <h3 id="meta-inflacao" className="text-[15px] font-bold">
        Inflação × meta
      </h3>
      <p className="text-[12px] text-muted">IPCA em 12 meses · Fonte: Banco Central · meta: CMN</p>
      <div className="mt-2 flex flex-wrap items-baseline gap-x-3 gap-y-1">
        <span className="num font-display text-[30px] font-semibold">{formatPct(v, 2)}</span>
        <span className={`text-[13px] font-semibold ${status.cls}`}>{status.text}</span>
      </div>
      <div className="mt-3">
        <LineChart
          series={[{ id: "ipca12", label: "IPCA 12 meses", points: pts, tone: "fg" }]}
          height={120}
          band={{ low: lower, high: upper }}
          baseline={center}
          label={`IPCA em 12 meses nos últimos ${pts.length} meses, com a faixa da meta`}
          description={`De ${formatPct(pts[0][1], 2)} (${formatMonthShort(pts[0][0])}) para ${formatPct(v, 2)} (${formatMonthShort(latest.month)}). Meta ${formatPct(center, 1)}, tolerância de ${formatPct(lower, 1)} a ${formatPct(upper, 1)}.`}
          formatValue={(x) => formatPct(x, 2)}
          formatDate={formatMonthShort}
        />
      </div>
      <p className="mt-2 text-[12px] leading-snug text-muted">
        Faixa verde: tolerância da meta ({formatPct(lower, 1)} a {formatPct(upper, 1)}); linha tracejada: centro ({formatPct(center, 1)}).
        Dado até {formatMonthYear(latest.month)}.
      </p>
    </Card>
  );
}
