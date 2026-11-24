"use client";

import { useEffect, useRef, useState } from "react";

/**
 * Logo do ativo (AllInvestView, baixado no build) num círculo de 40px.
 * Sem logo, ou se a imagem falhar no navegador, mostra as iniciais do ticker
 * (o mesmo plano B da V1).
 */
export function AssetLogo({ logo, ticker, size = 40 }: { logo?: string | null; ticker: string; size?: number }) {
  const [failed, setFailed] = useState(false);
  const img = useRef<HTMLImageElement>(null);
  // A imagem do HTML pré-renderizado pode falhar antes da hidratação, quando o
  // onError ainda não existe: confere o estado dela ao montar.
  useEffect(() => {
    const el = img.current;
    if (el && el.complete && el.naturalWidth === 0) setFailed(true);
  }, []);
  const initials = ticker.replace(/[^A-Z0-9]/gi, "").slice(0, 2).toUpperCase();
  if (logo && !failed) {
    return (
      <span
        aria-hidden="true"
        className="flex shrink-0 items-center justify-center overflow-hidden rounded-full border border-line bg-white"
        style={{ width: size, height: size }}
      >
        {/* eslint-disable-next-line @next/next/no-img-element -- export estático; PNG pequeno já servido pelo site */}
        <img
          ref={img}
          src={logo}
          alt=""
          width={size}
          height={size}
          loading="lazy"
          decoding="async"
          onError={() => setFailed(true)}
          className="size-full object-contain p-1"
        />
      </span>
    );
  }
  return (
    <span
      aria-hidden="true"
      className="flex shrink-0 items-center justify-center rounded-full bg-pos-soft font-display font-bold text-pos"
      style={{ width: size, height: size, fontSize: Math.round(size * 0.33) }}
    >
      {initials}
    </span>
  );
}
