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
  await page.goto("/");
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
  test("carrossel não anda sozinho com movimento reduzido", async ({ page }) => {
    await page.goto("/");
    const v = page.locator(".marquee-viewport");
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

test("carrossel: anda sozinho, 1º toque pausa sem navegar, 2º toque abre o ativo", async ({ page }) => {
  await page.goto("/");
  const section = page.locator("section", { has: page.getByRole("heading", { name: "Todos os ativos" }) });
  const viewport = section.locator(".marquee-viewport");
  const x = () => viewport.evaluate((el) => el.scrollLeft);
  await viewport.evaluate((el) => el.scrollIntoView({ block: "center" })); // longe da tab bar fixa
  const x0 = await x();
  await page.waitForTimeout(1500);
  expect(await x()).toBeGreaterThan(x0);
  const spot = { position: { x: 120, y: 40 }, force: true };
  await viewport.click(spot);
  expect(new URL(page.url()).pathname).toBe("/");
  await expect(section).toContainText("Pausado");
  const p1 = await x();
  await page.waitForTimeout(1200);
  expect(await x()).toBe(p1);
  await viewport.click(spot);
  await expect(page).toHaveURL(/\/ativo\//);
});

test("carrossel: arrastar rola e pausa", async ({ page }) => {
  await page.goto("/");
  const viewport = page.locator(".marquee-viewport");
  await viewport.evaluate((el) => el.scrollIntoView({ block: "center" }));
  await viewport.evaluate((el) => el.scrollBy({ left: 400 }));
  await expect(page.locator("section", { has: page.getByRole("heading", { name: "Todos os ativos" }) })).toContainText("Pausado");
});

test("carrossel: ativos da carteira têm indicativo", async ({ page }) => {
  await page.goto("/");
  const list = page.locator("ul[aria-label=Ativos]");
  await expect(list.locator("a", { hasText: "na sua carteira" })).toHaveCount(6);
  await expect(list.locator("a", { hasText: "Petrobras" })).toHaveClass(/border-pos/);
  await expect(list.locator("a", { hasText: "Apple" })).not.toHaveClass(/border-pos/);
});

test("em linguagem simples: sem botões; troca ao arrastar e pelas setas", async ({ page }) => {
  await page.goto("/");
  const card = page.locator("section", { has: page.getByRole("heading", { name: "EM LINGUAGEM SIMPLES" }) }).filter({ visible: true });
  await expect(card.getByRole("button")).toHaveCount(0);
  const visible = () => card.locator("p[aria-hidden=false]").textContent();
  const first = await visible();
  const box = (await card.boundingBox())!;
  await page.mouse.move(box.x + box.width * 0.8, box.y + box.height / 2);
  await page.mouse.down();
  await page.mouse.move(box.x + box.width * 0.2, box.y + box.height / 2, { steps: 5 });
  await page.mouse.up();
  const second = await visible();
  expect(second).not.toBe(first);
  await card.focus();
  await page.keyboard.press("ArrowLeft");
  expect(await visible()).toBe(first);
});
