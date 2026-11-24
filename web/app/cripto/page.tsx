import type { Metadata } from "next";
import { Footer } from "@/components/Footer";
import { CryptoView } from "@/components/CryptoView";
import { PageHeader } from "@/components/ui";
import { getAsset, getSeries } from "@/lib/data";
import { formatDate } from "@/lib/format";

export const metadata: Metadata = {
  title: "Cripto",
  description: "Bitcoin e Ethereum: preço em dólar, variação, máxima, mínima, volatilidade e comparação base 100.",
};

export default function CriptoPage() {
  const btc = getAsset("bitcoin");
  const eth = getAsset("ethereum");
  return (
    <>
      <PageHeader title="Cripto" subtitle={`Bitcoin e Ethereum em dólar · ${formatDate(btc.lastDate)}`} />
      <CryptoView btc={{ asset: btc, series: getSeries("bitcoin") }} eth={{ asset: eth, series: getSeries("ethereum") }} />
      <Footer attribution />
    </>
  );
}
