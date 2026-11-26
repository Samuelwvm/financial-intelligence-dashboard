"use client";

import { motion, useReducedMotion } from "motion/react";
import { useState } from "react";
import { formatMonthShort, formatMonthYear, formatPct } from "@/lib/format";
import type { Macro } from "@/lib/schema";
import { IconChevron } from "./icons";
import { LineChart } from "./LineChart";
import { Card } from "./ui";

/**
 * Tela Mundo — juro real no mundo, em dois cards (uma pergunta por card):
 *  1) RealRateRankingCard: "onde o Brasil está hoje?" — ranking de 10 países no mesmo mês.
 *  2) RealRateCompareCard: "como evoluiu comparado a outro país?" — série de 24 meses.
 * Web: lado a lado (alturas equilibradas). Celular: empilhados. Fonte única: BIS.
 */
export function WorldRealRate({ data, bcbMonth, i = 0 }: { data: Macro["realRate"]; bcbMonth: string; i?: number }) {
  return (
    <div className="flex flex-col gap-3 lg:grid lg:grid-cols-2 lg:items-stretch lg:gap-4">
      <RealRateRankingCard data={data} bcbMonth={bcbMonth} i={i} />
      <RealRateCompareCard data={data} i={i + 1} />
    </div>
  );
}

function RealRateRankingCard({ data, bcbMonth, i }: { data: Macro["realRate"]; bcbMonth: string; i: number }) {
  const reduce = useReducedMotion();
  const { month, ranking, series } = data;
  const br = ranking.find((r) => r.code === "BR")!;
  const pos = ranking.findIndex((r) => r.code === "BR") + 1;
  const runnerUp = ranking.find((r) => r.code !== "BR")!;

  // Escala proporcional: o zero fica onde os dados pedem (não no meio), para as barras
  // positivas — a maioria — usarem a largura disponível.
  const min = Math.min(0, ...ranking.map((r) => r.real));
  const max = Math.max(0, ...ranking.map((r) => r.real));
  const span = max - min || 1;
  const zero = (-min / span) * 100;

  // Meses sem dado na janela de 24 meses (ex.: EUA sem CPI em out/2025).
  const window = (series.BR as [string, number][]).map(([m]) => m);
  const gaps = ranking
    .map((r) => ({ name: r.name, missing: window.filter((m) => !(series[r.code] as [string, number][]).some(([d]) => d === m)) }))
    .filter((g) => g.missing.length > 0);

  const takeaway =
    pos === 1 && runnerUp.real > 0
      ? `O Brasil tem o maior juro real entre os ${ranking.length} países — cerca de ${Math.round(br.real / runnerUp.real)} vezes o do 2º colocado (${runnerUp.name}).`
      : `O Brasil está em ${pos}º lugar entre os ${ranking.length} países comparados.`;

  return (
    <Card i={i} className="mx-5 flex flex-col lg:mx-0" aria-labelledby="juro-real">
      <h2 id="juro-real" className="text-[15px] font-bold">
        Juro real no mundo
      </h2>
      <p className="text-[12px] text-muted">
        Juro básico descontada a inflação de 12 meses · {formatMonthYear(month)} · Fonte: BIS
      </p>
      <p className="mt-2 text-[14px] leading-snug">{takeaway}</p>

      <ol className="mt-3 flex flex-col gap-2" aria-label={`Juro real por país em ${formatMonthYear(month)}, do maior para o menor`}>
        {ranking.map((r, k) => {
          const isBr = r.code === "BR";
          const w = (Math.abs(r.real) / span) * 100;
          const style =
            r.real >= 0
              ? { left: `${zero}%`, width: `${w}%`, transformOrigin: "left" }
              : { left: `${zero - w}%`, width: `${w}%`, transformOrigin: "right" };
          return (
            <li key={r.code} className="grid grid-cols-[1.4rem_minmax(0,7rem)_1fr_3.4rem] items-center gap-2 text-[13px]">
              <span className="num text-right text-[11px] text-muted">{k + 1}º</span>
              <span className={`truncate ${isBr ? "font-bold text-pos" : "font-semibold"}`}>{r.name}</span>
              <span className="relative flex h-2.5" aria-hidden="true">
                <span className="absolute inset-y-[-3px] w-px bg-line" style={{ left: `${zero}%` }} />
                <motion.span
                  initial={{ scaleX: 0 }}
                  animate={{ scaleX: 1 }}
                  transition={{ duration: reduce ? 0 : 0.4, delay: reduce ? 0 : k * 0.03 }}
                  className={`absolute inset-y-0 rounded-full ${isBr ? "bg-pos" : "bg-[var(--bar-ipca)]"}`}
                  style={style}
                />
              </span>
              <span className={`num text-right font-semibold ${isBr ? "text-pos" : ""}`}>{formatPct(r.real, 1)}</span>
            </li>
          );
        })}
      </ol>

      {/* Conteúdo de consulta: recolhido por padrão, acessível por teclado e leitor de tela. */}
      <details className="group mt-auto pt-4">
        <summary className="flex min-h-11 cursor-pointer list-none items-center justify-between gap-2 rounded-xl bg-soft px-3 text-[13px] font-semibold text-fg">
          Sobre os dados
          <IconChevron size={18} className="text-muted transition-transform group-open:rotate-180 motion-reduce:transition-none" />
        </summary>
        <ul className="mt-2 list-disc space-y-1 pl-5 text-[12px] leading-snug text-muted">
          <li>
            Fonte única: <strong className="font-semibold text-fg">BIS</strong> (Banco de Compensações Internacionais), com a mesma
            metodologia para os {ranking.length} países. Conta de Fisher: (1 + juro) ÷ (1 + inflação) − 1.
          </li>
          <li>
            O BIS publica cerca de 1 mês depois das fontes nacionais: aqui o Brasil aparece em {formatMonthYear(month)}, enquanto os dados
            do Banco Central na tela Brasil já vão até {formatMonthYear(bcbMonth)}.
          </li>
          <li>
            &ldquo;Juro básico&rdquo; é a taxa de política monetária que o BIS registra para cada banco central. Ela não tem o mesmo nome
            nem funciona exatamente igual em todos os países.
          </li>
          {gaps.length > 0 && (
            <li>
              Meses sem dado nos últimos 24 meses: {gaps.map((g) => `${g.name} (${g.missing.map(formatMonthShort).join(", ")})`).join("; ")}.
            </li>
          )}
          <li>
            Países: grandes economias (EUA, Zona do Euro, Reino Unido, Japão), BRICS (China, Índia, África do Sul) e vizinhos (México,
            Chile).
          </li>
        </ul>
      </details>
    </Card>
  );
}

