// Carteira: média simples (pesos iguais) das curvas base 100 dos ativos escolhidos.
// Fórmula documentada em docs/auditoria-v1.md §5.
import type { PortfolioData } from "./schema";

export type Point = [date: string, value: number];

export function portfolioCurve(data: PortfolioData, slugs: string[]): Point[] {
  const cols = slugs.map((s) => data.series[s]).filter((c): c is (number | null)[] => Array.isArray(c));
  if (cols.length === 0) return [];
  const out: Point[] = [];
  data.dates.forEach((d, i) => {
    let sum = 0;
    let n = 0;
    for (const c of cols) {
      const v = c[i];
      if (v !== null && v !== undefined) {
        sum += v;
        n += 1;
      }
    }
    // Só começa quando todos os ativos já têm ponto (evita a curva "pular" na entrada de um ativo).
    if (n === cols.length) out.push([d, sum / n]);
  });
  // Renormaliza para o primeiro ponto comum valer 100.
  if (out.length > 0 && out[0][1] !== 100) {
    const b = out[0][1];
    return out.map(([d, v]) => [d, (v / b) * 100]);
  }
  return out;
}

export function seriesCurve(data: PortfolioData, slug: string): Point[] {
  const col = data.series[slug] ?? [];
  const out: Point[] = [];
  data.dates.forEach((d, i) => {
    const v = col[i];
    if (v !== null && v !== undefined) out.push([d, v]);
  });
  return out;
}

export const curveReturn = (curve: Point[]) => (curve.length ? curve[curve.length - 1][1] - 100 : 0);

// ── Persistência local (sem conta, sem servidor) ─────────────────────────────
const KEY = "radar:carteira:v1";
const EVENT = "radar:carteira";

export function readPortfolio(candidates: string[], fallback: string[]): string[] {
  if (typeof window === "undefined") return fallback;
  try {
    const raw = window.localStorage.getItem(KEY);
    if (!raw) return fallback;
    const list = (JSON.parse(raw) as unknown[]).filter(
      (s): s is string => typeof s === "string" && candidates.includes(s),
    );
    return list.length ? list : fallback;
  } catch {
    return fallback;
  }
}

export function writePortfolio(slugs: string[]) {
  try {
    window.localStorage.setItem(KEY, JSON.stringify(slugs));
  } catch {
    /* modo privado sem storage: segue só na memória */
  }
  window.dispatchEvent(new CustomEvent(EVENT, { detail: slugs }));
}

export function onPortfolioChange(cb: () => void) {
  const handler = () => cb();
  window.addEventListener(EVENT, handler);
  window.addEventListener("storage", handler);
  return () => {
    window.removeEventListener(EVENT, handler);
    window.removeEventListener("storage", handler);
  };
}

/** Rebaseia uma curva para valer 100 em `start` (o 1º dia da carteira) e corta o que vem antes,
 * para que carteira, Ibovespa, CDI e IPCA partam exatamente do mesmo ponto. */
export function rebaseAt(points: Point[], start: string | undefined): Point[] {
  if (!start || points.length === 0) return points;
  let base: number | null = null;
  for (const [d, v] of points) {
    if (d <= start) base = v;
    else break;
  }
  const from = points.findIndex(([d]) => d >= start);
  if (from < 0) return [];
  const b = base ?? points[from][1];
  const out = points.slice(from).map(([d, v]) => [d, (v / b) * 100] as Point);
  if (out[0][0] !== start) out.unshift([start, (base ?? points[from][1]) / b * 100]);
  return out;
}

/*
 * FEATURE DESATIVADA — referências CDI e IPCA no gráfico de desempenho (docs/decisoes.md §35–37).
 *
 * export const REFERENCES = [
 *   { id: "cdi", label: "CDI", tone: "cdi", dashed: "2 3" },
 *   { id: "ipca", label: "IPCA", tone: "ipca", dashed: "8 3 2 3" },
 * ] as const;
 */
