// Contrato dos JSON: valida os arquivos gerados pelo pipeline (quando existem)
// e garante que dados quebrados são rejeitados.
import { existsSync, readdirSync, readFileSync } from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";
import { glossarySchema, ibgeSchema, macroSchema, portfolioSchema, PERIODS, seriesSchema, summarySchema } from "@/lib/schema";

const DIR = path.join(__dirname, "..", "..", "public", "data");
const has = existsSync(path.join(DIR, "summary.json"));
const read = (rel: string) => JSON.parse(readFileSync(path.join(DIR, rel), "utf-8"));

describe.skipIf(!has)("JSON gerados pelo pipeline", () => {
  it("summary.json respeita o contrato e as referências existem", () => {
    const s = summarySchema.parse(read("summary.json"));
    const slugs = new Set(s.assets.map((a) => a.slug));
    for (const r of [...s.pulse, ...s.portfolio.candidates, s.portfolio.benchmark]) expect(slugs.has(r)).toBe(true);
    for (const a of s.assets) expect(existsSync(path.join(DIR, "series", `${a.slug}.json`))).toBe(true);
  });
  it("séries, carteira e glossário", () => {
    for (const f of readdirSync(path.join(DIR, "series"))) seriesSchema.parse(read(`series/${f}`));
    for (const p of PERIODS) portfolioSchema.parse(read(`portfolio/${p}.json`));
    expect(glossarySchema.parse(read("glossary.json")).terms.length).toBeGreaterThanOrEqual(20);
  });
  it("ibge.json: 9 grupos do IPCA e impactos que somam o índice geral do mês", () => {
    const g = ibgeSchema.parse(read("ibge.json"));
    const soma = g.ipca.groups.reduce((a, x) => a + x.impact, 0);
    expect(soma).toBeCloseTo(g.ipca.general.monthly, 1); // convenção do IBGE (arredondamentos)
    expect(g.unemployment.series.at(-1)![0]).toBe(g.unemployment.date);
  });
  it("macro.json: juro real pela conta de Fisher e meta coerente", () => {
    const m = macroSchema.parse(read("macro.json"));
    const fisher = (i: number, p: number) => ((1 + i / 100) / (1 + p / 100) - 1) * 100;
    const reais = m.realRate.ranking.map((r) => r.real);
    for (const r of m.realRate.ranking) expect(r.real).toBeCloseTo(fisher(r.policy, r.inflation), 3);
    expect(reais).toEqual([...reais].sort((a, b) => b - a)); // ranking do maior para o menor
    expect(Object.keys(m.realRate.series)).toHaveLength(10);
    expect(m.realRate.series.BR.at(-1)![0]).toBe(m.realRate.month); // ranking e série no mesmo mês
    const t = m.inflationTarget;
    expect(t.lower).toBeLessThan(t.center);
    expect(t.center).toBeLessThan(t.upper);
    expect(t.series.at(-1)![0]).toBe(t.latest.month);
  });
  it("série do período começa no preço-base", () => {
    const s = seriesSchema.parse(read("series/petr4.json"));
    for (const p of PERIODS) expect(s.periods[p].points[0][1]).toBeCloseTo(s.periods[p].base, 3);
  });
});

describe("rejeita dados quebrados", () => {
  const ok = {
    schemaVersion: 1,
    generatedAt: "2026-11-23T22:00:00Z",
    asOf: "2026-11-23",
    pulse: ["a", "a", "a", "a", "a"],
    portfolio: { candidates: ["a"], default: ["a"], benchmark: "a" },
    macro: Object.fromEntries(["selic", "selicDaily", "cdi", "ipca12m", "ipcaMonthly"].map((k) => [k, { value: 1, date: "2026-11-23" }])),
    assets: [
      {
        symbol: "A", slug: "a", name: "A", ticker: "A", group: "brasil", kind: "acao", currency: "BRL", market: "x",
        lastDate: "2026-11-23", price: 10, change: 1,
        stats: Object.fromEntries(PERIODS.map((p) => [p, { ret: 1, vol: 2, high: 11, low: 9 }])),
      },
    ],
  };
  it("aceita o mínimo válido", () => expect(summarySchema.safeParse(ok).success).toBe(true));
  it("preço zero, NaN ou data inválida", () => {
    const bad = structuredClone(ok);
    bad.assets[0].price = 0;
    expect(summarySchema.safeParse(bad).success).toBe(false);
    const bad2 = structuredClone(ok);
    bad2.assets[0].stats["30d"].ret = Number.NaN;
    expect(summarySchema.safeParse(bad2).success).toBe(false);
    const bad3 = structuredClone(ok);
    bad3.asOf = "23/11/2026";
    expect(summarySchema.safeParse(bad3).success).toBe(false);
  });
  it("carteira com séries desalinhadas", () => {
    expect(portfolioSchema.safeParse({ period: "7d", dates: ["2026-01-02"], series: { a: [100, 101] } }).success).toBe(false);
  });
});
