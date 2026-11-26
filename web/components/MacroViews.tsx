"use client";

import { motion, useReducedMotion } from "motion/react";
import { useState } from "react";
import { formatMonthShort, formatMonthYear, formatPct } from "@/lib/format";
import type { Macro } from "@/lib/schema";
import { LineChart } from "./LineChart";
import { Card } from "./ui";

/**
 * Tela Mundo: juro real no mundo (fonte única: BIS).
 * Ranking dos 10 países no mesmo mês + Brasil × país escolhido em 24 meses.
 * Só descreve o dado; os cuidados de leitura ficam no próprio card ("Sobre os dados").
 */
export function WorldRealRateCard({ data, bcbMonth, i = 0 }: { data: Macro["realRate"]; bcbMonth: string; i?: number }) {
  const [other, setOther] = useState("US");
  const reduce = useReducedMotion();
  const { month, ranking, series } = data;
  const br = ranking.find((r) => r.code === "BR")!;
  const sel = ranking.find((r) => r.code === other)!;
  const pos = ranking.findIndex((r) => r.code === "BR") + 1;
  const maxAbs = Math.max(...ranking.map((r) => Math.abs(r.real)), 0.1);
  const pts = (code: string) => series[code] as [string, number][];
  const choices = ranking.filter((r) => r.code !== "BR").sort((a, b) => a.name.localeCompare(b.name, "pt-BR"));

  // Meses sem dado dentro da janela de 24 meses (ex.: EUA sem CPI em out/2025).
  const window = pts("BR").map(([m]) => m);
  const gaps = ranking
    .map((r) => ({ name: r.name, missing: window.filter((m) => !pts(r.code).some(([d]) => d === m)) }))
    .filter((g) => g.missing.length > 0);

  return (
    <Card i={i} className="mx-5 lg:mx-0" aria-labelledby="juro-real">
      <h2 id="juro-real" className="text-[15px] font-bold">
        Juro real no mundo
      </h2>
      <p className="text-[12px] text-muted">
        Juro básico descontada a inflação dos últimos 12 meses · {formatMonthYear(month)} · Fonte: BIS
      </p>

      {/* Dois blocos empilhados em qualquer tela, separados por uma linha (como o "---" do Notion). */}
      <div className="mt-4">
        {/* Ranking no mesmo mês para todos */}
        <h3 className="text-[13px] font-semibold text-muted">Ranking · {formatMonthYear(month)}</h3>
        <ol className="mt-2 flex max-w-[640px] flex-col gap-2" aria-label={`Juro real por país em ${formatMonthYear(month)}, do maior para o menor`}>
          {ranking.map((r, k) => {
            const isBr = r.code === "BR";
            const w = (Math.abs(r.real) / maxAbs) * 50;
            return (
              <li key={r.code} className="grid grid-cols-[1.25rem_minmax(0,7.5rem)_1fr_3.6rem] items-center gap-2 text-[13px]">
                <span className="num text-right text-[11px] text-muted">{k + 1}º</span>
                <span className={`truncate ${isBr ? "font-bold text-pos" : "font-semibold"}`}>{r.name}</span>
                <span className="relative flex h-2.5" aria-hidden="true">
                  <span className="absolute inset-y-0 left-1/2 w-px bg-line" />
                  <motion.span
                    initial={{ scaleX: 0 }}
                    animate={{ scaleX: 1 }}
                    transition={{ duration: reduce ? 0 : 0.4, delay: reduce ? 0 : k * 0.03 }}
                    className={`absolute inset-y-0 rounded-full ${isBr ? "bg-pos" : "bg-[var(--bar-ipca)]"}`}
                    style={
                      r.real >= 0
                        ? { left: "50%", width: `${w}%`, transformOrigin: "left" }
                        : { right: "50%", width: `${w}%`, transformOrigin: "right" }
                    }
                  />
                </span>
                <span className={`num text-right font-semibold ${isBr ? "text-pos" : ""}`}>{formatPct(r.real, 1)}</span>
              </li>
            );
          })}
        </ol>

        <hr className="my-5 border-t border-line" />

        {/* Brasil × país escolhido */}
        <div className="min-w-0">
          <h3 className="text-[13px] font-semibold text-muted">Brasil × {sel.name} · últimos 24 meses</h3>
          <div role="group" aria-label="País para comparar com o Brasil" className="no-scrollbar mt-2 flex gap-1.5 overflow-x-auto lg:flex-wrap">
            {choices.map((c) => (
              <button
                key={c.code}
                type="button"
                aria-pressed={other === c.code}
                onClick={() => setOther(c.code)}
                className={`min-h-9 shrink-0 rounded-full border px-3 text-[13px] font-semibold transition-colors ${
                  other === c.code ? "border-fg bg-fg text-inverse-fg" : "border-line bg-card text-fg hover:border-muted"
                }`}
              >
                {c.name}
              </button>
            ))}
          </div>
          <div className="mt-2 flex gap-4 text-[13px]">
            <span className="font-bold text-pos">— Brasil {formatPct(br.real, 1)}</span>
            <span className="font-bold text-fg">
              - - {sel.name} {formatPct(sel.real, 1)}
            </span>
          </div>
          <div className="mt-1">
            <LineChart
              series={[
                { id: "BR", label: "Brasil", points: pts("BR"), tone: "pos" },
                { id: other, label: sel.name, points: pts(other), tone: "fg", dashed: true },
              ]}
              height={150}
              heightClass="h-[150px] lg:h-[190px]"
              baseline={0}
              yAxis={(x) => formatPct(x, 0)}
              animKey={other}
              label={`Juro real do Brasil e de ${sel.name} nos últimos 24 meses`}
              description={`Em ${formatMonthYear(month)}: Brasil ${formatPct(br.real, 1)}, ${sel.name} ${formatPct(sel.real, 1)}.`}
              formatValue={(x) => formatPct(x, 1)}
              formatDate={formatMonthShort}
            />
          </div>
        </div>
      </div>

      <p className="mt-4 border-t border-line pt-3 text-[13px] leading-snug text-muted">
        Em {formatMonthYear(month)}, o Brasil tinha o <strong className="font-semibold text-fg">{pos}º maior juro real</strong> entre os{" "}
        {ranking.length} países comparados ({formatPct(br.real, 1)} ao ano; {sel.name}: {formatPct(sel.real, 1)}). Juro real mais alto
        tende a atrair investimento estrangeiro — um dos fatores que influenciam o dólar, não o único.
      </p>

      <div className="mt-3 rounded-xl bg-soft p-3 text-[12px] leading-snug text-muted">
        <h3 className="font-semibold text-fg">Sobre os dados</h3>
        <ul className="mt-1 list-disc space-y-1 pl-4">
          <li>
            Fonte única: <strong className="font-semibold text-fg">BIS</strong> (Banco de Compensações Internacionais), com a mesma
            metodologia para os {ranking.length} países. Conta de Fisher: (1 + juro) ÷ (1 + inflação) − 1.
          </li>
          <li>
            O BIS publica cerca de 1 mês depois das fontes nacionais. Por isso, aqui o Brasil aparece em {formatMonthYear(month)},
            enquanto os dados do Banco Central na tela Brasil já vão até {formatMonthYear(bcbMonth)}.
          </li>
          <li>
            &ldquo;Juro básico&rdquo; é a taxa de política monetária que o BIS registra para cada banco central. Ela não tem o mesmo nome
            nem funciona exatamente igual em todos os países.
          </li>
          {gaps.length > 0 && (
            <li>
              Meses sem dado no período: {gaps.map((g) => `${g.name} (${g.missing.map(formatMonthShort).join(", ")})`).join("; ")}.
            </li>
          )}
          <li>
            Países: grandes economias (EUA, Zona do Euro, Reino Unido, Japão), BRICS (China, Índia, África do Sul) e vizinhos (México,
            Chile).
          </li>
        </ul>
      </div>
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
