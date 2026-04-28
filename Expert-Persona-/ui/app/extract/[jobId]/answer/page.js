"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { Brain, HelpCircle, AlertTriangle, Send, Loader2, CheckCircle2, ChevronRight } from "lucide-react";
import { getJobStatus, getQuestions, submitAnswers } from "@/app/lib/api";

export default function ExpertAnsweringPage() {
  const { jobId } = useParams();
  const router = useRouter();

  const [status, setStatus] = useState("loading"); // loading, awaiting_answers, submitting, complete, error
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({}); // { index: { answer, confidence, is_outside_scope } }
  const [error, setError] = useState(null);
  const [pollingStatus, setPollingStatus] = useState("Initializing Deep Scan...");

  // Poll for status
  useEffect(() => {
    let interval;

    const pollStatus = async () => {
      try {
        const data = await getJobStatus(jobId);
        
        if (data.status === "failed") {
          setStatus("error");
          setError(data.error || "Extraction failed.");
          clearInterval(interval);
          return;
        }

        if (data.status === "awaiting_answers") {
          setStatus("awaiting_answers");
          clearInterval(interval);
          fetchQuestions();
        } else if (data.status === "complete") {
          setStatus("complete");
          clearInterval(interval);
          router.push(`/extract/${jobId}/result`);
        } else {
          // Update polling message based on current node
          if (data.current_node === "loading_documents") setPollingStatus("Loading documents from Knowledge Hub...");
          else if (data.current_node === "ingestion") setPollingStatus("Deep Scan running (Llama 3.1 70B)...");
          else if (data.current_node === "journalist") setPollingStatus("Generating scenario questions...");
          else if (data.current_node === "answer_processor") setPollingStatus("Processing your manual answers...");
          else if (data.current_node === "compiler") setPollingStatus("Assembling final PersonaManifest...");
        }
      } catch (err) {
        // Keep polling on temporary network errors
        console.error("Polling error:", err);
      }
    };

    if (status === "loading" || status === "submitting") {
      pollStatus();
      interval = setInterval(pollStatus, 3000);
    }

    return () => clearInterval(interval);
  }, [jobId, status, router]);

  const fetchQuestions = async () => {
    try {
      const data = await getQuestions(jobId);
      const fetchedQuestions = data.questions || [];
      setQuestions(fetchedQuestions);
      
      // Initialize answer state
      const initialAnswers = {};
      fetchedQuestions.forEach((q, i) => {
        initialAnswers[i] = { answer: "", confidence: "high", is_outside_scope: false };
      });
      setAnswers(initialAnswers);
    } catch (err) {
      setStatus("error");
      setError("Failed to load questions. " + err.message);
    }
  };

  const handleAnswerChange = (index, field, value) => {
    setAnswers(prev => ({
      ...prev,
      [index]: { ...prev[index], [field]: value }
    }));
  };

  const handleSubmit = async () => {
    // Validate that non-outside-scope questions have answers
    const payload = Object.keys(answers).map(key => ({
      question_index: parseInt(key),
      ...answers[key]
    }));

    for (const ans of payload) {
      if (!ans.is_outside_scope && !ans.answer.trim()) {
        setError("Please answer all in-scope questions before submitting.");
        return;
      }
    }

    setStatus("submitting");
    setError(null);
    setPollingStatus("Submitting answers to Processor...");

    try {
      await submitAnswers(jobId, payload);
      // Polling will automatically pick up the new status and redirect when complete
    } catch (err) {
      setStatus("awaiting_answers");
      setError("Failed to submit answers. " + err.message);
    }
  };

  if (status === "loading" || status === "submitting" || status === "complete") {
    return (
      <div className="flex h-[80vh] items-center justify-center p-8 slide-up">
        <div className="glass-card glow-border p-10 max-w-md w-full text-center space-y-6">
          <div className="w-20 h-20 mx-auto rounded-full bg-indigo-500/10 flex items-center justify-center border border-indigo-500/20 shadow-[0_0_40px_-10px_rgba(99,102,241,0.3)]">
            {status === "complete" ? (
              <CheckCircle2 className="w-10 h-10 text-emerald-400" />
            ) : (
              <Loader2 className="w-10 h-10 text-indigo-400 animate-spin" />
            )}
          </div>
          <div>
            <h2 className="text-xl font-bold text-white font-[family-name:var(--font-outfit)] mb-2">
              {status === "submitting" ? "Processing Answers" : status === "complete" ? "Extraction Complete" : "AI Ingestion Active"}
            </h2>
            <p className="text-sm text-slate-400 animate-pulse">
              {pollingStatus}
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (status === "error") {
    return (
      <div className="p-8 max-w-3xl mx-auto slide-up">
        <div className="glass-card border-red-500/30 p-8 text-center space-y-4">
          <AlertTriangle className="w-12 h-12 text-red-400 mx-auto" />
          <h2 className="text-xl font-bold text-white">Extraction Pipeline Halted</h2>
          <p className="text-slate-400">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-4xl mx-auto slide-up pb-32">
      <div className="mb-8 flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white font-[family-name:var(--font-outfit)] tracking-tight mb-2 flex items-center gap-3">
            <Brain className="w-8 h-8 text-indigo-400" />
            Expert Knowledge Calibration
          </h1>
          <p className="text-slate-400 text-lg">
            The AI has generated {questions.length} scenarios based on your documents. <br/>
            Answer as you naturally would in the real world.
          </p>
        </div>
      </div>

      {error && (
        <div className="mb-6 p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm flex items-center gap-2">
          <AlertTriangle className="w-4 h-4" />
          {error}
        </div>
      )}

      <div className="space-y-6">
        {questions.map((q, idx) => {
          const ans = answers[idx] || { answer: "", confidence: "high", is_outside_scope: false };
          const isBoundary = q.boundary_area !== undefined;
          
          return (
            <div key={idx} className={`glass-card border p-6 transition-all ${ans.is_outside_scope ? "opacity-60 border-slate-800" : isBoundary ? "border-amber-500/20" : "border-indigo-500/20 glow-border"}`}>
              <div className="flex items-start gap-4 mb-4">
                <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 mt-1 ${isBoundary ? "bg-amber-500/10 text-amber-400" : "bg-indigo-500/10 text-indigo-400"}`}>
                  {isBoundary ? <AlertTriangle className="w-4 h-4" /> : <HelpCircle className="w-4 h-4" />}
                </div>
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">
                      {isBoundary ? "Boundary Check" : "Validation Scenario"}
                    </span>
                    <span className="text-[10px] text-slate-600 px-2 py-0.5 rounded-full bg-slate-800">
                      Probing: {q.tests_hypothesis || q.boundary_area}
                    </span>
                  </div>
                  <h3 className="text-base text-white leading-relaxed font-medium">
                    {q.question}
                  </h3>
                </div>
              </div>

              <div className="pl-12 space-y-4">
                <textarea
                  value={ans.answer}
                  onChange={(e) => handleAnswerChange(idx, "answer", e.target.value)}
                  disabled={ans.is_outside_scope}
                  placeholder={ans.is_outside_scope ? "Skipped: Outside your scope of expertise" : "Type your honest, professional answer here..."}
                  className="w-full h-32 bg-slate-950/60 border border-slate-800 rounded-xl p-4 text-sm text-white placeholder:text-slate-600 focus:outline-none focus:border-indigo-500/50 disabled:bg-slate-900/50 disabled:cursor-not-allowed transition-all resize-none"
                />

                <div className="flex items-center justify-between pt-2">
                  <div className="flex items-center gap-3">
                    <label className="text-xs text-slate-400 font-medium">Confidence Level:</label>
                    <div className="flex bg-slate-900/80 rounded-lg p-1 border border-slate-800">
                      {["high", "medium", "low"].map((level) => (
                        <button
                          key={level}
                          onClick={() => handleAnswerChange(idx, "confidence", level)}
                          disabled={ans.is_outside_scope}
                          className={`px-3 py-1.5 rounded-md text-xs font-bold capitalize transition-all ${
                            ans.confidence === level && !ans.is_outside_scope
                              ? "bg-slate-800 text-white shadow-sm"
                              : "text-slate-500 hover:text-slate-300 disabled:opacity-30"
                          }`}
                        >
                          {level}
                        </button>
                      ))}
                    </div>
                  </div>

                  <label className="flex items-center gap-2 cursor-pointer group">
                    <div className={`w-10 h-5 rounded-full transition-colors relative ${ans.is_outside_scope ? "bg-amber-500" : "bg-slate-800"}`}>
                      <div className={`absolute top-1 w-3 h-3 rounded-full bg-white transition-all ${ans.is_outside_scope ? "left-6" : "left-1"}`}></div>
                    </div>
                    <span className={`text-xs font-bold transition-colors ${ans.is_outside_scope ? "text-amber-400" : "text-slate-500 group-hover:text-slate-300"}`}>
                      Outside Scope
                    </span>
                    <input 
                      type="checkbox" 
                      className="hidden"
                      checked={ans.is_outside_scope}
                      onChange={(e) => handleAnswerChange(idx, "is_outside_scope", e.target.checked)}
                    />
                  </label>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Sticky Bottom Bar */}
      <div className="fixed bottom-0 left-0 right-0 p-4 bg-slate-950/80 backdrop-blur-xl border-t border-slate-800/60 z-50">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <p className="text-sm text-slate-400">
            <span className="text-white font-bold">{Object.values(answers).filter(a => a.answer.trim() || a.is_outside_scope).length}</span> of {questions.length} answered
          </p>
          <button
            onClick={handleSubmit}
            className="px-6 py-3 bg-gradient-to-r from-indigo-500 to-indigo-600 text-white font-bold rounded-xl hover:from-indigo-400 hover:to-indigo-500 transition-all shadow-lg shadow-indigo-500/20 flex items-center gap-2"
          >
            Submit Answers to Compiler
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
