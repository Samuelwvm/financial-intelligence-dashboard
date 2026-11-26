import { expect, test } from "@playwright/test";

const ROUTES = ["/", "/brasil/", "/mundo/", "/cripto/", "/entenda/", "/ativo/petr4/", "/ativo/dow-jones/", "/ativo/bitcoin/"];

for (const route of ROUTES) {
  test(`renderiza ${route} sem erros e sem scroll horizontal`, async ({ page }) => {
    const errors: string[] = [];
    page.on("pageerror", (e) => errors.push(e.message));
    page.on("console", (m) => m.type() === "error" && errors.push(m.text()));
    await page.goto(route);
    await expect(page.locator("h1")).toBeVisible();
    await expect(page.getByRole("navigation", { name: "Principal" }).first()).toBeVisible();
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
    expect(overflow).toBeLessThanOrEqual(0);
    expect(errors).toEqual([]);
  });
}

test("texto 'em tempo real' não aparece; data de atualização aparece", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator("body")).not.toContainText(/tempo real/i);
  await expect(page.locator("header p").first()).toContainText(/\d{2}\/\d{2}\/\d{4}/);
});

test("tema escuro persistido é aplicado antes da pintura (sem flash)", async ({ page }) => {
  await page.addInitScript(() => localStorage.setItem("radar:tema", "dark"));
  await page.goto("/", { waitUntil: "commit" });
  await page.waitForSelector("html[data-theme]");
  expect(await page.locator("html").getAttribute("data-theme")).toBe("dark");
  const bg = await page.evaluate(() => getComputedStyle(document.body).backgroundColor);
  expect(bg).toBe("rgb(11, 18, 16)");
});

test("alternar tema persiste", async ({ page }) => {
  await page.goto("/", { waitUntil: "networkidle" }); // o botão só responde depois da hidratação
  const before = await page.locator("html").getAttribute("data-theme");
  await page.getByRole("button", { name: /Ativar modo|Modo (claro|escuro)/ }).first().click();
  const after = await page.locator("html").getAttribute("data-theme");
  expect(after).not.toBe(before);
  await page.reload();
  expect(await page.locator("html").getAttribute("data-theme")).toBe(after);
});

test("variação sempre com ▲/▼ além da cor", async ({ page }) => {
  await page.goto("/");
  const chips = page.locator("span.rounded-full", { hasText: /[▲▼]/ });
  expect(await chips.count()).toBeGreaterThanOrEqual(5);
});

test("trocar período atualiza o gráfico do ativo", async ({ page }) => {
  await page.goto("/ativo/petr4/");
  const chart = page.getByRole("img", { name: /Gráfico do preço/ });
  await expect(chart).toHaveAttribute("aria-label", /30 dias/);
  await page.getByRole("button", { name: "1 ano" }).click();
  await expect(chart).toHaveAttribute("aria-label", /1 ano/);
});

test("glossário: filtro Câmbio não fica vazio (bug da V1) e busca funciona", async ({ page }) => {
  await page.goto("/entenda/");
  await page.getByRole("button", { name: "Câmbio", exact: true }).click();
  await expect(page.getByRole("button", { name: /Dólar comercial/ })).toBeVisible();
  await page.getByRole("button", { name: "Todos", exact: true }).click();
  await page.getByLabel("Buscar termo").fill("volatil");
  await expect(page.getByRole("button", { name: /^Volatilidade/ })).toBeVisible();
  await page.getByRole("button", { name: /^Volatilidade/ }).click();
  await expect(page.getByText(/desvio-padrão dos retornos/)).toBeVisible();
});

test("carteira: editar ativos persiste no navegador", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  await page.getByRole("button", { name: "Editar ativos", exact: true }).click();
  const dialog = page.getByRole("dialog", { name: "Editar ativos da carteira" });
  await dialog.getByText("Bitcoin").click();
  await page.keyboard.press("Escape");
  await expect(page.locator("#carteira-m").locator("..")).toContainText("7 ativos");
  await page.reload();
  await expect(page.locator("#carteira-m").locator("..")).toContainText("7 ativos");
});

