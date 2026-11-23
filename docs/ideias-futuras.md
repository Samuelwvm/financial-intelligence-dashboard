# Ideias futuras (fora do escopo da V2)

Registradas durante a V2 e **não implementadas** (o escopo da V2 = só o que já existia na V1).

- **Volatilidade de cripto anualizada com √365.** A V1 e a V2 usam √252 para todos os ativos (convenção de pregões). Cripto negocia todos os dias, então √365 seria mais fiel.
- **Separar indicadores macro de `assets_history`** numa tabela própria (`macro_history`), sem a coluna `variation`.
- **Novas fontes:** IBGE, Boletim Focus, agro, notícias.
- **Página de metodologia** com as fórmulas (hoje documentadas em `docs/auditoria-v1.md` §5).
- **Simulador** de carteira com pesos diferentes (a V2 usa pesos iguais, como a comparação base 100 da V1).
- **Logos dos ativos** com licença explícita (ver `docs/decisoes.md`). A V2 usa iniciais em círculo.
- **Armazenar o banco como asset de uma Release** (`gh release upload --clobber`) em vez de branch órfã, eliminando o force-push do bot.
