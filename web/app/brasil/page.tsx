import type { Metadata } from "next";
import { Footer } from "@/components/Footer";
import { IbgeView } from "@/components/IbgeView";
import { AssetList, SeriesCard } from "@/components/Lists";
import { MacroCards } from "@/components/Market";
import { PageHeader } from "@/components/ui";
import { getAsset, getIbge, getMacro, getSeries, getSummary } from "@/lib/data";
import { formatDate } from "@/lib/format";

export const metadata: Metadata = {
  title: "Brasil",
  description: "As 10 ações da B3 acompanhadas, evolução do Ibovespa, juros (SELIC, CDI), inflação por grupo e desemprego (IBGE).",
};

export default function BrasilPage() {
  const s = getSummary();
  const stocks = s.assets.filter((a) => a.group === "brasil" && a.kind === "acao");
  const ibov = getAsset("ibovespa");
  return (
    <>
      <PageHeader title="Brasil" subtitle={`Ações da B3 e Ibovespa · dados de ${formatDate(ibov.lastDate)}`} />
      <SeriesCard asset={ibov} series={getSeries("ibovespa")} heading="Ibovespa" />
      <AssetList id="acoes-b3" title="Ações da B3" assets={stocks} start={1} />
      <IbgeView data={getIbge()} target={getMacro().inflationTarget} start={7}>
        <div className="flex gap-2 px-5 lg:gap-4 lg:px-0" aria-label="Juros e inflação">
          <MacroCards macro={s.macro} start={4} />
        </div>
      </IbgeView>
      <Footer attribution />
    </>
  );
}
