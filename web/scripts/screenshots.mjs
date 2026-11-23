// Capturas da V2 (390×844 e 1440×900, claro e escuro) + artboards do mockup.
// Uso: npm run build && node scripts/screenshots.mjs  → docs/screenshots/
import { chromium } from "@playwright/test";
import { createServer } from "node:http";
import { readFile, mkdir, stat } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.resolve(here, "../out");
const SHOTS = path.resolve(here, "../../docs/screenshots");
const MOCK = path.resolve(here, "../../design/mockup/preview");
const TYPES = { ".html": "text/html", ".js": "text/javascript", ".css": "text/css", ".json": "application/json", ".woff2": "font/woff2", ".svg": "image/svg+xml", ".txt": "text/plain" };

const server = createServer(async (req, res) => {
  let p = decodeURIComponent(new URL(req.url, "http://x").pathname);
  let file = path.join(OUT, p);
  try {
    if ((await stat(file)).isDirectory()) file = path.join(file, "index.html");
  } catch {
    file = path.join(OUT, "404.html");
  }
  try {
    res.writeHead(200, { "content-type": TYPES[path.extname(file)] ?? "application/octet-stream" });
    res.end(await readFile(file));
  } catch {
    res.writeHead(404).end();
  }
});
await new Promise((r) => server.listen(4174, r));
const BASE = "http://localhost:4174";

const ROUTES = [
  ["painel", "/"],
  ["ativo", "/ativo/petr4/"],
  ["brasil", "/brasil/"],
  ["mundo", "/mundo/"],
  ["cripto", "/cripto/"],
  ["entenda", "/entenda/"],
];
const VIEWPORTS = [
  ["mobile", { width: 390, height: 844 }],
  ["web", { width: 1440, height: 900 }],
];
const only = process.argv[2];

await mkdir(SHOTS, { recursive: true });
const browser = await chromium.launch();
for (const theme of ["light", "dark"]) {
  for (const [vp, size] of VIEWPORTS) {
    const ctx = await browser.newContext({ viewport: size, deviceScaleFactor: 1, colorScheme: theme, reducedMotion: "reduce" });
    await ctx.addInitScript((t) => localStorage.setItem("radar:tema", t), theme);
    const page = await ctx.newPage();
    for (const [name, route] of ROUTES) {
      if (only && name !== only) continue;
      await page.goto(BASE + route, { waitUntil: "networkidle" });
      await page.waitForTimeout(300);
      await page.screenshot({ path: path.join(SHOTS, `${name}-${vp}-${theme}.png`) });
      await page.screenshot({ path: path.join(SHOTS, `${name}-${vp}-${theme}-full.png`), fullPage: true });
    }
    await ctx.close();
  }
}

// Mockup (referência) nos mesmos tamanhos.
const MOCKS = [
  ["painel-mobile-light", "Painel.html", 390, 844], ["painel-mobile-dark", "Painel-Dark.html", 390, 844],
  ["ativo-mobile-light", "Ativo.html", 390, 844], ["ativo-mobile-dark", "Ativo-Dark.html", 390, 844],
  ["cripto-mobile-light", "Cripto.html", 390, 844], ["cripto-mobile-dark", "Cripto-Dark.html", 390, 844],
  ["entenda-mobile-light", "Entenda.html", 390, 844], ["entenda-mobile-dark", "Entenda-Dark.html", 390, 844],
  ["painel-web-light", "Web-Painel.html", 1440, 900], ["painel-web-dark", "Web-Painel-Dark.html", 1440, 900],
];
for (const [name, file, width, height] of MOCKS) {
  if (only && !name.startsWith(only)) continue;
  const ctx = await browser.newContext({ viewport: { width, height }, deviceScaleFactor: 1, reducedMotion: "reduce" });
  const page = await ctx.newPage();
  await page.goto(pathToFileURL(path.join(MOCK, file)).href, { waitUntil: "networkidle" });
  await page.waitForTimeout(300);
  await page.screenshot({ path: path.join(SHOTS, `mockup-${name}.png`) });
  await ctx.close();
}
await browser.close();
server.close();
console.log(`capturas em ${SHOTS}`);
