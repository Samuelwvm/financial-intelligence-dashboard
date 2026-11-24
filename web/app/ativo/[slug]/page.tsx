import type { Metadata } from "next";
import { AssetLogo } from "@/components/AssetLogo";
import { AssetView } from "@/components/AssetView";
import { PageHeader } from "@/components/ui";
import { getAsset, getSeries, getSummary } from "@/lib/data";
import { formatDate } from "@/lib/format";

export const dynamicParams = false;

export function generateStaticParams() {
  return getSummary().assets.map((a) => ({ slug: a.slug }));
}

type Props = { params: Promise<{ slug: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const a = getAsset(slug);
  return { title: `${a.name} (${a.ticker})`, description: `${a.name}: preço, variação, máxima, mínima e volatilidade por período. ${a.market}.` };
}

const BACK = { brasil: { href: "/brasil/", label: "Brasil" }, mundo: { href: "/mundo/", label: "Mundo" }, cripto: { href: "/cripto/", label: "Cripto" } };

export default async function AtivoPage({ params }: Props) {
  const { slug } = await params;
  const s = getSummary();
  const asset = getAsset(slug);
  const series = getSeries(slug);
  const portfolio = s.portfolio.candidates.includes(slug) ? { candidates: s.portfolio.candidates, defaults: s.portfolio.default } : null;
  return (
    <>
      <PageHeader
        title={asset.name}
        subtitle={`${asset.market} · dados de ${formatDate(asset.lastDate)}`}
        back={BACK[asset.group]}
        icon={asset.logoDomain ? <AssetLogo logo={asset.logo} ticker={asset.ticker} size={32} /> : undefined}
      />
      <AssetView asset={asset} series={series} portfolio={portfolio} />
    </>
  );
}
