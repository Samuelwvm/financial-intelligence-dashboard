// Rodapé discreto: aviso legal (mesmo texto da V1) e atribuição obrigatória dos logos.
// A atribuição precisa ser um link visível e sem rel="nofollow" (termos da AllInvestView).
export function Footer() {
  return (
    <footer className="mx-5 mt-4 border-t border-line pt-3 text-[11px] leading-[1.5] text-muted lg:mx-0 lg:mt-6">
      <p>
        Os cálculos são automáticos, baseados em dados públicos (Yahoo Finance / Banco Central do Brasil), e não
        representam análise de valores mobiliários ou recomendação de investimento. Rentabilidade passada não é garantia
        de retorno futuro.
      </p>
      <p className="mt-1">
        <a href="https://www.allinvestview.com/tools/ticker-logos/" className="underline underline-offset-2 hover:text-fg">
          Logos by AllInvestView
        </a>
      </p>
    </footer>
  );
}
