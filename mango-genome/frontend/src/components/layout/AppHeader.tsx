"use client";
import Image from "next/image";
import Link from "next/link";

export default function AppHeader() {
  return (
    <header className="bg-navy-800 border-b border-[#1e3054] sticky top-0 z-50">
      <div className="max-w-screen-xl mx-auto px-4 py-3 flex items-center justify-between gap-4">
        {/* Left logo */}
        <div className="flex-shrink-0">
          <Image
            src="/images/SSUETLogo.png"
            alt="SSUET Logo"
            width={90}
            height={90}
            className="object-contain"
            priority
          />
        </div>

        {/* Centre title */}
        <div className="flex-1 text-center">
          <Link href="/about" className="block">
            <h1 className="text-xl md:text-2xl font-bold text-accent tracking-wide">
              Mango Genome Database
            </h1>
          </Link>
          <p className="text-xs text-slate-400 mt-0.5 hidden sm:block">
            Department of Bioinformatics &nbsp;·&nbsp; Sir Syed University of Engineering &amp; Technology, Karachi
          </p>
        </div>

        {/* Right logo */}
        <div className="flex-shrink-0">
          <Image
            src="/images/logo.png"
            alt="MGD Logo"
            width={90}
            height={90}
            className="object-contain"
            priority
          />
        </div>
      </div>
    </header>
  );
}
