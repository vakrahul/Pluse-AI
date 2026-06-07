import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "PulseIQ — Healthcare Sales Intelligence",
  description: "Governed HCP analytics, prescriber networks, and compliance knowledge for pharma teams.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
