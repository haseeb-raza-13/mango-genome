"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import {
  Dna,
  AlignJustify,
  Download,
  Info,
  HelpCircle,
  ChevronDown,
  ChevronRight,
  Menu,
  X,
} from "lucide-react";
import clsx from "clsx";

const nav = [
  { label: "BLAST", href: "/blast", icon: Dna },
  { label: "MSA", href: "/msa", icon: AlignJustify },
  { label: "Downloads", href: "/downloads", icon: Download },
  {
    label: "About",
    icon: Info,
    children: [
      { label: "Project", href: "/about" },
      { label: "Disclaimer", href: "/about/disclaimer" },
      { label: "Work", href: "/about/work" },
      { label: "Literature", href: "/about/literature" },
    ],
  },
  {
    label: "Help",
    icon: HelpCircle,
    children: [
      { label: "User Guide", href: "/help" },
      { label: "Contact Us", href: "/help/contact" },
    ],
  },
];

function NavItem({ item, pathname }: { item: (typeof nav)[0]; pathname: string | null }) {
  const isChildActive = "children" in item && item.children?.some((c) => pathname === c.href) || false;
  const [open, setOpen] = useState(isChildActive);
  const Icon = item.icon;

  if ("href" in item && item.href) {
    const active = pathname !== null && pathname === item.href;
    return (
      <Link
        href={item.href}
        className={clsx(
          "flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-all",
          active
            ? "bg-accent/15 text-accent border border-accent/30"
            : "text-slate-300 hover:bg-white/5 hover:text-white"
        )}
      >
        <Icon size={16} />
        {item.label}
      </Link>
    );
  }

  return (
    <div>
      <button
        onClick={() => setOpen((o) => !o)}
        className={clsx(
          "w-full flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-all",
          isChildActive ? "text-accent" : "text-slate-300 hover:bg-white/5 hover:text-white"
        )}
      >
        <Icon size={16} />
        <span className="flex-1 text-left">{item.label}</span>
        {open ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
      </button>
      {open && (
        <div className="ml-7 mt-0.5 space-y-0.5 border-l border-[#1e3054] pl-3">
          {"children" in item &&
            item.children?.map((child) => (
              <Link
                key={child.href}
                href={child.href}
                className={clsx(
                  "block px-3 py-2 rounded text-xs font-medium transition-all",
                  pathname === child.href
                    ? "text-accent"
                    : "text-slate-400 hover:text-white"
                )}
              >
                {child.label}
              </Link>
            ))}
        </div>
      )}
    </div>
  );
}

export default function Sidebar() {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <>
      {/* Mobile toggle */}
      <button
        className="md:hidden fixed top-4 left-4 z-50 p-2 rounded-lg bg-navy-700 border border-[#1e3054] text-slate-300"
        onClick={() => setMobileOpen((o) => !o)}
      >
        {mobileOpen ? <X size={18} /> : <Menu size={18} />}
      </button>

      {/* Backdrop */}
      {mobileOpen && (
        <div
          className="md:hidden fixed inset-0 z-30 bg-black/60"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Sidebar panel */}
      <aside
        className={clsx(
          "fixed top-0 left-0 h-full z-40 w-56 bg-navy-800 border-r border-[#1e3054] flex flex-col transition-transform duration-200",
          "md:translate-x-0 md:static md:h-auto",
          mobileOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        <div className="pt-16 md:pt-4 px-3 pb-4 flex-1 overflow-y-auto space-y-1">
          <p className="px-4 pb-2 text-xs text-slate-500 uppercase tracking-widest font-semibold">
            Navigation
          </p>
          {nav.map((item) => (
            <NavItem key={item.label} item={item} pathname={pathname} />
          ))}
        </div>

        <div className="px-4 py-3 border-t border-[#1e3054] text-xs text-slate-500">
          <p>Mango Genome Database</p>
          <p className="text-slate-600">v1.0.0</p>
        </div>
      </aside>
    </>
  );
}
