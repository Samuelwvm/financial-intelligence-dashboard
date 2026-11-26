// Carregamento dos JSON no build (Server Components). Valida o contrato e a
// idade dos dados: o build FALHA se o dado estiver quebrado ou velho demais.
import "server-only";
import { existsSync, readFileSync } from "node:fs";
import path from "node:path";
import { cache } from "react";
import type { z } from "zod";
import {
  glossarySchema,
  ibgeSchema,
  macroSchema,
  portfolioSchema,
  seriesSchema,
  summarySchema,
  type Period,
} from "./schema";

const DATA_DIR = path.join(process.cwd(), "public", "data");
// Dias corridos tolerados entre a geração dos dados e o build.
const MAX_AGE_DAYS = Number(process.env.RADAR_MAX_DATA_AGE_DAYS ?? 7);

function load<T extends z.ZodTypeAny>(rel: string, schema: T): z.infer<T> {
  let raw: string;
  try {
    raw = readFileSync(path.join(DATA_DIR, rel), "utf-8");
  } catch {
    throw new Error(
      `[dados] arquivo ausente: public/data/${rel}. Rode "python -m pipeline.run --skip-collect" na raiz do projeto.`,
    );
  }
  const parsed = schema.safeParse(JSON.parse(raw));
  if (!parsed.success) {
    throw new Error(`[dados] public/data/${rel} fora do contrato:\n${parsed.error.message}`);
  }
  return parsed.data;
}

export const getSummary = cache(() => {
  const s = load("summary.json", summarySchema);
  // Idade do dado mais recente (asOf), não do arquivo: um export novo de um banco parado também falha.
  const ageDays = (Date.now() - Date.parse(`${s.asOf}T00:00:00Z`)) / 86_400_000;
  if (ageDays > MAX_AGE_DAYS) {
    throw new Error(
      `[dados] dado mais recente é de ${s.asOf} (${ageDays.toFixed(1)} dias; limite ${MAX_AGE_DAYS}). ` +
        `Atualize os dados ou ajuste RADAR_MAX_DATA_AGE_DAYS.`,
    );
  }
  // Logo baixado no build (scripts/fetch-logos.mjs) ou null → o site mostra as iniciais.
  const base = process.env.NEXT_PUBLIC_BASE_PATH ?? "";
  for (const a of s.assets) {
    a.logo = existsSync(path.join(process.cwd(), "public", "logos", `${a.slug}.png`)) ? `${base}/logos/${a.slug}.png` : null;
  }
  const slugs = new Set(s.assets.map((a) => a.slug));
  for (const ref of [...s.pulse, ...s.portfolio.candidates, ...s.portfolio.default, s.portfolio.benchmark]) {
    if (!slugs.has(ref)) throw new Error(`[dados] referência a ativo inexistente: ${ref}`);
  }
  return s;
});

export const getSeries = cache((slug: string) => load(`series/${slug}.json`, seriesSchema));
export const getPortfolio = cache((period: Period) => load(`portfolio/${period}.json`, portfolioSchema));
export const getGlossary = cache(() => load("glossary.json", glossarySchema));
export const getIbge = cache(() => load("ibge.json", ibgeSchema));
export const getMacro = cache(() => load("macro.json", macroSchema));

export function getAsset(slug: string) {
  const a = getSummary().assets.find((x) => x.slug === slug);
  if (!a) throw new Error(`[dados] ativo não encontrado: ${slug}`);
  return a;
}
