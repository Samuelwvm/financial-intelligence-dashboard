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

test("rodapé: aviso legal discreto e atribuição dos logos (link sem nofollow)", async ({ page }) => {
  for (const r of ["/", "/mundo/", "/ativo/aapl/"]) {
    await page.goto(r);
    const footer = page.locator("footer");
    await expect(footer).toContainText("não representam análise de valores mobiliários ou recomendação de investimento");
    const link = footer.getByRole("link", { name: "Logos by AllInvestView" });
    await expect(link).toHaveAttribute("href", "https://www.allinvestview.com/tools/ticker-logos/");
    expect(await link.getAttribute("rel")).toBeNull();
  }
});

test("em linguagem simples: troca de dica e pausa", async ({ page }) => {
  await page.goto("/");
  const card = page.locator("section", { has: page.getByRole("heading", { name: "EM LINGUAGEM SIMPLES" }) }).filter({ visible: true });
  const visible = () => card.locator("p[aria-hidden=false]").textContent();
  const first = await visible();
  await card.getByRole("button", { name: "Próxima dica" }).click();
  expect(await visible()).not.toBe(first);
  await card.getByRole("button", { name: /Pausar/ }).click();
  await expect(card.getByRole("button", { name: /Retomar/ })).toBeVisible();
});
