import { describe, expect, it } from "vitest";
import { formatPct, formatPlain, formatPrice, formatSignedPct, formatDate } from "@/lib/format";
import { curveReturn, portfolioCurve, rebaseAt, seriesCurve } from "@/lib/portfolio";
import type { PortfolioData } from "@/lib/schema";

const nbsp = (s: string) => s.replace(/ /g, " ");

describe("formatação pt-BR", () => {
  it("moedas", () => {
    expect(nbsp(formatPrice(41.3, "BRL"))).toBe("R$ 41,30");
    expect(nbsp(formatPrice(61130.62, "USD"))).toBe("US$ 61.131");
    expect(nbsp(formatPrice(230.456, "USD"))).toBe("US$ 230,46");
    expect(formatPrice(164796.4, "PTS")).toBe("164.796");
    expect(nbsp(formatPrice(26.26, "SAR"))).toMatch(/SAR 26,26/);
  });
  it("percentuais com vírgula e sinal", () => {
    expect(formatPct(13.75)).toBe("13,75%");
    expect(formatSignedPct(1.234)).toBe("+1,2%");
    expect(formatSignedPct(-29.62)).toBe("−29,6%");
    expect(formatSignedPct(-0.04)).toBe("0,0%");
  });
  it("número sem moeda e datas", () => {
    expect(formatPlain(81268.4, "USD")).toBe("81.268");
    expect(formatDate("2026-11-23")).toBe("23/11/2026");
  });
});

describe("carteira (média base 100 com pesos iguais)", () => {
  const data: PortfolioData = {
    period: "7d",
    dates: ["2026-01-02", "2026-01-03", "2026-01-05"],
    series: {
      a: [100, null, 110], // ação: sem sábado (o pipeline já preenche para a frente; aqui testamos o null)
      b: [null, 100, 90],
      ibov: [100, 100, 105],
    },
  };
  it("só começa quando todos os ativos têm ponto e renormaliza para 100", () => {
    const c = portfolioCurve({ ...data, series: { a: [100, 100, 110], b: [null, 100, 90] } }, ["a", "b"]);
    expect(c).toEqual([
      ["2026-01-03", 100],
      ["2026-01-05", 100],
    ]);
    expect(curveReturn(c)).toBeCloseTo(0);
  });
  it("um ativo só = a própria curva", () => {
    const c = portfolioCurve({ ...data, series: { a: [100, 100, 110] } }, ["a"]);
    expect(curveReturn(c)).toBeCloseTo(10);
  });
  it("ignora slugs desconhecidos e devolve vazio sem ativos", () => {
    expect(portfolioCurve(data, ["zzz"])).toEqual([]);
  });
  it("série do índice de referência pula nulos", () => {
    expect(seriesCurve(data, "b")).toEqual([
      ["2026-01-03", 100],
      ["2026-01-05", 90],
    ]);
  });
});

describe("referências partem do mesmo ponto que a carteira", () => {
  const cdi: [string, number][] = [["2026-01-02", 100], ["2026-01-05", 100.1], ["2026-01-06", 100.2]];
  it("rebaseia para 100 no 1º dia da carteira e corta o que vem antes", () => {
    const r = rebaseAt(cdi, "2026-01-05");
    expect(r[0]).toEqual(["2026-01-05", 100]);
    expect(r[1][1]).toBeCloseTo((100.2 / 100.1) * 100);
  });
  it("dia da carteira sem ponto da referência usa o último anterior (fim de semana)", () => {
    const r = rebaseAt(cdi, "2026-01-04"); // domingo
    expect(r[0]).toEqual(["2026-01-04", 100]);
    expect(r[1][1]).toBeCloseTo(100.1);
  });
  it("sem início definido devolve a curva original", () => {
    expect(rebaseAt(cdi, undefined)).toBe(cdi);
  });
});
