"use client";

/**
 * Seletor compacto de período dentro de um card (ex.: 2 anos · 5 anos · 10 anos).
 * Botões de alternância (aria-pressed) sobre superfície suave; ativo = fundo texto-principal.
 */
export function Segmented<T extends string>({
  label,
  value,
  options,
  onChange,
}: {
  label: string;
  value: T;
  options: readonly { id: T; label: string }[];
  onChange: (id: T) => void;
}) {
  return (
    <div role="group" aria-label={label} className="inline-flex rounded-[10px] bg-soft p-0.5">
      {options.map((p) => (
        <button
          key={p.id}
          type="button"
          aria-pressed={value === p.id}
          onClick={() => onChange(p.id)}
          className={`min-h-9 rounded-[8px] px-2.5 text-[13px] font-semibold whitespace-nowrap transition-colors ${
            value === p.id ? "bg-fg text-inverse-fg" : "text-fg hover:bg-line"
          }`}
        >
          {p.label}
        </button>
      ))}
    </div>
  );
}
