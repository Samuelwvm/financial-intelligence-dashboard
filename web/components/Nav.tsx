"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "motion/react";
import { IconBrasil, IconCripto, IconEntenda, IconMundo, IconPainel } from "./icons";
import { ThemeToggle } from "./ThemeToggle";

export const NAV = [
  { href: "/", label: "Painel", Icon: IconPainel, group: "painel" },
  { href: "/brasil/", label: "Brasil", Icon: IconBrasil, group: "brasil" },
  { href: "/mundo/", label: "Mundo", Icon: IconMundo, group: "mundo" },
  { href: "/cripto/", label: "Cripto", Icon: IconCripto, group: "cripto" },
  { href: "/entenda/", label: "Entenda", Icon: IconEntenda, group: "entenda" },
] as const;

type Groups = Record<string, string>;

/** Aba ativa: rota direta ou, na tela /ativo/<slug>/, o grupo do ativo (brasil, mundo, cripto). */
function useActive(groups: Groups) {
  const path = usePathname() ?? "/";
  const base = process.env.NEXT_PUBLIC_BASE_PATH ?? "";
  const p = (path.startsWith(base) ? path.slice(base.length) : path).replace(/\/?$/, "/");
  const m = p.match(/^\/ativo\/([^/]+)\//);
  const hint = m ? groups[m[1]] : undefined;
  return (href: string, group: string) => {
    if (hint) return group === hint;
    if (href === "/") return p === "/";
    return p.startsWith(href);
  };
}

export function Sidebar({ groups }: { groups: Groups }) {
  const isActive = useActive(groups);
  return (
    <aside className="fixed inset-y-0 left-0 z-30 hidden w-[248px] flex-col gap-1.5 border-r border-line bg-card px-4 py-7 lg:flex">
      <Link href="/" className="px-3 pb-5 font-display text-[20px] font-semibold text-fg">
        Radar<span className="text-pos"> Financeiro</span>
      </Link>
      <nav aria-label="Principal" className="flex flex-col gap-1">
        {NAV.map(({ href, label, Icon, group: g }) => {
          const active = isActive(href, g);
          return (
            <Link
              key={href}
              href={href}
              aria-current={active ? "page" : undefined}
              className={`relative flex min-h-11 items-center gap-3 rounded-xl px-3 text-[15px] ${
                active ? "font-bold text-pos" : "font-medium text-muted hover:text-fg"
              }`}
            >
              {active && (
                <motion.span
                  layoutId="sidebar-active"
                  className="absolute inset-0 rounded-xl bg-pos-soft"
                  transition={{ type: "spring", stiffness: 500, damping: 40 }}
                  aria-hidden="true"
                />
              )}
              <Icon size={20} className="relative" />
              <span className="relative">{label}</span>
            </Link>
          );
        })}
      </nav>
      <div className="mt-auto px-1">
        <ThemeToggle withLabel />
      </div>
    </aside>
  );
}

export function TabBar({ groups }: { groups: Groups }) {
  const isActive = useActive(groups);
  return (
    <nav
      aria-label="Principal"
      className="fixed inset-x-0 bottom-0 z-30 flex border-t border-line bg-card pb-[max(10px,env(safe-area-inset-bottom))] lg:hidden"
    >
      {NAV.map(({ href, label, Icon, group: g }) => {
        const active = isActive(href, g);
        return (
          <Link
            key={href}
            href={href}
            aria-current={active ? "page" : undefined}
            className={`relative flex min-h-14 flex-1 flex-col items-center justify-center gap-[3px] text-[11px] ${
              active ? "font-bold text-pos" : "font-medium text-muted"
            }`}
          >
            {active && (
              <motion.span
                layoutId="tab-active"
                className="absolute top-0 h-[2px] w-8 rounded-full bg-pos"
                transition={{ type: "spring", stiffness: 500, damping: 40 }}
                aria-hidden="true"
              />
            )}
            <Icon size={22} />
            {label}
          </Link>
        );
      })}
    </nav>
  );
}
