"use client";

import { motion } from "framer-motion";

export function HeartTrail({ className }: { className?: string }) {
  return (
    <div className={`relative flex items-center ${className ?? "h-16 w-full"}`}>
      {/* Static baseline */}
      <div className="absolute inset-x-0 top-1/2 h-px -translate-y-1/2 bg-gradient-to-r from-transparent via-pulse-500/40 to-transparent" />

      {/* Glowing trail that grows from left to right */}
      <motion.div
        className="absolute left-0 top-1/2 h-px -translate-y-1/2 rounded-full bg-gradient-to-r from-transparent via-pulse-400 to-pulse-400/0"
        initial={{ width: "0%" }}
        animate={{ width: "100%" }}
        transition={{ duration: 3, ease: "easeInOut", repeat: Infinity, repeatDelay: 0.6 }}
      />

      {/* Heart icon travelling across */}
      <motion.div
        className="absolute top-1/2 -translate-y-1/2"
        initial={{ left: "0%" }}
        animate={{ left: "100%" }}
        transition={{ duration: 3, ease: "easeInOut", repeat: Infinity, repeatDelay: 0.6 }}
      >
        {/* Drop shadow glow */}
        <motion.div
          animate={{ scale: [1, 1.25, 1] }}
          transition={{ duration: 0.7, repeat: Infinity, ease: "easeInOut" }}
          className="relative"
        >
          <svg
            viewBox="0 0 24 24"
            fill="currentColor"
            className="h-7 w-7 -translate-x-1/2 text-pulse-400 drop-shadow-[0_0_8px_rgba(45,212,191,0.9)]"
          >
            <path d="M12 21.593c-.425-.332-8.5-6.705-8.5-11.593 0-3.038 2.462-5.5 5.5-5.5 1.766 0 3.332.874 4.326 2.224C14.32 5.374 15.886 4.5 17.652 4.5c3.038 0 5.5 2.462 5.5 5.5 0 4.888-8.075 11.261-8.5 11.593l-1.152.907-1.152-.907z" />
          </svg>
          {/* Pulse ring */}
          <motion.div
            className="absolute inset-0 -translate-x-1/2 rounded-full border border-pulse-400/50"
            animate={{ scale: [1, 2.2], opacity: [0.6, 0] }}
            transition={{ duration: 0.9, repeat: Infinity, ease: "easeOut" }}
          />
        </motion.div>
      </motion.div>
    </div>
  );
}
