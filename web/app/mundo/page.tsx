import type { Metadata } from "next";
import { Footer } from "@/components/Footer";
import { AssetList, SeriesCard } from "@/components/Lists";
import { Pulse } from "@/components/Market";
import { PageHeader } from "@/components/ui";
import { getAsset, getSeries, getSummary } from "@/lib/data";
import { formatDate } from "@/lib/format";

export const metadata: Metadata = {
  title: "Mundo",
  description: "Ações globais, dólar e euro contra o real, ouro, petróleo, S&P 500 e Dow Jones.",
};

export default function MundoPage() {
  const s = getSummary();
  const mundo = s.assets.filter((a) => a.group === "mundo");
  const stocks = mundo.filter((a) => a.kind === "acao");
  const others = mundo.filter((a) => a.kind === "commodity" || a.kind === "indice");
  const refs = ["sp500", "dow-jones", "dolar", "euro", "ouro"].map(getAsset);
  const asOf = mundo.reduce((d, a) => (a.lastDate > d ? a.lastDate : d), "");
  return (
    <>
      <PageHeader title="Mundo" subtitle={`Ações globais, câmbio e commodities · dados de ${formatDate(asOf)}`} />
      <Pulse assets={refs} label="Referências globais" />
      <section aria-label="Câmbio contra o real" className="flex flex-col gap-3 lg:grid lg:grid-cols-2 lg:gap-4">
        <SeriesCard asset={getAsset("dolar")} series={getSeries("dolar")} heading="Dólar (USD/BRL)" i={5} />
        <SeriesCard asset={getAsset("euro")} series={getSeries("euro")} heading="Euro (EUR/BRL)" i={6} />
      </section>
      <AssetList id="acoes-globais" title="Ações globais" assets={stocks} start={7} />
      <AssetList id="commodities-indices" title="Commodities e índices" assets={others} start={8} />
      <Footer attribution />
    </>
  );
}
