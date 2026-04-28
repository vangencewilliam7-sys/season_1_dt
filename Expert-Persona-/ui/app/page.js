"use client";

import Link from "next/link";
import { Upload, Brain, MessageSquare, ArrowRight, Zap, Shield, Cpu } from "lucide-react";

const FEATURES = [
  {
    icon: Cpu,
    title: "Deep Document Scan",
    desc: "AI reads expert documents and extracts behavioral hypotheses using semantic analysis.",
    color: "from-indigo-500 to-violet-500",
  },
  {
    icon: Brain,
    title: "AI Journalist Interview",
    desc: "Auto-generates tough scenario questions to test and validate the expert's decision patterns.",
    color: "from-sky-500 to-cyan-500",
  },
  {
    icon: Shield,
    title: "Dynamic Persona Routing",
    desc: "Routes queries through the persona's drop zones and heuristics for grounded responses.",
    color: "from-emerald-500 to-teal-500",
  },
];

const SAMPLE_JOBS = [
  {
    id: "demo-job-72fb55d2",
    expert: "Alex Rivet",
    role: "Principal Solutions Architect",
    domain: "tech_consulting",
    status: "complete",
    heuristics: 2,
    dropZones: 5,
  },
];

export default function DashboardPage() {
  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8 slide-up">
      {/* Hero */}
      <div className="relative overflow-hidden rounded-2xl border border-slate-800/60 bg-gradient-to-br from-slate-900 via-slate-900 to-indigo-950/30 p-10">
        <div className="absolute top-0 right-0 w-96 h-96 bg-indigo-500/5 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2"></div>
        <div className="relative">
          <div className="flex items-center gap-2 mb-4">
            <Zap className="w-4 h-4 text-indigo-400" />
            <span className="text-xs font-bold uppercase tracking-widest text-indigo-400">
              Persona Extraction Engine
            </span>
          </div>
          <h1 className="text-4xl font-bold font-[family-name:var(--font-outfit)] text-white mb-3 tracking-tight">
            Build AI Digital Twins
          </h1>
          <p className="text-slate-400 max-w-xl text-base leading-relaxed mb-8">
            Upload expert documents, let the AI interview the knowledge base,
            and extract a high-fidelity persona manifest that powers your Digital Twin.
          </p>
          <div className="flex gap-4">
            <Link
              href="/extract/new"
              className="px-6 py-3 bg-gradient-to-r from-indigo-500 to-indigo-600 text-white font-bold rounded-xl hover:from-indigo-400 hover:to-indigo-500 transition-all shadow-lg shadow-indigo-500/20 flex items-center gap-2 text-sm"
            >
              <Upload className="w-4 h-4" />
              Start New Extraction
            </Link>
            <Link
              href="/chat"
              className="px-6 py-3 border border-slate-700 text-slate-300 font-semibold rounded-xl hover:bg-slate-800/50 hover:border-slate-600 transition-all flex items-center gap-2 text-sm"
            >
              <MessageSquare className="w-4 h-4" />
              Test a Persona
            </Link>
          </div>
        </div>
      </div>

      {/* Feature Cards */}
      <div className="grid grid-cols-3 gap-6">
        {FEATURES.map(({ icon: Icon, title, desc, color }) => (
          <div key={title} className="glass-card glow-border p-6 group hover:scale-[1.02] transition-transform duration-300">
            <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${color} flex items-center justify-center mb-4 shadow-lg`}>
              <Icon className="w-5 h-5 text-white" />
            </div>
            <h3 className="text-white font-bold mb-2 font-[family-name:var(--font-outfit)]">{title}</h3>
            <p className="text-sm text-slate-400 leading-relaxed">{desc}</p>
          </div>
        ))}
      </div>

      {/* Recent Extractions */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-white font-[family-name:var(--font-outfit)]">
            Recent Extractions
          </h2>
          <Link href="/extract/new" className="text-sm text-indigo-400 hover:text-indigo-300 flex items-center gap-1 font-semibold">
            View All <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
        <div className="space-y-3">
          {SAMPLE_JOBS.map((job) => (
            <Link
              key={job.id}
              href={`/extract/${job.id}/result`}
              className="glass-card p-5 flex items-center justify-between group hover:border-indigo-500/30 transition-all cursor-pointer block"
            >
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500/20 to-sky-500/20 border border-indigo-500/20 flex items-center justify-center">
                  <Brain className="w-5 h-5 text-indigo-400" />
                </div>
                <div>
                  <h4 className="text-white font-bold group-hover:text-indigo-300 transition-colors">
                    {job.expert}
                  </h4>
                  <p className="text-xs text-slate-500">{job.role} &bull; {job.domain}</p>
                </div>
              </div>
              <div className="flex items-center gap-6">
                <div className="text-right">
                  <p className="text-xs text-slate-500 mb-0.5">Heuristics</p>
                  <p className="text-lg font-bold text-white font-[family-name:var(--font-outfit)]">{job.heuristics}</p>
                </div>
                <div className="text-right">
                  <p className="text-xs text-slate-500 mb-0.5">Drop Zones</p>
                  <p className="text-lg font-bold text-white font-[family-name:var(--font-outfit)]">{job.dropZones}</p>
                </div>
                <span className="status-badge bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  {job.status}
                </span>
                <ArrowRight className="w-4 h-4 text-slate-600 group-hover:text-indigo-400 transition-colors" />
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
