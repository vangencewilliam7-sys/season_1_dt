"use client";

import { useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Upload, User, Globe, ArrowRight, AlertCircle, FileText, X, PlusCircle } from "lucide-react";
import { startExtraction, uploadDocuments } from "@/app/lib/api";

const DOMAINS = [
  { id: "generic", label: "Generic", desc: "Domain-agnostic extraction" },
  { id: "tech_consulting", label: "Tech Consulting", desc: "Architecture & engineering" },
  { id: "recruiting", label: "Recruiting", desc: "Talent acquisition & HR" },
  { id: "healthcare", label: "Healthcare", desc: "Clinical & medical" },
];

function FileDropzone({ title, desc, files, setFiles }) {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") setIsDragging(true);
    else if (e.type === "dragleave") setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFiles((prev) => [...prev, ...Array.from(e.dataTransfer.files)]);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      setFiles((prev) => [...prev, ...Array.from(e.target.files)]);
    }
  };

  const removeFile = (indexToRemove) => {
    setFiles(files.filter((_, idx) => idx !== indexToRemove));
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <label className="block text-[11px] text-slate-500 uppercase font-bold tracking-wider">{title}</label>
        <span className="text-[10px] text-slate-600">{desc}</span>
      </div>
      
      <div 
        className={`border-2 border-dashed rounded-xl p-6 transition-all text-center flex flex-col items-center justify-center cursor-pointer ${
          isDragging ? "border-indigo-500 bg-indigo-500/10" : "border-slate-800 bg-slate-950/40 hover:border-slate-700"
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input 
          ref={fileInputRef} 
          type="file" 
          multiple 
          className="hidden" 
          onChange={handleChange} 
          accept=".pdf,.md,.txt,.doc,.docx"
        />
        <PlusCircle className={`w-8 h-8 mb-3 transition-colors ${isDragging ? "text-indigo-400" : "text-slate-600"}`} />
        <p className="text-sm font-bold text-slate-300">Drag & drop files here</p>
        <p className="text-[11px] text-slate-500 mt-1">or click to browse</p>
      </div>

      {files.length > 0 && (
        <div className="grid grid-cols-2 gap-2 mt-3">
          {files.map((f, idx) => (
            <div key={idx} className="flex items-center justify-between bg-slate-900 border border-slate-800 rounded-lg p-2 px-3">
              <div className="flex items-center gap-2 truncate pr-2">
                <FileText className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
                <span className="text-xs text-slate-300 truncate">{f.name}</span>
              </div>
              <button 
                type="button" 
                onClick={(e) => { e.stopPropagation(); removeFile(idx); }}
                className="text-slate-500 hover:text-red-400 transition-colors"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function NewExtractionPage() {
  const router = useRouter();
  const [expertName, setExpertName] = useState("");
  const [expertRole, setExpertRole] = useState("");
  const [domain, setDomain] = useState("generic");
  
  const [knowledgeHubFiles, setKnowledgeHubFiles] = useState([]);
  const [masterCasesFiles, setMasterCasesFiles] = useState([]);
  
  const [isLoading, setIsLoading] = useState(false);
  const [loadingText, setLoadingText] = useState("");
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (knowledgeHubFiles.length === 0 && masterCasesFiles.length === 0) {
      setError("Please upload at least one document in either Knowledge Hub or Master Cases.");
      return;
    }

    setIsLoading(true);
    setError(null);

    // Auto-generate a slugified Expert ID
    const baseSlug = expertName.toLowerCase().replace(/[^a-z0-9]+/g, '_') || "expert";
    const uniqueId = Math.random().toString(36).substring(2, 7);
    const expertId = `${baseSlug}_${uniqueId}`;

    try {
      // 1. Upload files
      if (knowledgeHubFiles.length > 0) {
        setLoadingText("Uploading Knowledge Hub documents...");
        await uploadDocuments(expertId, "knowledge_hub", knowledgeHubFiles);
      }
      
      if (masterCasesFiles.length > 0) {
        setLoadingText("Uploading Master Cases...");
        await uploadDocuments(expertId, "master_cases", masterCasesFiles);
      }

      // 2. Start Extraction
      setLoadingText("Initializing Digital Twin Engine...");
      const data = await startExtraction({
        expertId,
        expertName,
        expertRole,
        readerType: "filesystem",
      });

      if (data.job_id) {
        router.push(`/extract/${data.job_id}/answer`);
      } else {
        setError(data.detail || "Failed to start extraction");
        setIsLoading(false);
      }
    } catch (err) {
      setError(err.message || "Cannot connect to backend. Is the server running?");
      setIsLoading(false);
    }
  };

  return (
    <div className="p-8 max-w-3xl mx-auto slide-up pb-24">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white font-[family-name:var(--font-outfit)] tracking-tight mb-2">
          New Persona Extraction
        </h1>
        <p className="text-slate-400">
          Upload expert documents and configure the extraction pipeline.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Expert Identity */}
        <div className="glass-card glow-border p-6 space-y-5">
          <h2 className="text-lg font-bold text-white font-[family-name:var(--font-outfit)] flex items-center gap-2">
            <User className="w-4.5 h-4.5 text-indigo-400" />
            Expert Identity
          </h2>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-[11px] text-slate-500 uppercase font-bold tracking-wider mb-1.5">
                Expert Name
              </label>
              <input
                type="text"
                value={expertName}
                onChange={(e) => setExpertName(e.target.value)}
                className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-4 py-3 text-sm text-white placeholder:text-slate-600 focus:outline-none focus:border-indigo-500/50 transition-colors"
                placeholder="Dr. Jane Smith"
                required
              />
            </div>
            <div>
              <label className="block text-[11px] text-slate-500 uppercase font-bold tracking-wider mb-1.5">
                Expert Role
              </label>
              <input
                type="text"
                value={expertRole}
                onChange={(e) => setExpertRole(e.target.value)}
                className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-4 py-3 text-sm text-white placeholder:text-slate-600 focus:outline-none focus:border-indigo-500/50 transition-colors"
                placeholder="Principal Architect"
                required
              />
            </div>
          </div>
        </div>

        {/* Document Source */}
        <div className="glass-card glow-border p-6 space-y-8">
          <h2 className="text-lg font-bold text-white font-[family-name:var(--font-outfit)] flex items-center gap-2 mb-2">
            <Upload className="w-4.5 h-4.5 text-sky-400" />
            Document Upload
          </h2>

          <FileDropzone 
            title="Base Knowledge (Knowledge Hub)" 
            desc="Resumes, publications, generic guidelines"
            files={knowledgeHubFiles}
            setFiles={setKnowledgeHubFiles}
          />
          
          <div className="h-px bg-slate-800/50 w-full" />

          <FileDropzone 
            title="Inference Knowledge (Master Cases)" 
            desc="Past decisions, post-mortems, specific project logs"
            files={masterCasesFiles}
            setFiles={setMasterCasesFiles}
          />
        </div>

        {/* Domain Selection */}
        <div className="glass-card glow-border p-6 space-y-5">
          <h2 className="text-lg font-bold text-white font-[family-name:var(--font-outfit)] flex items-center gap-2">
            <Globe className="w-4.5 h-4.5 text-emerald-400" />
            Domain Adapter
          </h2>

          <div className="grid grid-cols-2 gap-3">
            {DOMAINS.map((d) => (
              <button
                key={d.id}
                type="button"
                onClick={() => setDomain(d.id)}
                className={`p-4 rounded-xl border text-left transition-all ${
                  domain === d.id
                    ? "border-indigo-500/40 bg-indigo-500/10"
                    : "border-slate-800 bg-slate-950/40 hover:border-slate-700"
                }`}
              >
                <p className={`text-sm font-bold ${domain === d.id ? "text-indigo-300" : "text-slate-300"}`}>
                  {d.label}
                </p>
                <p className="text-[11px] text-slate-500 mt-0.5">{d.desc}</p>
              </button>
            ))}
          </div>
        </div>

        {/* Error */}
        {error && (
          <div className="flex items-center gap-3 p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
            <AlertCircle className="w-4 h-4 shrink-0" />
            {error}
          </div>
        )}

        {/* Submit */}
        <button
          type="submit"
          disabled={isLoading}
          className="w-full py-4 bg-gradient-to-r from-indigo-500 to-indigo-600 text-white font-bold rounded-xl hover:from-indigo-400 hover:to-indigo-500 transition-all shadow-lg shadow-indigo-500/20 flex items-center justify-center gap-2 text-sm disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? (
            <>
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin shrink-0"></div>
              {loadingText}
            </>
          ) : (
            <>
              <Upload className="w-4 h-4" />
              Upload & Start Extraction
              <ArrowRight className="w-4 h-4" />
            </>
          )}
        </button>
      </form>
    </div>
  );
}
