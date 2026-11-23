// Servidor estático mínimo para testes (equivalente ao GitHub Pages sem basePath).
// Uso: node scripts/serve.mjs <pasta> <porta>
import { createServer } from "node:http";
import { readFile, stat } from "node:fs/promises";
import path from "node:path";

const root = path.resolve(process.argv[2] ?? "out");
const port = Number(process.argv[3] ?? 4175);
const TYPES = { ".html": "text/html; charset=utf-8", ".js": "text/javascript", ".css": "text/css", ".json": "application/json", ".woff2": "font/woff2", ".svg": "image/svg+xml", ".txt": "text/plain", ".ico": "image/x-icon", ".png": "image/png" };

createServer(async (req, res) => {
  const p = decodeURIComponent(new URL(req.url, "http://x").pathname);
  let file = path.join(root, p);
  if (!file.startsWith(root)) return res.writeHead(403).end();
  let status = 200;
  try {
    if ((await stat(file)).isDirectory()) file = path.join(file, "index.html");
    await stat(file);
  } catch {
    file = path.join(root, "404.html");
    status = 404;
  }
  let body;
  try {
    body = await readFile(file);
  } catch {
    return res.writeHead(404).end();
  }
  res.writeHead(status, { "content-type": TYPES[path.extname(file)] ?? "application/octet-stream" });
  res.end(body);
}).listen(port, () => console.log(`servindo ${root} em http://localhost:${port}`));
