import Link from "next/link";
import { PageHeader } from "@/components/ui";

export default function NotFound() {
  return (
    <>
      <PageHeader title="Página não encontrada" subtitle="O endereço pode ter mudado. Volte ao painel para continuar." />
      <div className="px-5 lg:px-0">
        <Link href="/" className="inline-flex min-h-12 items-center rounded-[14px] bg-primary px-6 text-[15px] font-bold text-primary-fg">
          Ir para o painel
        </Link>
      </div>
    </>
  );
}
