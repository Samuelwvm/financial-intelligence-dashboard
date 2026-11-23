"use client";

import { motion } from "motion/react";
import { useEffect } from "react";

// Transição curta entre páginas (250 ms). Na primeira carga não anima, para
// não esconder o HTML pré-renderizado (protege o LCP).
let firstLoad = true;

export default function Template({ children }: { children: React.ReactNode }) {
  const animateIn = !firstLoad;
  useEffect(() => {
    firstLoad = false;
  }, []);
  return (
    <motion.div
      className="flex flex-col gap-3 lg:gap-5"
      initial={animateIn ? { opacity: 0, y: 6 } : false}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, ease: [0.2, 0.7, 0.2, 1] }}
    >
      {children}
    </motion.div>
  );
}
