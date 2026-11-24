// Rodapé discreto, por página:
// - aviso legal (texto da V1): só na tela Entenda, por escolha do dono do projeto;
// - atribuição dos logos, obrigatória pelos termos da AllInvestView em toda página
//   que mostra logos (link visível e sem rel="nofollow").
export function Footer({ disclaimer = false, attribution = false }: { disclaimer?: boolean; attribution?: boolean }) {
  if (!disclaimer && !attribution) return null;
  return (
    <footer className="mx-5 mt-4 border-t border-line pt-3 text-[11px] leading-[1.5] text-muted lg:mx-0 lg:mt-6">
      {disclaimer && (
        <p>
          Os cálculos são automáticos, baseados em dados públicos (Yahoo Finance / Banco Central do Brasil), e não
          representam análise de valores mobiliários ou recomendação de investimento. Rentabilidade passada não é
          garantia de retorno futuro.
        </p>
      )}
      {attribution && (
        <p className={disclaimer ? "mt-1" : undefined}>
          <a href="https://www.allinvestview.com/tools/ticker-logos/" className="underline underline-offset-2 hover:text-fg">
            Logos by AllInvestView
          </a>
        </p>
      )}
    </footer>
  );
}