function RealRateCompareCard({ data, i }: { data: Macro["realRate"]; i: number }) {
  const [other, setOther] = useState("US");
  const { month, ranking, series } = data;
  const br = ranking.find((r) => r.code === "BR")!;
  const sel = ranking.find((r) => r.code === other)!;
  const choices = ranking.filter((r) => r.code !== "BR").sort((a, b) => a.name.localeCompare(b.name, "pt-BR"));
  const pts = (code: string) => series[code] as [string, number][];

  return (
    <Card i={i} className="mx-5 flex flex-col lg:mx-0" aria-labelledby="juro-real-comparar">
      <div className="flex flex-wrap items-start justify-between gap-x-3 gap-y-2">
        <div>
          <h2 id="juro-real-comparar" className="text-[15px] font-bold">
            Brasil × {sel.name}
          </h2>
          <p className="text-[12px] text-muted">Juro real nos últimos 24 meses · Fonte: BIS</p>
        </div>
        <label className="flex items-center gap-2 text-[12px] font-semibold text-muted">
          Comparar com
          <select
            value={other}
            onChange={(e) => setOther(e.target.value)}
            className="min-h-11 rounded-[10px] border border-line bg-card px-3 text-[14px] font-semibold text-fg"
          >
            {choices.map((c) => (
              <option key={c.code} value={c.code}>
                {c.name}
              </option>
            ))}
          </select>
        </label>
      </div>

      <div className="mt-3 flex gap-5">
        <div>
          <div className="text-[11px] font-semibold text-pos">— Brasil</div>
          <div className="num font-display text-[22px] font-semibold text-pos">{formatPct(br.real, 1)}</div>
        </div>
        <div>
          <div className="text-[11px] font-semibold text-muted">- - {sel.name}</div>
          <div className="num font-display text-[22px] font-semibold">{formatPct(sel.real, 1)}</div>
        </div>
      </div>

      <div className="mt-2">
        <LineChart
          series={[
            { id: "BR", label: "Brasil", points: pts("BR"), tone: "pos" },
            { id: other, label: sel.name, points: pts(other), tone: "fg", dashed: true },
          ]}
          height={170}
          heightClass="h-[170px] lg:h-[200px]"
          baseline={0}
          yAxis={(x) => formatPct(x, 0)}
          animKey={other}
          label={`Juro real do Brasil e de ${sel.name} nos últimos 24 meses`}
          description={`Em ${formatMonthYear(month)}: Brasil ${formatPct(br.real, 1)}, ${sel.name} ${formatPct(sel.real, 1)}.`}
          formatValue={(x) => formatPct(x, 1)}
          formatDate={formatMonthShort}
        />
      </div>

      <p className="mt-auto pt-3 text-[13px] leading-snug text-muted">
        Juro real mais alto tende a atrair investimento estrangeiro — um dos fatores que influenciam o dólar, não o único.
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
