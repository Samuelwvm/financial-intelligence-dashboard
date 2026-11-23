// Formatação pt-BR com Intl (moeda, percentual com vírgula, datas).
import type { AssetSummary } from "./schema";

type Currency = AssetSummary["currency"];

const nf = (min: number, max: number) =>
  new Intl.NumberFormat("pt-BR", { minimumFractionDigits: min, maximumFractionDigits: max });

const cf = (currency: string, digits: number) =>
  new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency,
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });

/** Casas decimais conforme a grandeza (US$ 61.131 / US$ 230,45 / R$ 5,93). */
function digitsFor(value: number): number {
  return Math.abs(value) >= 10_000 ? 0 : 2;
}

export function formatPrice(value: number, currency: Currency): string {
  if (currency === "PTS") return nf(0, 0).format(value);
  return cf(currency, digitsFor(value)).format(value);
}

/** Número sem símbolo de moeda (máxima/mínima de cripto no mockup: "0.000"). */
export function formatPlain(value: number, currency: Currency): string {
  if (currency === "PTS") return nf(0, 0).format(value);
  const d = digitsFor(value);
  return nf(d, d).format(value);
}

/** Percentual com sinal: +1,2% / −3,4%. */
export function formatSignedPct(value: number, digits = 1): string {
  const v = Number(value.toFixed(digits));
  const sign = v > 0 ? "+" : v < 0 ? "−" : "";
  return `${sign}${nf(digits, digits).format(Math.abs(v))}%`;
}

export function formatPct(value: number, digits = 2): string {
  return `${nf(digits, digits).format(value)}%`;
}

const dateFmt = new Intl.DateTimeFormat("pt-BR", { day: "2-digit", month: "2-digit", year: "numeric", timeZone: "UTC" });
const shortDate = new Intl.DateTimeFormat("pt-BR", { day: "2-digit", month: "short", timeZone: "UTC" });
const monthYear = new Intl.DateTimeFormat("pt-BR", { month: "long", year: "numeric", timeZone: "UTC" });

const toDate = (iso: string) => new Date(`${iso.slice(0, 10)}T00:00:00Z`);

export const formatDate = (iso: string) => dateFmt.format(toDate(iso));
export const formatShortDate = (iso: string) => shortDate.format(toDate(iso)).replace(".", "");
export const formatMonthYear = (iso: string) => monthYear.format(toDate(iso));

export const PERIOD_LABEL: Record<string, string> = {
  "1d": "Hoje",
  "7d": "7d",
  "30d": "30d",
  "90d": "90d",
  "1y": "1 ano",
};

export const PERIOD_LONG: Record<string, string> = {
  "1d": "no último pregão",
  "7d": "no período de 7 dias",
  "30d": "no período de 30 dias",
  "90d": "no período de 90 dias",
  "1y": "no período de 1 ano",
};
