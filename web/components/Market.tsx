// Blocos de mercado renderizados no build (sem JS no cliente).
import Link from "next/link";
import { formatDate, formatMonthYear, formatPct, formatPrice } from "@/lib/format";
import type { AssetSummary, Summary } from "@/lib/schema";
import { AssetLogo } from "./AssetLogo";
import { Chip } from "./ui";

/** Pulso do mercado: carrossel de cards de 136px (mobile) / grade de 5 (web). */
export function Pulse({ assets, label = "Pulso do mercado" }: { assets: AssetSummary[]; label?: string }) {
  return (
    <section aria-label={label}>
      <ul className="no-scrollbar flex snap-x scroll-px-5 gap-2.5 overflow-x-auto px-5 lg:grid lg:grid-cols-[repeat(auto-fit,minmax(160px,1fr))] lg:gap-3 lg:overflow-visible lg:px-0">
        {assets.map((a, i) => (
          <li key={a.slug} className="w-[136px] flex-none snap-start lg:w-auto">
            <Link
              href={`/ativo/${a.slug}/`}
              style={{ "--i": i } as React.CSSProperties}
              className="rise lift block h-full rounded-[14px] border border-line bg-card p-3 lg:rounded-2xl lg:p-4"
            >
              <div className="text-[12px] font-semibold text-muted lg:text-[13px]">{a.name}</div>
              <div className="num mt-1 mb-1.5 whitespace-nowrap font-display text-[18px] font-semibold lg:mt-1.5 lg:mb-2 lg:text-[22px]">
                {formatPrice(a.price, a.currency)}
              </div>
              <Chip value={a.change} />
            </Link>
          </li>
        ))}
      </ul>
    </section>
  );
}

/** SELIC, CDI e IPCA (dados oficiais do BCB). Cada número leva ao termo no glossário. */
export function MacroCards({ macro, start = 0 }: { macro: Summary["macro"]; start?: number }) {
  const items = [
    { label: "SELIC", value: macro.selic.value, unit: "ao ano", term: "Selic", note: `Meta · ${formatDate(macro.selic.date)}` },
    { label: "CDI", value: macro.cdi.value, unit: "ao ano", term: "CDI", note: `Taxa anual · ${formatDate(macro.cdi.date)}` },
    {
      label: "IPCA",
      value: macro.ipca12m.value,
      unit: "12 meses",
      term: "IPCA",
      note: `Até ${formatMonthYear(macro.ipca12m.date)} · mensal ${formatPct(macro.ipcaMonthly.value)}`,
    },
  ];
  return (
    <>
      {items.map((m, i) => (
        <Link
          key={m.label}
          href={`/entenda/?termo=${encodeURIComponent(m.term)}`}
          style={{ "--i": start + i } as React.CSSProperties}
          className="rise lift block min-w-0 flex-1 rounded-[14px] border border-line bg-card p-3 lg:flex-[1_1_150px] lg:rounded-2xl lg:p-4"
          aria-label={`${m.label}: ${formatPct(m.value)} ${m.unit}. ${m.note}. Ver o que significa`}
        >
          <div className="text-[12px] font-semibold text-muted lg:text-[13px]">{m.label}</div>
          <div className="num mt-1 mb-0.5 font-display text-[20px] font-semibold lg:my-1 lg:text-[24px]">{formatPct(m.value)}</div>
          <div className="text-[11px] text-muted lg:text-[12px]">{m.unit}</div>
        </Link>
      ))}
    </>
  );
}

/** Dicas do card "Em linguagem simples", com os números do dia (dados oficiais do BCB). */
export function plainTips(macro: Summary["macro"], variant: "mobile" | "web"): string[] {
  const touch = variant === "mobile" ? " Toque num número para ver o que ele significa." : "";
  return [
    `Quando a SELIC sobe, a renda fixa tende a render mais e o crédito fica mais caro.${touch}`,
    `A SELIC está em ${formatPct(macro.selic.value)} ao ano. É a taxa básica que serve de referência para os juros do país.`,
    `O CDI anda colado na SELIC e hoje está em ${formatPct(macro.cdi.value)} ao ano. É a referência da maioria dos CDBs.`,
    `Com a inflação (IPCA) em ${formatPct(macro.ipca12m.value)} em 12 meses, um investimento precisa render mais que isso para não perder poder de compra.`,
    "Volatilidade alta quer dizer preço que sobe e desce muito. Não é bom nem ruim: é a medida do risco.",
    "Base 100 coloca todos os ativos no mesmo ponto de partida, para comparar quem subiu mais no período.",
    "Dólar em alta encarece importados e viagens, mas ajuda as empresas que exportam.",
    "Diversificar entre ativos diferentes reduz o estrago que a queda de um só pode fazer na carteira.",
  ];
}

/** Linha de ativo para as listas de Brasil e Mundo. */
export function AssetRowLink({ a, ret, digits, i }: { a: AssetSummary; ret: number; digits: number; i: number }) {
  return (
    <li>
      <Link
        href={`/ativo/${a.slug}/`}
        style={{ "--i": i } as React.CSSProperties}
        className="rise lift flex min-h-16 items-center gap-3 rounded-2xl border border-line bg-card px-4 py-3 lg:rounded-[18px]"
      >
        <AssetLogo logo={a.logo} ticker={a.ticker} />
        <span className="min-w-0 flex-1">
          <span className="block truncate text-[15px] font-bold">{a.name}</span>
          <span className="block text-[12px] text-muted">{a.ticker}</span>
        </span>
        <span className="text-right">
          <span className="num block whitespace-nowrap font-display text-[16px] font-semibold">{formatPrice(a.price, a.currency)}</span>
          <Chip value={ret} digits={digits} />
        </span>
      </Link>
    </li>
  );
}
