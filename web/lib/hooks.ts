"use client";

import { useCallback, useEffect, useRef, useState, useSyncExternalStore } from "react";
import { onPortfolioChange, readPortfolio, writePortfolio } from "./portfolio";
import { portfolioSchema, type Period, type PortfolioData } from "./schema";

export const BASE_PATH = process.env.NEXT_PUBLIC_BASE_PATH ?? "";

/** Carteira salva no navegador; durante a pré-renderização usa a padrão. */
export function usePortfolio(candidates: string[], fallback: string[]) {
  const key = useRef<string>("");
  const cached = useRef<string[]>(fallback);
  const get = useCallback(() => {
    const list = readPortfolio(candidates, fallback);
    const k = list.join(",");
    if (k !== key.current) {
      key.current = k;
      cached.current = list;
    }
    return cached.current;
  }, [candidates, fallback]);
  const slugs = useSyncExternalStore(onPortfolioChange, get, () => fallback);
  return [slugs, writePortfolio] as const;
}

type State = { status: "loading" } | { status: "error" } | { status: "ready"; data: PortfolioData };

/** Busca /data/portfolio/<período>.json sob demanda (o período inicial vem embutido). */
export function usePortfolioData(period: Period, initial: PortfolioData): State {
  const [store, setStore] = useState<Record<string, PortfolioData>>({ [initial.period]: initial });
  const [failed, setFailed] = useState<Record<string, boolean>>({});

  useEffect(() => {
    if (store[period] || failed[period]) return;
    let alive = true;
    fetch(`${BASE_PATH}/data/portfolio/${period}.json`)
      .then((r) => {
        if (!r.ok) throw new Error(String(r.status));
        return r.json();
      })
      .then((j) => {
        const parsed = portfolioSchema.parse(j);
        if (alive) setStore((s) => ({ ...s, [period]: parsed }));
      })
      .catch(() => alive && setFailed((f) => ({ ...f, [period]: true })));
    return () => {
      alive = false;
    };
  }, [period, store, failed]);

  if (store[period]) return { status: "ready", data: store[period] };
  if (failed[period]) return { status: "error" };
  return { status: "loading" };
}
