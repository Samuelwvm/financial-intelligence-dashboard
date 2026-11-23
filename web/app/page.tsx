import { MacroCards, PlainLanguage, Pulse } from "@/components/Market";
import { Portfolio } from "@/components/Portfolio";
import { PageHeader } from "@/components/ui";
import { getAsset, getPortfolio, getSummary } from "@/lib/data";
import { formatDate } from "@/lib/format";

export default function PainelPage() {
  const s = getSummary();
  const bench = getAsset(s.portfolio.benchmark);
  return (
    <>
      <PageHeader title="Mercado hoje" subtitle={`Atualizado após o fechamento de ${formatDate(s.asOf)}`} />
      <Pulse assets={s.pulse.map(getAsset)} />
      <Portfolio
        candidates={s.portfolio.candidates.map(getAsset)}
        defaults={s.portfolio.default}
        benchmark={{ slug: bench.slug, name: bench.name }}
        initial={getPortfolio("30d")}
      />
      <div className="flex gap-2 px-5 lg:flex-wrap lg:gap-4 lg:px-0">
        <MacroCards macro={s.macro} start={3} />
        <PlainLanguage i={7} variant="web" />
      </div>
      <PlainLanguage i={6} variant="mobile" mobileExtra="Toque num número para ver o que ele significa." />
    </>
  );
}
