"use client";

import { AnimatePresence, motion, useReducedMotion } from "motion/react";
import { useEffect, useId, useRef, useState, type KeyboardEvent } from "react";
import { IconCheck, IconChevron } from "./icons";

export type SelectOption = { value: string; label: string };

/** Sem acento e minúsculo, para a busca por letra ("i" acha "Índia"). */
const fold = (s: string) => s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();

/**
 * Lista suspensa no padrão do sistema (a nativa do navegador não aceita estilo).
 * Padrão "select-only combobox" do WAI-ARIA: botão abre uma listbox; setas, Home/End,
 * Enter/Espaço, Esc e busca pela primeira letra. Fecha ao clicar fora ou sair com Tab.
 */
export function SelectMenu({
  label,
  value,
  options,
  onChange,
}: {
  label: string;
  value: string;
  options: SelectOption[];
  onChange: (value: string) => void;
}) {
  const id = useId();
  const reduce = useReducedMotion();
  const [open, setOpen] = useState(false);
  const [active, setActive] = useState(0);
  const root = useRef<HTMLDivElement>(null);
  const button = useRef<HTMLButtonElement>(null);
  const list = useRef<HTMLUListElement>(null);
  const selected = Math.max(
    0,
    options.findIndex((o) => o.value === value),
  );

  useEffect(() => {
    if (!open) return;
    const onDown = (e: PointerEvent) => {
      if (!root.current?.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("pointerdown", onDown);
    return () => document.removeEventListener("pointerdown", onDown);
  }, [open]);

  useEffect(() => {
    if (open) list.current?.focus();
  }, [open]);

  useEffect(() => {
    if (open) list.current?.querySelector<HTMLElement>(`[data-i="${active}"]`)?.scrollIntoView({ block: "nearest" });
  }, [open, active]);

  const show = (at = selected) => {
    setActive(at);
    setOpen(true);
  };
  const close = () => {
    setOpen(false);
    button.current?.focus();
  };
  const pick = (i: number) => {
    onChange(options[i].value);
    close();
  };

  const onButtonKey = (e: KeyboardEvent) => {
    if (["ArrowDown", "ArrowUp", "Enter", " "].includes(e.key)) {
      e.preventDefault();
      show();
    }
  };

  const onListKey = (e: KeyboardEvent) => {
    const last = options.length - 1;
    const keys: Record<string, () => void> = {
      ArrowDown: () => setActive((a) => Math.min(last, a + 1)),
      ArrowUp: () => setActive((a) => Math.max(0, a - 1)),
      Home: () => setActive(0),
      End: () => setActive(last),
      Enter: () => pick(active),
      " ": () => pick(active),
      Escape: close,
    };
    if (keys[e.key]) {
      e.preventDefault();
      keys[e.key]();
    } else if (e.key === "Tab") {
      setOpen(false);
    } else if (e.key.length === 1) {
      const k = fold(e.key);
      const from = options.findIndex((o, i) => i > active && fold(o.label).startsWith(k));
      const at = from >= 0 ? from : options.findIndex((o) => fold(o.label).startsWith(k));
      if (at >= 0) setActive(at);
    }
  };

  return (
    <div ref={root} className="flex items-center gap-2">
      <span id={`${id}-label`} className="text-[12px] font-semibold text-muted">
        {label}
      </span>
      <div className="relative">
        <button
          ref={button}
          type="button"
          id={`${id}-button`}
          aria-haspopup="listbox"
          aria-expanded={open}
          aria-controls={`${id}-list`}
          aria-labelledby={`${id}-label ${id}-button`}
          onClick={() => (open ? setOpen(false) : show())}
          onKeyDown={onButtonKey}
          className={`flex min-h-11 items-center gap-2 rounded-[10px] border bg-card pr-2.5 pl-3 text-[14px] font-semibold text-fg transition-colors ${
            open ? "border-fg" : "border-line hover:border-muted"
          }`}
        >
          {options[selected]?.label}
          <IconChevron
            size={18}
            className={`text-muted transition-transform motion-reduce:transition-none ${open ? "rotate-180" : ""}`}
          />
        </button>
        <AnimatePresence>
          {open && (
            <motion.ul
              ref={list}
              id={`${id}-list`}
              role="listbox"
              tabIndex={-1}
              aria-labelledby={`${id}-label`}
              aria-activedescendant={`${id}-opt-${active}`}
              onKeyDown={onListKey}
              initial={{ opacity: 0, y: reduce ? 0 : -4 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: reduce ? 0 : -4 }}
              transition={{ duration: reduce ? 0 : 0.15 }}
              className="absolute top-full left-0 z-30 mt-1.5 thin-scroll max-h-[min(24rem,60vh)] w-max min-w-full overflow-y-auto rounded-[14px] border border-line bg-card p-1 shadow-[var(--shadow)] outline-none"
            >
              {options.map((o, i) => {
                const isSel = i === selected;
                return (
                  <li
                    key={o.value}
                    id={`${id}-opt-${i}`}
                    data-i={i}
                    role="option"
                    aria-selected={isSel}
                    onPointerMove={() => setActive(i)}
                    onClick={() => pick(i)}
                    className={`flex min-h-10 cursor-pointer items-center justify-between gap-4 rounded-[10px] px-3 text-[14px] ${
                      i === active ? "bg-soft" : ""
                    } ${isSel ? "font-bold text-pos" : "font-semibold text-fg"}`}
                  >
                    {o.label}
                    <IconCheck size={16} className={isSel ? "" : "invisible"} />
                  </li>
                );
              })}
            </motion.ul>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
