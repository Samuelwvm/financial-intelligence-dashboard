// Baixa os logos dos ativos do CDN da AllInvestView para public/logos/<slug>.png.
//
// Os termos permitem guardar cópia ("You may cache or proxy logos on your own
// servers"), desde que o link "Logos by AllInvestView" fique visível (rodapé).
// Servir do próprio site evita 404 no navegador e dependência do CDN em tempo real.
// Nunca falha o build: logo que não vier (404, rede fora) vira iniciais no site.
import { mkdir, readFile, readdir, rm, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const DATA = path.resolve(here, "../public/data/summary.json");
const OUT = path.resolve(here, "../public/logos");
const CDN = "https://cdn.tickerlogos.com/";

let summary;
try {
  summary = JSON.parse(await readFile(DATA, "utf-8"));
} catch {
  console.log("fetch-logos: summary.json ausente; pulando (o build vai apontar o erro de dados).");
  process.exit(0);
}

await mkdir(OUT, { recursive: true });
const wanted = summary.assets.filter((a) => a.logoDomain);
const keep = new Set();
let ok = 0;
const missing = [];

async function fetchOne(a) {
  try {
    const res = await fetch(CDN + a.logoDomain, { signal: AbortSignal.timeout(10_000) });
    const type = res.headers.get("content-type") ?? "";
    if (!res.ok || !type.startsWith("image/png")) throw new Error(`HTTP ${res.status} ${type}`);
    const buf = Buffer.from(await res.arrayBuffer());
    if (buf.length < 100) throw new Error("arquivo vazio");
    await writeFile(path.join(OUT, `${a.slug}.png`), buf);
    keep.add(`${a.slug}.png`);
    ok += 1;
  } catch (e) {
    missing.push(`${a.slug} (${a.logoDomain}): ${e.message}`);
  }
}

// Poucas requisições por vez (limite do CDN: 150 a cada 10 s).
for (let i = 0; i < wanted.length; i += 4) await Promise.all(wanted.slice(i, i + 4).map(fetchOne));

// Remove logos antigos que não vieram desta vez (ativo saiu do catálogo ou o CDN removeu).
for (const f of await readdir(OUT)) if (!keep.has(f)) await rm(path.join(OUT, f));

console.log(`fetch-logos: ${ok}/${wanted.length} logos; sem logo (iniciais): ${missing.length ? missing.join("; ") : "nenhum"}`);
