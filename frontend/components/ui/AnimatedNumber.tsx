"use client";

import { motion, useSpring, useTransform } from "framer-motion";
import { useEffect } from "react";

export function AnimatedNumber({ value, format }: { value: number; format?: "currency" | "percent" | "number" }) {
  const spring = useSpring(0, { stiffness: 60, damping: 20 });
  const display = useTransform(spring, (v) => {
    if (format === "currency") return `₹${(v / 10000000).toFixed(1)}Cr`;
    if (format === "percent") return `${v.toFixed(1)}%`;
    return Math.round(v).toLocaleString("en-IN");
  });

  useEffect(() => {
    spring.set(value);
  }, [spring, value]);

  return <motion.span>{display}</motion.span>;
}