test.describe("movimento reduzido", () => {
  test.use({ reducedMotion: "reduce" });
  test("sem rolagem horizontal com movimento reduzido", async ({ page }) => {
    await page.goto("/");
    // O que importa para quem usa: a página não se desloca para o lado.
    const x = await page.evaluate(() => {
      window.scrollTo(500, 0);
      return window.scrollX;
    });
    expect(x).toBe(0);
    // e nada escapa da rolagem dos carrosséis (ex.: textos só para leitor de tela)
    for (const r of ["/", "/brasil/", "/mundo/"]) {
      await page.goto(r);
      expect(await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth)).toBeLessThanOrEqual(0);
    }
  });
  test("carrossel não anda sozinho com movimento reduzido", async ({ page }) => {
    await page.goto("/");
    const v = page.locator(".marquee-viewport");
    await page.mouse.move(0, 0);
    const x0 = await v.evaluate((el) => el.scrollLeft);
    await page.waitForTimeout(1200);
    expect(await v.evaluate((el) => el.scrollLeft)).toBe(x0);
  });
  test("conteúdo visível e linhas desenhadas sem animação", async ({ page }) => {
    await page.goto("/cripto/");
    const line = page.locator("svg[role=img] path[stroke='var(--pos)']").first();
    await expect(line).toBeVisible();
    const anim = await page.evaluate(() => getComputedStyle(document.querySelector(".rise")!).animationName);
    expect(anim).toBe("none");
  });
});

test("logos: mostra o logo quando existe e iniciais quando não (Bradesco)", async ({ page }) => {
  await page.goto("/brasil/");
  const petr = page.getByRole("link", { name: /Petrobras/ });
  await expect(petr.locator("img")).toHaveAttribute("src", /logos\/petr4\.png$/);
  const bbdc = page.getByRole("link", { name: /Bradesco/ });
  await expect(bbdc.locator("img")).toHaveCount(0);
  await expect(bbdc).toContainText("BB");
});

test("logos: imagem que falha no navegador vira iniciais", async ({ page }) => {
  await page.route("**/logos/vale3.png", (r) => r.fulfill({ status: 404, body: "" }));
  await page.goto("/brasil/");
  const vale = page.getByRole("link", { name: /Vale/ });
  await expect(vale.locator("img")).toHaveCount(0);
  await expect(vale).toContainText("VA");
});

test("rodapé: aviso legal só no Entenda; atribuição dos logos onde há logos", async ({ page }) => {
  const cases: [string, boolean][] = [["/", true], ["/brasil/", true], ["/mundo/", true], ["/cripto/", true], ["/ativo/aapl/", true], ["/entenda/", false], ["/ativo/ibovespa/", false]];
  const aviso = "não representam análise de valores mobiliários ou recomendação de investimento";
  for (const [r, logos] of cases) {
    await page.goto(r);
    const footer = page.locator("footer");
    if (r === "/entenda/") await expect(footer).toContainText(aviso);
    else await expect(page.getByText(aviso)).toHaveCount(0);
    const link = footer.getByRole("link", { name: "Logos by AllInvestView" });
    if (logos) {
      await expect(link).toHaveAttribute("href", "https://www.allinvestview.com/tools/ticker-logos/");
      expect(await link.getAttribute("rel")).toBeNull();
    } else {
      await expect(link).toHaveCount(0);
    }
  }
});

test("glossário: exemplo destacado do texto de explicação", async ({ page }) => {
  await page.goto("/entenda/");
  const ex = page.getByText("EXEMPLO").first();
  await expect(ex).toBeVisible();
  const bg = await ex.locator("..").evaluate((el) => getComputedStyle(el).backgroundColor);
  expect(bg).not.toBe("rgba(0, 0, 0, 0)");
});



