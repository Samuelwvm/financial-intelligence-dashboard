// Contrato tipado dos JSON gerados por pipeline/export.py (schemaVersion 1).
import { z } from "zod";

export const PERIODS = ["1d", "7d", "30d", "90d", "1y"] as const;
export type Period = (typeof PERIODS)[number];

const isoDate = z.string().regex(/^\d{4}-\d{2}-\d{2}$/);
const finite = z.number().finite();
const positive = finite.positive();

const stats = z.object({ ret: finite, vol: finite.nonnegative(), high: positive, low: positive });

export const assetSummary = z.object({
  symbol: z.string(),
  slug: z.string().regex(/^[a-z0-9-]+$/),
  name: z.string(),
  ticker: z.string(),
  group: z.enum(["brasil", "mundo", "cripto"]),
  kind: z.enum(["acao", "indice", "moeda", "commodity", "cripto"]),
  currency: z.enum(["BRL", "USD", "SAR", "PTS"]),
  market: z.string(),
  /** Domínio do logo no CDN da AllInvestView (null = sem logo, usa iniciais). */
  logoDomain: z.string().nullable().optional(),
  /** Caminho do logo baixado no build (preenchido em lib/data.ts, não vem do JSON). */
  logo: z.string().nullable().optional(),
  lastDate: isoDate,
  price: positive,
  change: finite,
  stats: z.object({ "1d": stats, "7d": stats, "30d": stats, "90d": stats, "1y": stats }),
});
export type AssetSummary = z.infer<typeof assetSummary>;

const macroValue = z.object({ value: finite, date: isoDate });

export const summarySchema = z.object({
  schemaVersion: z.literal(1),
  generatedAt: z.string().datetime(),
  asOf: isoDate,
  pulse: z.array(z.string()).length(5),
  portfolio: z.object({
    candidates: z.array(z.string()).min(1),
    default: z.array(z.string()).min(1),
    benchmark: z.string(),
  }),
  macro: z.object({
    selic: macroValue,
    selicDaily: macroValue,
    cdi: macroValue,
    ipca12m: macroValue,
    ipcaMonthly: macroValue,
  }),
  assets: z.array(assetSummary).min(1),
});
export type Summary = z.infer<typeof summarySchema>;

const point = z.tuple([isoDate, positive]);
const periodSeries = z.object({ base: positive, points: z.array(point).min(1) });

export const seriesSchema = z.object({
  slug: z.string(),
  periods: z.object({ "1d": periodSeries, "7d": periodSeries, "30d": periodSeries, "90d": periodSeries, "1y": periodSeries }),
});
export type AssetSeries = z.infer<typeof seriesSchema>;

export const portfolioSchema = z
  .object({
    period: z.enum(PERIODS),
    dates: z.array(isoDate).min(1),
    series: z.record(z.string(), z.array(finite.nullable())),
  })
  .refine((p) => Object.values(p.series).every((s) => s.length === p.dates.length), "séries desalinhadas");
export type PortfolioData = z.infer<typeof portfolioSchema>;

export const glossarySchema = z.object({
  categories: z.array(z.string()).min(1),
  terms: z
    .array(z.object({ term: z.string(), category: z.string(), definition: z.string(), example: z.string() }))
    .min(20),
});
export type Glossary = z.infer<typeof glossarySchema>;
