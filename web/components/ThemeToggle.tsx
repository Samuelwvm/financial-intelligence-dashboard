"use client";

import { useSyncExternalStore } from "react";
import { IconMoon, IconSun } from "./icons";

type Theme = "light" | "dark";
const KEY = "radar:tema";

function current(): Theme {
  return document.documentElement.dataset.theme === "dark" ? "dark" : "light";
}

function subscribe(cb: () => void) {
  const obs = new MutationObserver(cb);
  obs.observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
  return () => obs.disconnect();
}

/** Script inline do <head>: aplica o tema antes da primeira pintura (sem flash). */
export const themeScript = `(function(){try{var t=localStorage.getItem("${KEY}");if(t!=="light"&&t!=="dark"){t=matchMedia("(prefers-color-scheme: dark)").matches?"dark":"light"}document.documentElement.dataset.theme=t}catch(e){}})()`;

export function ThemeToggle({ withLabel = false }: { withLabel?: boolean }) {
  const theme = useSyncExternalStore(subscribe, current, () => "light" as Theme);
  const next: Theme = theme === "dark" ? "light" : "dark";
  const label = next === "dark" ? "Ativar modo escuro" : "Ativar modo claro";

  function toggle() {
    document.documentElement.dataset.theme = next;
    try {
      localStorage.setItem(KEY, next);
    } catch {
      /* sem storage */
    }
  }

  return (
    <button
      type="button"
      onClick={toggle}
      aria-label={withLabel ? undefined : label}
      className={`inline-flex min-h-11 items-center gap-3 rounded-xl text-[15px] font-medium text-muted hover:text-fg ${
        withLabel ? "w-full px-3" : "min-w-11 justify-center"
      }`}
    >
      {theme === "dark" ? <IconSun size={20} /> : <IconMoon size={20} />}
      {withLabel && <span>{next === "dark" ? "Modo escuro" : "Modo claro"}</span>}
    </button>
  );
}
