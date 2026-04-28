"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Brain, BookOpen, Shield, AlertTriangle, CheckCircle2, Copy, ArrowLeft } from "lucide-react";
import Link from "next/link";

export default function ResultPage() {
  const { jobId } = useParams();
  const [manifest, setManifest] = useState(null);
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);
  const [activeTab, setActiveTab] = useState("overview");

  useEffect(() => {
    async function load() {
      try {
        const res = await fetch(`http://localhost:8000/extract/${jobId}/manifest`);
        if (!res.ok) {
          // Try loading the local manifest file as fallback
          const fallback = await fetch("/api/manifest");
          if (fallback.ok) {
            setManifest(await fallback.json());
          } else {
            throw new Error("Job not found");
          }
          return;
        }
        const data = await res.json();
        setManifest(data.manifest || data);
      } catch (e) {
        // Load hardcoded sample manifest for demo
        setManifest({
          expert_id: "c6c76022-cfd1-4237-836d-94638bf72b6c",
          extracted_at: "2026-04-22T14:10:07Z",
          manifest_version: 1,
          source_documents: [
            "expert_archi_001/knowledge_hub/architecture_principles.md",
            "expert_archi_001/master_cases/legacy_migration.md",
            "expert_archi_001/master_cases/scaling_ecommerce.md",
          ],
          identity: {
            name: "Alex Rivet",
            role: "Principal Solutions Architect",
            domain: "tech_consulting",
          },
          communication_style: {
            tone: ["direct", "pragmatic", "skeptical of hype"],
            verbosity: "concise",
            preferred_framing: "Risk-first evaluation",
          },
          heuristics: [
            {
              trigger: "When a performance bottleneck exists in a legacy DB during a time-sensitive period",
              decision: "Use Redis caching/buffering instead of a DB migration",
              reasoning: "Stability is more important than the 'perfect' DB when deadlines are short",
            },
            {
              trigger: "When presented with a legacy migration request",
              decision: "Force decomposition of the monolith into serverless/modern components",
              reasoning: "Migration is the ONLY time you have political leverage to fix architectural debt",
            },
          ],
          drop_zone_triggers: [
            "Mobile UX design",
            "Legacy Mainframe COBOL",
            "Frontend performance tuning",
            "Mobile application design",
            "Frontend Frameworks",
          ],
          confidence_threshold: 0.7,
        });
      }
    }
    load();
  }, [jobId]);

  if (!manifest) {
    return (
      <div className="p-8 flex items-center justify-center h-96">
        <div className="w-6 h-6 border-2 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin"></div>
      </div>
    );
  }

  const identity = manifest.identity || {};
  const style = manifest.communication_style || {};
  const heuristics = manifest.heuristics || [];
  const dropZones = manifest.drop_zone_triggers || [];

  const copyJSON = () => {
    navigator.clipboard.writeText(JSON.stringify(manifest, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const TABS = [
    { id: "overview", label: "Overview" },
    { id: "heuristics", label: "Heuristics" },
    { id: "boundaries", label: "Boundaries" },
    { id: "json", label: "Raw JSON" },
  ];

  return (
    <div className="p-8 max-w-5xl mx-auto slide-up">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <Link href="/" className="text-xs text-slate-500 hover:text-slate-400 flex items-center gap-1 mb-3 transition-colors">
            <ArrowLeft className="w-3 h-3" /> Back to Dashboard
          </Link>
          <h1 className="text-3xl font-bold text-white font-[family-name:var(--font-outfit)] tracking-tight">
            {identity.name || "Expert"}
          </h1>
          <p className="text-slate-400 mt-1">{identity.role} &bull; {identity.domain}</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={copyJSON}
            className="px-4 py-2.5 border border-slate-800 text-slate-300 font-semibold rounded-xl hover:bg-slate-800/50 transition-all flex items-center gap-2 text-xs"
          >
            <Copy className="w-3.5 h-3.5" />
            {copied ? "Copied!" : "Copy JSON"}
          </button>
          <Link
            href="/chat"
            className="px-4 py-2.5 bg-gradient-to-r from-indigo-500 to-indigo-600 text-white font-bold rounded-xl hover:from-indigo-400 hover:to-indigo-500 transition-all shadow-lg shadow-indigo-500/20 flex items-center gap-2 text-xs"
          >
            <Brain className="w-3.5 h-3.5" />
            Test This Persona
          </Link>
        </div>
      </div>

      {/* Stats Bar */}
      <div className="grid grid-cols-4 gap-4 mb-8">
        {[
          { label: "Heuristics", value: heuristics.length, color: "text-indigo-400" },
          { label: "Drop Zones", value: dropZones.length, color: "text-amber-400" },
          { label: "Confidence", value: `${(manifest.confidence_threshold * 100).toFixed(0)}%`, color: "text-emerald-400" },
          { label: "Sources", value: (manifest.source_documents || []).length, color: "text-sky-400" },
        ].map((s) => (
          <div key={s.label} className="glass-card p-4 text-center">
            <p className={`text-2xl font-bold font-[family-name:var(--font-outfit)] ${s.color}`}>{s.value}</p>
            <p className="text-[11px] text-slate-500 uppercase font-bold tracking-wider mt-1">{s.label}</p>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-6 bg-slate-900/50 rounded-xl p-1 border border-slate-800/40">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex-1 px-4 py-2.5 rounded-lg text-xs font-bold transition-all ${
              activeTab === tab.id
                ? "bg-indigo-500/15 text-indigo-400 border border-indigo-500/20"
                : "text-slate-500 hover:text-slate-300"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {activeTab === "overview" && (
        <div className="space-y-4 slide-up">
          {/* Communication Style */}
          <div className="glass-card glow-border p-6">
            <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-2 font-[family-name:var(--font-outfit)]">
              <BookOpen className="w-4 h-4 text-sky-400" />
              Communication Style
            </h3>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <p className="text-[11px] text-slate-500 uppercase font-bold tracking-wider mb-2">Tone</p>
                <div className="flex flex-wrap gap-1.5">
                  {(style.tone || []).map((t) => (
                    <span key={t} className="px-3 py-1 bg-sky-500/10 text-sky-400 border border-sky-500/20 rounded-lg text-xs font-semibold">
                      {t}
                    </span>
                  ))}
                </div>
              </div>
              <div>
                <p className="text-[11px] text-slate-500 uppercase font-bold tracking-wider mb-2">Verbosity</p>
                <p className="text-sm text-white font-semibold capitalize">{style.verbosity}</p>
              </div>
              <div>
                <p className="text-[11px] text-slate-500 uppercase font-bold tracking-wider mb-2">Framing</p>
                <p className="text-sm text-white font-semibold">{style.preferred_framing}</p>
              </div>
            </div>
          </div>

          {/* Source Documents */}
          <div className="glass-card p-6">
            <h3 className="text-sm font-bold text-white mb-3 font-[family-name:var(--font-outfit)]">Source Documents</h3>
            <div className="space-y-2">
              {(manifest.source_documents || []).map((doc, i) => (
                <div key={i} className="flex items-center gap-3 px-3 py-2 bg-slate-900/50 rounded-lg">
                  <BookOpen className="w-3.5 h-3.5 text-slate-500" />
                  <span className="text-xs text-slate-400 font-mono">{doc}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {activeTab === "heuristics" && (
        <div className="space-y-4 slide-up">
          {heuristics.map((h, i) => (
            <div key={i} className="glass-card glow-border p-6">
              <div className="flex items-start gap-4">
                <div className="w-8 h-8 rounded-lg bg-indigo-500/20 flex items-center justify-center shrink-0 mt-0.5">
                  <span className="text-sm font-bold text-indigo-400">{i + 1}</span>
                </div>
                <div className="space-y-3 flex-1">
                  <div>
                    <p className="text-[10px] text-indigo-400 uppercase font-bold tracking-wider mb-1">WHEN</p>
                    <p className="text-sm text-white">{h.trigger}</p>
                  </div>
                  <div>
                    <p className="text-[10px] text-emerald-400 uppercase font-bold tracking-wider mb-1">THEN DO</p>
                    <p className="text-sm text-white">{h.decision}</p>
                  </div>
                  <div>
                    <p className="text-[10px] text-amber-400 uppercase font-bold tracking-wider mb-1">BECAUSE</p>
                    <p className="text-sm text-slate-400 italic">{h.reasoning}</p>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {activeTab === "boundaries" && (
        <div className="space-y-4 slide-up">
          <div className="glass-card glow-border p-6">
            <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-2 font-[family-name:var(--font-outfit)]">
              <Shield className="w-4 h-4 text-amber-400" />
              Drop Zone Triggers
            </h3>
            <p className="text-xs text-slate-500 mb-4">
              Topics this expert does NOT handle. Queries matching these will be routed to escalation.
            </p>
            <div className="space-y-2">
              {dropZones.map((dz, i) => (
                <div key={i} className="flex items-center gap-3 px-4 py-3 bg-amber-500/5 border border-amber-500/10 rounded-xl">
                  <AlertTriangle className="w-4 h-4 text-amber-500/60" />
                  <span className="text-sm text-slate-300">{dz}</span>
                </div>
              ))}
            </div>
          </div>
          <div className="glass-card p-6">
            <h3 className="text-sm font-bold text-white mb-3 flex items-center gap-2 font-[family-name:var(--font-outfit)]">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              Confidence Threshold
            </h3>
            <div className="flex items-center gap-4">
              <div className="flex-1 h-3 bg-slate-800 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-emerald-500 to-emerald-400 rounded-full transition-all"
                  style={{ width: `${manifest.confidence_threshold * 100}%` }}
                ></div>
              </div>
              <span className="text-lg font-bold text-emerald-400 font-[family-name:var(--font-outfit)]">
                {(manifest.confidence_threshold * 100).toFixed(0)}%
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-2">
              Below this threshold, the AI responds as a Deputy (fallback identity) instead of the expert.
            </p>
          </div>
        </div>
      )}

      {activeTab === "json" && (
        <div className="slide-up">
          <div className="glass-card p-6 relative">
            <button
              onClick={copyJSON}
              className="absolute top-4 right-4 px-3 py-1.5 bg-slate-800 text-slate-400 rounded-lg text-xs font-semibold hover:text-white hover:bg-slate-700 transition-all"
            >
              {copied ? "Copied!" : "Copy"}
            </button>
            <pre className="text-xs text-slate-300 font-mono overflow-x-auto leading-relaxed">
              {JSON.stringify(manifest, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}
