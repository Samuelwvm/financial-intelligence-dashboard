import type { Metadata } from "next";
import { GlossaryView } from "@/components/GlossaryView";
import { PageHeader } from "@/components/ui";
import { getGlossary } from "@/lib/data";

export const metadata: Metadata = {
  title: "Entenda o mercado",
  description: "Glossário com termos do mercado financeiro explicados sem complicação: SELIC, CDI, IPCA, volatilidade, base 100 e mais.",
};

export default function EntendaPage() {
  const g = getGlossary();
  return (
    <>
      <PageHeader title="Entenda o mercado" subtitle="Termos explicados sem complicação" />
      <GlossaryView glossary={g} />
    </>
  );
}
