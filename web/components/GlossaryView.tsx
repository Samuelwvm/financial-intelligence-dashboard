"use client";

import { AnimatePresence, motion, useReducedMotion } from "motion/react";
import { useEffect, useId, useMemo, useState } from "react";
import type { Glossary } from "@/lib/schema";
import { EmptyNote } from "./ui";

const norm = (s: string) => s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();

export function GlossaryView({ glossary }: { glossary: Glossary }) {
  const [q, setQ] = useState("");
  const [cat, setCat] = useState("Todos");
  const [open, setOpen] = useState<string | null>(glossary.terms[0]?.term ?? null);

  // ?termo=Selic (vindo dos cards de SELIC/CDI/IPCA) abre o termo.
  useEffect(() => {
    const t = new URLSearchParams(window.location.search).get("termo");
    if (!t) return;
    const hit = glossary.terms.find((x) => norm(x.term).startsWith(norm(t)));
    if (hit) {
      // eslint-disable-next-line react-hooks/set-state-in-effect -- parâmetro de URL só existe no navegador
      setOpen(hit.term);
      requestAnimationFrame(() => document.getElementById(`t-${norm(hit.term).replace(/\W+/g, "-")}`)?.scrollIntoView({ block: "center" }));
    }
  }, [glossary.terms]);

  const list = useMemo(() => {
    const nq = norm(q.trim());
    return glossary.terms.filter(
      (t) => (cat === "Todos" || t.category === cat) && (!nq || norm(t.term).includes(nq) || norm(t.definition).includes(nq)),
    );
  }, [glossary.terms, q, cat]);

  return (
    <>
      <div className="px-5 lg:max-w-[560px] lg:px-0">
        <label htmlFor="busca" className="sr-only">
          Buscar termo
        </label>
        <input
          id="busca"
          type="search"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Buscar termo, ex.: SELIC"
          autoComplete="off"
          className="min-h-12 w-full rounded-[14px] border border-line bg-card px-4 text-[15px] text-fg placeholder:text-muted"
        />
      </div>
      <div role="group" aria-label="Categorias" className="no-scrollbar flex gap-2 overflow-x-auto px-5 lg:flex-wrap lg:px-0">
        {["Todos", ...glossary.categories].map((c) => {
          const active = c === cat;
          return (
            <button
              key={c}
              type="button"
              aria-pressed={active}
              onClick={() => setCat(c)}
              className={`min-h-11 shrink-0 rounded-full border px-4 text-[14px] font-semibold transition-colors ${
                active ? "border-fg bg-fg text-inverse-fg" : "border-line bg-card text-fg hover:border-muted"
              }`}
            >
              {c}
            </button>
          );
        })}
      </div>
      <p className="sr-only" aria-live="polite">
        {list.length} {list.length === 1 ? "termo encontrado" : "termos encontrados"}
      </p>
      <div className="flex flex-col gap-2 px-5 lg:grid lg:grid-cols-2 lg:items-start lg:gap-3 lg:px-0">
        {list.length === 0 && <EmptyNote>Nenhum termo encontrado. Tente outra palavra ou a categoria &quot;Todos&quot;.</EmptyNote>}
        {list.map((t, i) => (
          <Term key={t.term} t={t} i={i} open={open === t.term} onToggle={() => setOpen(open === t.term ? null : t.term)} />
        ))}
      </div>
    </>
  );
}

function Term({
  t,
  i,
  open,
  onToggle,
}: {
  t: Glossary["terms"][number];
  i: number;
  open: boolean;
  onToggle: () => void;
}) {
  const id = useId();
  const reduce = useReducedMotion();
  const anchor = `t-${norm(t.term).replace(/\W+/g, "-")}`;
  return (
    <div id={anchor} style={{ "--i": Math.min(i, 8) } as React.CSSProperties} className="rise rounded-[14px] border border-line bg-card px-4">
      <h2>
        <button
          type="button"
          aria-expanded={open}
          aria-controls={id}
          onClick={onToggle}
          className="flex min-h-14 w-full items-center justify-between gap-2 text-left"
        >
          <span className="text-[16px] font-bold">{t.term}</span>
          <span className="rounded-full bg-pos-soft px-2 py-[3px] text-[11px] font-semibold text-pos">{t.category}</span>
        </button>
      </h2>
      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            id={id}
            role="region"
            initial={reduce ? false : { height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={reduce ? { opacity: 0 } : { height: 0, opacity: 0 }}
            transition={{ duration: 0.22, ease: [0.2, 0.7, 0.2, 1] }}
            className="overflow-hidden"
          >
            <p className="mb-2 text-[15px] leading-[1.45] text-muted">{t.definition}</p>
            <div className="mb-3.5 rounded-r-xl border-l-2 border-pos bg-soft px-3 py-2.5">
              <div className="text-[11px] font-bold tracking-[0.04em] text-pos">EXEMPLO</div>
              <p className="mt-0.5 text-[14px] leading-[1.45] text-fg">{t.example}</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
