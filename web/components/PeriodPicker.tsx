"use client";

import { PERIOD_LABEL } from "@/lib/format";
import { PERIODS, type Period } from "@/lib/schema";

/**
 * Dois estilos do mockup:
 * - "segment": botões de raio 10 sobre superfície suave (tela do ativo, painel web);
 * - "pill": chips de raio pílula com borda (Cripto, filtros).
 * Ativo = fundo texto-principal com texto invertido.
 */
export function PeriodPicker({
  value,
  onChange,
  variant = "segment",
  stretch = false,
  label = "Período",
  periods = PERIODS,
}: {
  value: Period;
  onChange: (p: Period) => void;
  variant?: "segment" | "pill";
  stretch?: boolean;
  label?: string;
  periods?: readonly Period[];
}) {
  return (
    <div
      role="group"
      aria-label={label}
      className={`flex ${variant === "pill" ? "no-scrollbar gap-2 overflow-x-auto" : "gap-1.5"} ${stretch ? "w-full" : "flex-wrap"}`}
    >
      {periods.map((p) => {
        const active = p === value;
        const base =
          variant === "pill"
            ? `min-h-11 shrink-0 rounded-full border px-4 text-[14px] font-semibold ${
                active ? "border-fg bg-fg text-inverse-fg" : "border-line bg-card text-fg hover:border-muted"
              }`
            : `min-h-11 rounded-[10px] text-[13px] font-semibold lg:px-4 lg:text-[14px] ${
                stretch ? "flex-1" : "px-4"
              } ${active ? "bg-fg text-inverse-fg" : "bg-soft text-fg hover:bg-line"}`;
        return (
          <button key={p} type="button" aria-pressed={active} onClick={() => onChange(p)} className={`${base} transition-colors`}>
            {PERIOD_LABEL[p]}
          </button>
        );
      })}
    </div>
  );
}
