import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Recoverwell — Context-aware recovery",
  description: "An explainable, adaptive recovery activity recommendation research platform.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}