test("carrossel: ativos da carteira têm indicativo", async ({ page }) => {
  await page.goto("/");
  const list = page.locator("ul[aria-label=Ativos]");
  await expect(list.locator("a", { hasText: "na sua carteira" })).toHaveCount(6);
  await expect(list.locator("a", { hasText: "Petrobras" })).toHaveClass(/border-pos/);
  await expect(list.locator("a", { hasText: "Apple" })).not.toHaveClass(/border-pos/);
});


const isWeb = () => test.info().project.name === "web";

test("carrossel: anda sozinho e abre o ativo direto no toque/clique", async ({ page }) => {
  await page.goto("/");
  const viewport = page.locator(".marquee-viewport");
  await viewport.evaluate((el) => el.scrollIntoView({ block: "center" })); // longe da tab bar fixa
  const x = () => viewport.evaluate((el) => el.scrollLeft);
  await page.mouse.move(0, 0); // mouse longe: em cima do carrossel ele pausa
  const x0 = await x();
  // Sob carga o navegador desenha menos quadros: espera o movimento em vez de medir uma vez só.
  await expect.poll(x, { timeout: 8000 }).toBeGreaterThan(x0);
  await viewport.click({ position: { x: 120, y: 40 }, force: true });
  await expect(page).toHaveURL(/\/ativo\//);
});

test("carrossel: web pausa com o mouse e tem setas; celular arrasta e pausa", async ({ page }) => {
  await page.goto("/");
  const section = page.locator("section", { has: page.getByRole("heading", { name: "Todos os ativos" }) });
  const viewport = section.locator(".marquee-viewport");
  await viewport.evaluate((el) => el.scrollIntoView({ block: "center" }));
  const x = () => viewport.evaluate((el) => el.scrollLeft);
  if (isWeb()) {
    await viewport.hover({ position: { x: 300, y: 40 } });
    const p1 = await x();
    await page.waitForTimeout(1000);
    expect(await x()).toBe(p1);
    await page.mouse.move(0, 0);
    const before = await x();
    await section.getByRole("button", { name: "Próximos ativos" }).click();
    await expect.poll(async () => Math.abs((await x()) - before), { timeout: 8000 }).toBeGreaterThan(300);
    await expect(section).toContainText("Pausado por 20 s");
  } else {
    await expect(section.getByRole("button", { name: "Próximos ativos" })).toBeHidden();
    await viewport.evaluate((el) => el.scrollBy({ left: 400 }));
    await expect(section).toContainText("Pausado por 20 s");
  }
});

test("em linguagem simples: web usa setas e pontinhos; celular arrasta", async ({ page }) => {
  await page.goto("/");
  const card = page.locator("section", { has: page.getByRole("heading", { name: "EM LINGUAGEM SIMPLES" }) }).filter({ visible: true });
  const visible = () => card.locator("p[aria-hidden=false]").textContent();
  const first = await visible();
  if (isWeb()) {
    await card.getByRole("button", { name: "Próxima dica" }).click();
    expect(await visible()).not.toBe(first);
    await card.getByRole("button", { name: "Dica anterior" }).click();
    expect(await visible()).toBe(first);
    // arrastar com o mouse NÃO troca no computador
    const b = (await card.boundingBox())!;
    await page.mouse.move(b.x + b.width * 0.8, b.y + b.height * 0.7);
    await page.mouse.down();
    await page.mouse.move(b.x + b.width * 0.2, b.y + b.height * 0.7, { steps: 5 });
    await page.mouse.up();
    expect(await visible()).toBe(first);
  } else {
    await expect(card.getByRole("button")).toHaveCount(0);
    await card.evaluate((el) => {
      const r = el.getBoundingClientRect();
      const y = r.top + r.height / 2;
      const opts = { bubbles: true, pointerType: "touch", isPrimary: true, pointerId: 7 } as PointerEventInit;
      el.dispatchEvent(new PointerEvent("pointerdown", { ...opts, clientX: r.right - 30, clientY: y }));
      el.dispatchEvent(new PointerEvent("pointerup", { ...opts, clientX: r.left + 30, clientY: y }));
    });
    expect(await visible()).not.toBe(first);
  }
});

// FEATURE DESATIVADA (CDI/IPCA no gráfico; docs/decisoes.md §35–37):
// test("desempenho: carteira comparada ao Ibovespa, CDI e IPCA (liga/desliga)", async ({ page }) => {
//   test.skip(test.info().project.name !== "web", "no celular o gráfico fica no painel Risco x retorno");
//   await page.goto("/");
//   const card = page.locator("section", { has: page.getByRole("heading", { name: "Desempenho relativo (base 100)" }) });
//   const chart = card.getByRole("img", { name: /CDI e à inflação/ });
//   await expect(chart).toBeVisible();
//   const cdi = card.getByRole("button", { name: /^CDI/ });
//   await expect(cdi).toContainText(/[+−]\d+,\d%/);
//   await expect(card.getByRole("button", { name: /^IPCA/ })).toContainText(/%/);
//   const lines = () => chart.locator("path[fill=none]").count();
//   const before = await lines();
//   expect(before).toBe(4); // carteira, Ibovespa, CDI, IPCA
//   await cdi.click();
//   await expect(cdi).toHaveAttribute("aria-pressed", "false");
//   expect(await lines()).toBe(3);
// });

test("Brasil: inflação por grupo (IBGE) alterna mês/12 meses e desemprego com fonte", async ({ page }) => {
  await page.goto("/brasil/");
  const ipca = page.locator('section[aria-labelledby="ipca-grupos"]');
  await expect(ipca).toContainText("Fonte: IBGE");
  await expect(ipca.getByRole("listitem")).toHaveCount(9);
  await expect(ipca).toContainText("Em 12 meses, o que mais subiu foi");
  await ipca.getByRole("button", { name: "No mês" }).click();
  await expect(ipca).toContainText("mais pressionou o IPCA do mês");
  const des = page.locator('section[aria-labelledby="desemprego"]');
  await expect(des).toContainText("PNAD Contínua");
  await expect(des.getByRole("img", { name: /desemprego/i })).toBeVisible();
});

test("Mundo: juro real Brasil × EUA com fontes e conta de Fisher", async ({ page }) => {
  await page.goto("/mundo/");
  const card = page.locator('section[aria-labelledby="juro-real"]');
  await expect(card).toContainText("Juro real: Brasil × EUA");
  await expect(card).toContainText(/Brasil · \w{3}\/\d{2}/);
  await expect(card).toContainText("New York Fed");
  await expect(card).toContainText("um dos fatores que influenciam o dólar, não o único");
  await expect(card.getByRole("img", { name: /Juro real do Brasil e dos EUA/ })).toBeVisible();
});

test("Brasil: desemprego com filtro de período e inflação × meta", async ({ page }) => {
  await page.goto("/brasil/");
  const des = page.locator('section[aria-labelledby="desemprego"]');
  const chart = des.getByRole("img", { name: /Taxa de desemprego/ });
  await expect(chart).toHaveAttribute("aria-label", /2 anos/);
  await des.getByRole("button", { name: "Desde 2012" }).click();
  await expect(chart).toHaveAttribute("aria-label", /desde 2012/);
  await expect(des).toContainText("Desde 2012, o maior valor foi");
  const meta = page.locator('section[aria-labelledby="meta-inflacao"]');
  await expect(meta).toContainText(/(acima do teto|abaixo do piso|dentro do intervalo) da meta/);
  await expect(meta.getByRole("img", { name: /intervalo da meta/ })).toBeVisible();
  await expect(meta).toContainText(/\d+º mês seguido (fora|dentro) do intervalo/);
  await expect(meta).toContainText("Decreto 12.079/2024");
});
