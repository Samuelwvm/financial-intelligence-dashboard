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
          yAxis={(x) => formatPct(x, 0)}
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

/**
 * Tela Brasil: IPCA 12 meses contra a meta contínua do CMN (3% ± 1,5 ponto).
 * Mostra quantos meses seguidos o índice está fora/dentro do intervalo e a regra oficial:
 * pelo art. 6º do Decreto 12.079/2024, 6 meses seguidos fora do intervalo obrigam o
 * Banco Central a publicar uma carta aberta. Só contagem do que já aconteceu — sem previsão.
 */
export function InflationTargetCard({ data, i = 0, className = "" }: { data: Macro["inflationTarget"]; i?: number; className?: string }) {
  const { center, lower, upper, latest } = data;
  const pts = data.series as [string, number][];
  const v = latest.value;
  const outside = (x: number) => x > upper || x < lower;
  let streak = 0;
  for (let k = pts.length - 1; k >= 0 && outside(pts[k][1]) === outside(v); k--) streak++;
  const status =
    v > upper
      ? { text: `acima do teto da meta (${formatPct(upper, 1)})`, cls: "text-neg" }
      : v < lower
        ? { text: `abaixo do piso da meta (${formatPct(lower, 1)})`, cls: "text-neg" }
        : { text: `dentro do intervalo da meta`, cls: "text-pos" };
  const ordinal = `${streak}º mês seguido`;
  const pctAxis = (x: number) => formatPct(x, Number.isInteger(x) ? 0 : 1);
  return (
    <Card i={i} className={`mx-5 lg:mx-0 ${className}`} aria-labelledby="meta-inflacao">
      <h3 id="meta-inflacao" className="text-[15px] font-bold">
        Inflação × meta
      </h3>
      <p className="text-[12px] text-muted">IPCA em 12 meses · {formatMonthYear(latest.month)} · Fonte: Banco Central · meta: CMN</p>
      <div className="mt-2 flex flex-wrap items-baseline gap-x-3 gap-y-1">
        <span className="num font-display text-[30px] font-semibold">{formatPct(v, 2)}</span>
        <span className={`text-[13px] font-semibold ${status.cls}`}>{status.text}</span>
      </div>
      <p className="text-[13px] text-muted">
        {outside(v) ? `${ordinal} fora do intervalo de ${formatPct(lower, 1)} a ${formatPct(upper, 1)}` : `${ordinal} dentro do intervalo de ${formatPct(lower, 1)} a ${formatPct(upper, 1)}`}
      </p>
      <div className="mt-3">
        <LineChart
          series={[{ id: "ipca12", label: "IPCA 12 meses", points: pts, tone: "fg" }]}
          height={150}
          heightClass="h-[150px] lg:h-[170px]"
          band={{ low: lower, high: upper }}
          refLines={[
            { value: upper, label: `teto ${formatPct(upper, 1)}` },
            { value: center, label: `meta ${formatPct(center, 0)}` },
            { value: lower, label: `piso ${formatPct(lower, 1)}` },
          ]}
          yAxis={pctAxis}
          label={`IPCA em 12 meses nos últimos ${pts.length} meses, com o intervalo da meta`}
          description={`De ${formatPct(pts[0][1], 2)} (${formatMonthShort(pts[0][0])}) para ${formatPct(v, 2)} (${formatMonthShort(latest.month)}). Meta de ${formatPct(center, 1)}, intervalo de ${formatPct(lower, 1)} a ${formatPct(upper, 1)}.`}
          formatValue={(x) => formatPct(x, 2)}
          formatDate={formatMonthShort}
        />
      </div>
      <p className="mt-3 border-t border-line pt-2.5 text-[12px] leading-snug text-muted">
        {outside(v) && (
          <>
            {streak < 6 ? (
              <>
                <strong className="font-semibold text-fg">{streak} de 6 meses seguidos</strong> fora do intervalo.{" "}
              </>
            ) : (
              <>
                <strong className="font-semibold text-fg">{streak} meses seguidos</strong> fora do intervalo — já atingiu os 6 meses da regra.{" "}
              </>
            )}
          </>
        )}
        Pela regra da meta contínua (Decreto 12.079/2024), quando o IPCA fica 6 meses seguidos fora do intervalo, o Banco
        Central publica uma carta aberta explicando o descumprimento.
      </p>
    </Card>
  );
}
