// Pós-build do export estático.
//
// O cliente do Next 16.4 busca os arquivos de prefetch por segmento com nome
// "achatado" (ex.: /cripto/__next.cripto.__PAGE__.txt — ver
// convertSegmentPathToStaticExportFilename), mas o build grava em subpastas
// (/cripto/__next.cripto/__PAGE__.txt). Sem isto, cada prefetch gera um 404 no
// console (a navegação funciona, mas cai no fallback). Copiamos cada arquivo
// aninhado para o nome achatado; se uma versão futura já gerar plano, nada muda.
import { cp, readdir, stat } from "node:fs/promises";
import path from "node:path";

const root = path.resolve(process.argv[2] ?? "out");
let copied = 0;

async function walk(dir) {
  for (const name of await readdir(dir)) {
    const full = path.join(dir, name);
    if (!(await stat(full)).isDirectory()) continue;
    if (name.startsWith("__next.")) await flatten(full, dir, name);
    else await walk(full);
  }
}

async function flatten(segDir, parent, prefix) {
  for (const name of await readdir(segDir)) {
    const full = path.join(segDir, name);
    if ((await stat(full)).isDirectory()) {
      await flatten(full, parent, `${prefix}.${name}`);
    } else {
      await cp(full, path.join(parent, `${prefix}.${name}`));
      copied += 1;
    }
  }
}

await walk(root);
console.log(`flatten-segments: ${copied} arquivo(s) de prefetch copiados para o nome esperado pelo cliente`);
