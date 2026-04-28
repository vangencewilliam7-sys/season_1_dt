"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, Upload, MessageSquare, Brain, Sparkles } from "lucide-react";

const NAV_ITEMS = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/extract/new", label: "New Extraction", icon: Upload },
  { href: "/chat", label: "Test Persona", icon: MessageSquare },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 h-screen w-72 bg-slate-950/80 backdrop-blur-xl border-r border-slate-800/60 flex flex-col z-50">
      {/* Logo */}
      <div className="p-6 border-b border-slate-800/60">
        <div className="flex items-center gap-3 mb-1">
          <div className="w-10 h-10 bg-gradient-to-br from-indigo-500 to-sky-500 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <Brain className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold font-[family-name:var(--font-outfit)] text-white tracking-tight">
              Expert Persona
            </h1>
            <p className="text-[10px] text-slate-500 uppercase tracking-widest font-semibold">
              Digital Twin Engine
            </p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1">
        {NAV_ITEMS.map(({ href, label, icon: Icon }) => {
          const isActive = pathname === href || (href !== "/" && pathname.startsWith(href));
          return (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 group ${
                isActive
                  ? "bg-indigo-500/10 text-indigo-400 border border-indigo-500/20"
                  : "text-slate-400 hover:text-white hover:bg-slate-800/50"
              }`}
            >
              <Icon className={`w-4.5 h-4.5 ${isActive ? "text-indigo-400" : "text-slate-500 group-hover:text-slate-300"}`} />
              {label}
            </Link>
          );
        })}
      </nav>

      {/* Status */}
      <div className="p-4 border-t border-slate-800/60">
        <div className="glass-card p-4">
          <div className="flex items-center gap-2 mb-2">
            <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
            <span className="text-xs font-bold text-white">System Status</span>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between text-[11px]">
              <span className="text-slate-500">Backend</span>
              <span className="flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full pulse-dot"></span>
                <span className="text-emerald-400 font-semibold">Online</span>
              </span>
            </div>
            <div className="flex justify-between text-[11px]">
              <span className="text-slate-500">LLM Provider</span>
              <span className="text-slate-400 font-mono">Mock</span>
            </div>
          </div>
        </div>
        <p className="text-[10px] text-slate-600 text-center mt-3">v1.0.0 — Persona Engine</p>
      </div>
    </aside>
  );
}
