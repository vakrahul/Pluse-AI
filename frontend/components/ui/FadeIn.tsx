"use client";

import { motion } from "framer-motion";
import { ReactNode } from "react";

interface FadeInProps {
  children: ReactNode;
  delay?: number;
  className?: string;
  direction?: "up" | "left" | "none";
}

export function FadeIn({ children, delay = 0, className, direction = "up" }: FadeInProps) {
  const initial = direction === "up"
    ? { opacity: 0, y: 24 }
    : direction === "left"
    ? { opacity: 0, x: -20 }
    : { opacity: 0 };

  return (
    <motion.div
      initial={initial}
      whileInView={{ opacity: 1, y: 0, x: 0 }}
      viewport={{ once: true, margin: "-40px" }}
      transition={{ duration: 0.55, delay, ease: [0.22, 1, 0.36, 1] }}
      className={className}
    >
      {children}
    </motion.div>
  );
}
