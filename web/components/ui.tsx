// Peças visuais compartilhadas (medidas do mockup).
import Link from "next/link";
import type { CSSProperties, ReactNode } from "react";
import { formatDate, formatPct, formatSignedPct } from "@/lib/format";
import { ThemeToggle } from "./ThemeToggle";

/** Chip de variação: pílula 2px 8px, 12px, peso 700, sempre com ▲/▼. */
export function Chip({ value, digits = 2, suffix, className = "" }: { value: number; digits?: number; suffix?: string; className?: string }) {
  const rounded = Number(value.toFixed(digits));
  const up = rounded >= 0;
  return (
    <span
      className={`num inline-block whitespace-nowrap rounded-full px-2 py-0.5 text-[12px] font-bold ${
        up ? "bg-pos-soft text-pos" : "bg-neg-soft text-neg"
      } ${className}`}
    >
      <span aria-hidden="true">{up ? "▲" : "▼"} </span>
      <span className="sr-only">{up ? "alta de " : "queda de "}</span>
      {suffix ?? formatPct(Math.abs(rounded), digits)}
    </span>
  );
}

export function signedClass(v: number) {
  return v >= 0 ? "text-pos" : "text-neg";
}

export { formatSignedPct };

/** Cabeçalho de página. Mobile: eyebrow + título 26px; web: título 32px. */
export function PageHeader({
  title,
  subtitle,
  back,
  icon,
}: {
  title: string;
  subtitle: ReactNode;
  back?: { href: string; label: string };
  icon?: ReactNode;
}) {
  return (
    <header className="flex items-start justify-between gap-3 px-5 pb-2 pt-[18px] lg:px-0 lg:pb-0 lg:pt-0">
      <div className="min-w-0">
        {back ? (
          <Link
            href={back.href}
            className="-my-[15px] -ml-1 inline-flex min-h-11 items-center gap-1 px-1 text-[12px] font-semibold tracking-[0.04em] text-pos lg:my-0 lg:min-h-0 lg:pb-1"
          >
            <span aria-hidden="true">‹</span> {back.label.toUpperCase()}
          </Link>
        ) : (
          <div className="text-[12px] font-semibold tracking-[0.04em] text-pos lg:hidden">RADAR FINANCEIRO</div>
        )}
        <h1 className="mt-0.5 flex items-center gap-2.5 font-display text-[26px] font-semibold leading-[1.15] text-fg lg:mt-0 lg:text-[32px] lg:font-bold">
          {icon}
          {title}
        </h1>
        <p className="mt-1 text-[14px] text-muted lg:text-[15px]">{subtitle}</p>
      </div>
      <div className="-mr-2 shrink-0 lg:hidden">
        <ThemeToggle />
      </div>
    </header>
  );
}

export function UpdatedAt({ date }: { date: string }) {
  return <>Atualizado diariamente · dados de {formatDate(date)}</>;
}

/** Card padrão: raio 16 (mobile) / 18 (web), borda 1px, padding 16/20. */
export function Card({
  children,
  className = "",
  i = 0,
  as: Tag = "section",
  lift = true,
  ...rest
}: {
  children: ReactNode;
  className?: string;
  i?: number;
  as?: "section" | "div" | "article";
  lift?: boolean;
} & React.HTMLAttributes<HTMLElement>) {
  return (
    <Tag
      style={{ "--i": i } as CSSProperties}
      className={`rise ${lift ? "lift" : ""} rounded-2xl border border-line bg-card p-4 lg:rounded-[18px] lg:p-5 ${className}`}
      {...rest}
    >
      {children}
    </Tag>
  );
}

/** Caixa de estatística (Máxima / Mínima / Volatilidade): superfície suave, raio 12. */
export function Stat({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div className="min-w-0 flex-1 rounded-xl bg-soft p-2.5">
      <div className="text-[11px] font-semibold text-muted">{label}</div>
      <div className="num mt-0.5 truncate font-display text-[16px] font-semibold">{value}</div>
    </div>
  );
}

export function Eyebrow({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <div className={`text-[13px] font-bold text-pos ${className}`}>{children}</div>;
}

export function ErrorNote({ children }: { children: ReactNode }) {
  return (
    <p role="alert" className="rounded-xl bg-neg-soft p-3 text-[14px] text-neg">
      {children}
    </p>
  );
}

export function EmptyNote({ children }: { children: ReactNode }) {
  return <p className="rounded-xl bg-soft p-4 text-center text-[14px] text-muted">{children}</p>;
}
