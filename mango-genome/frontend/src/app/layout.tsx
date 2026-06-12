import type { Metadata } from "next";
import "./globals.css";
import AppHeader from "@/src/components/layout/AppHeader";
import Sidebar from "@/src/components/layout/Sidebar";
import AppFooter from "@/src/components/layout/AppFooter";

export const metadata: Metadata = {
  title: "Mango Genome Database",
  description:
    "Bioinformatics platform for Mangifera indica genome analysis — BLAST search, MSA, and genome data downloads.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="bg-[#060c1a] text-slate-200 min-h-screen flex flex-col">
        <AppHeader />
        <div className="flex flex-1">
          <Sidebar />
          <main className="flex-1 min-w-0 p-4 md:p-8 overflow-x-hidden">{children}</main>
        </div>
        <AppFooter />
      </body>
    </html>
  );
}
