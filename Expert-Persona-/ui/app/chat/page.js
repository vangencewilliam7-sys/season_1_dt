"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Brain, User, AlertTriangle, ChevronDown, Shield, Zap, RotateCcw } from "lucide-react";

const ALEX_PERSONA = {
  expert_id: "demo-alex-001",
  identity: { name: "Alex Rivet", role: "Principal Solutions Architect", domain: "tech_consulting" },
  communication_style: { tone: ["direct", "pragmatic", "skeptical of hype"], verbosity: "concise", preferred_framing: "Risk-first evaluation" },
  heuristics: [
    { trigger: "When a performance bottleneck exists in a legacy DB during a time-sensitive period", decision: "Use Redis caching/buffering instead of a DB migration", reasoning: "Stability is more important than the 'perfect' DB when deadlines are short" },
    { trigger: "When presented with a legacy migration request", decision: "Force decomposition of the monolith into serverless/modern components", reasoning: "Migration is the ONLY time you have political leverage to fix architectural debt" },
  ],
  drop_zone_triggers: ["Mobile UX design", "Legacy Mainframe COBOL", "Frontend performance tuning", "Mobile application design", "Frontend Frameworks"],
  confidence_threshold: 0.7,
  fallback_identity: { role: "Consulting Associate", tone: "helpful, analytical", action: "State that this needs a Principal Architect's review" },
};

const SARAH_PERSONA = {
  expert_id: "demo-sarah-001",
  identity: { name: "Sarah Chen", role: "Senior Technical Recruiter", domain: "recruiting" },
  communication_style: { tone: ["empathetic", "structured", "professional"], verbosity: "detailed", preferred_framing: "Evidence-first evaluation" },
  heuristics: [
    { trigger: "When a candidate has strong technical skills but poor communication", decision: "Proceed to next round with a specific note on communication", reasoning: "Technical depth is harder to find than communication training" },
  ],
  drop_zone_triggers: ["Medical diagnosis", "Legal compliance advice", "Financial investment", "System architecture"],
  confidence_threshold: 0.8,
  fallback_identity: { role: "Recruiting Coordinator", tone: "neutral, process-oriented", action: "Acknowledge the gap and route to the senior recruiter" },
};

const PERSONAS = [ALEX_PERSONA, SARAH_PERSONA];

const QUICK_PROMPTS = {
  "demo-alex-001": [
    "Our database is slow during peak hours. Should we migrate to NoSQL?",
    "How should I approach a legacy monolith migration?",
    "Help me optimize React component rendering",
  ],
  "demo-sarah-001": [
    "How do you evaluate a candidate with strong Python skills but poor communication?",
    "What medication should I prescribe for chest pain?",
    "How should I design system architecture for a new platform?",
  ],
};

function checkDropZones(message, persona) {
  const msg = message.toLowerCase();
  const dropZones = persona.drop_zone_triggers || [];
  for (const trigger of dropZones) {
    const triggerLower = trigger.toLowerCase();
    if (msg.includes(triggerLower)) {
      return { escalated: true, reason: `Query matches drop zone: '${trigger}'` };
    }
    const words = triggerLower.split(" ").filter(w => w.length > 3);
    if (words.length > 0) {
      const matches = words.filter(w => msg.includes(w)).length;
      if (matches >= words.length * 0.7) {
        return { escalated: true, reason: `Query matches drop zone: '${trigger}'` };
      }
    }
  }
  return { escalated: false, reason: "" };
}

function generateResponse(message, persona, routeResult) {
  const identity = persona.identity;
  if (routeResult.escalated) {
    return {
      text: `I appreciate the question, but this falls outside my area of expertise. ${routeResult.reason}. As ${identity.name}, I focus specifically on ${identity.domain}. I'd recommend reaching out to a ${persona.fallback_identity.role} who can help you with this.`,
      route: "escalate",
    };
  }
  // Match heuristics
  const msgLower = message.toLowerCase();
  for (const h of persona.heuristics) {
    const triggerWords = h.trigger.toLowerCase().split(" ").filter(w => w.length > 3);
    const matches = triggerWords.filter(w => msgLower.includes(w)).length;
    if (matches >= triggerWords.length * 0.3) {
      return {
        text: `Based on my experience: ${h.decision}. Here's why — ${h.reasoning}. When ${h.trigger.toLowerCase()}, the worst thing you can do is chase complexity. Keep it simple, keep it stable.`,
        route: "respond",
      };
    }
  }
  return {
    text: `As ${identity.name}, a ${identity.role} with a ${persona.communication_style.preferred_framing.toLowerCase()} approach — I'd need more context about your specific situation. What are the constraints? Timeline? Team size? I don't give generic advice — give me the real scenario.`,
    route: "respond",
  };
}

export default function ChatPage() {
  const [activePersona, setActivePersona] = useState(PERSONAS[0]);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [showPersonaPanel, setShowPersonaPanel] = useState(false);
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = (text) => {
    const msg = text || input.trim();
    if (!msg) return;

    const userMsg = { role: "user", content: msg, timestamp: Date.now() };
    const routeResult = checkDropZones(msg, activePersona);
    const response = generateResponse(msg, activePersona, routeResult);
    const assistantMsg = {
      role: "assistant",
      content: response.text,
      route: response.route,
      escalated: routeResult.escalated,
      reason: routeResult.reason,
      timestamp: Date.now() + 1,
    };

    setMessages((prev) => [...prev, userMsg, assistantMsg]);
    setInput("");
  };

  const resetChat = () => {
    setMessages([]);
  };

  const switchPersona = (p) => {
    setActivePersona(p);
    setMessages([]);
    setShowPersonaPanel(false);
  };

  const identity = activePersona.identity;

  return (
    <div className="flex h-screen">
      {/* Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Chat Header */}
        <div className="border-b border-slate-800/60 bg-slate-950/60 backdrop-blur-sm px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-sky-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <Brain className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-white">{identity.name}</h2>
              <p className="text-[11px] text-slate-500">{identity.role} &bull; {identity.domain}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={resetChat}
              className="p-2.5 text-slate-500 hover:text-white hover:bg-slate-800 rounded-lg transition-all"
              title="Reset chat"
            >
              <RotateCcw className="w-4 h-4" />
            </button>
            <button
              onClick={() => setShowPersonaPanel(!showPersonaPanel)}
              className="px-3 py-2 border border-slate-800 rounded-lg text-xs font-semibold text-slate-400 hover:text-white hover:border-slate-700 transition-all flex items-center gap-1.5"
            >
              Switch Persona
              <ChevronDown className="w-3 h-3" />
            </button>
          </div>
        </div>

        {/* Persona Switcher Dropdown */}
        {showPersonaPanel && (
          <div className="absolute top-16 right-8 z-50 w-80 glass-card p-3 border border-slate-700 shadow-2xl mt-16 mr-4" style={{right: '16px', top: '64px', position: 'fixed'}}>
            {PERSONAS.map((p) => (
              <button
                key={p.expert_id}
                onClick={() => switchPersona(p)}
                className={`w-full text-left p-3 rounded-xl mb-1 transition-all ${
                  activePersona.expert_id === p.expert_id
                    ? "bg-indigo-500/10 border border-indigo-500/20"
                    : "hover:bg-slate-800/50"
                }`}
              >
                <p className="text-sm font-bold text-white">{p.identity.name}</p>
                <p className="text-[11px] text-slate-500">{p.identity.role}</p>
              </button>
            ))}
          </div>
        )}

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-indigo-500/20 to-sky-500/20 border border-indigo-500/20 flex items-center justify-center mb-4">
                <Brain className="w-7 h-7 text-indigo-400" />
              </div>
              <h3 className="text-xl font-bold text-white font-[family-name:var(--font-outfit)] mb-2">
                Test {identity.name}&apos;s Persona
              </h3>
              <p className="text-sm text-slate-500 max-w-md mb-6">
                Send a message to see how the conversation graph routes it through
                the persona&apos;s drop zones and heuristics.
              </p>
              <div className="space-y-2 w-full max-w-lg">
                <p className="text-[10px] text-slate-600 uppercase font-bold tracking-wider">Try these:</p>
                {(QUICK_PROMPTS[activePersona.expert_id] || []).map((prompt, i) => (
                  <button
                    key={i}
                    onClick={() => sendMessage(prompt)}
                    className="w-full text-left px-4 py-3 rounded-xl border border-slate-800/60 text-sm text-slate-400 hover:text-white hover:bg-slate-800/30 hover:border-slate-700 transition-all"
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((msg, i) => (
            <div key={i} className={`flex gap-3 slide-up ${msg.role === "user" ? "justify-end" : ""}`}>
              {msg.role === "assistant" && (
                <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 mt-0.5 ${
                  msg.escalated
                    ? "bg-amber-500/20 border border-amber-500/20"
                    : "bg-indigo-500/20 border border-indigo-500/20"
                }`}>
                  {msg.escalated ? (
                    <AlertTriangle className="w-4 h-4 text-amber-400" />
                  ) : (
                    <Brain className="w-4 h-4 text-indigo-400" />
                  )}
                </div>
              )}
              <div className={`max-w-lg ${msg.role === "user" ? "text-right" : ""}`}>
                {/* Route badge for assistant */}
                {msg.role === "assistant" && (
                  <div className="flex items-center gap-2 mb-1.5">
                    <span className={`status-badge ${
                      msg.escalated
                        ? "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                        : "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                    }`}>
                      {msg.escalated ? (
                        <span className="flex items-center gap-1"><Shield className="w-2.5 h-2.5" /> Escalated</span>
                      ) : (
                        <span className="flex items-center gap-1"><Zap className="w-2.5 h-2.5" /> In-Scope</span>
                      )}
                    </span>
                    {msg.reason && (
                      <span className="text-[10px] text-slate-600">{msg.reason}</span>
                    )}
                  </div>
                )}
                <div className={`px-4 py-3 rounded-2xl text-sm leading-relaxed ${
                  msg.role === "user"
                    ? "bg-indigo-500 text-white rounded-br-md"
                    : msg.escalated
                      ? "bg-amber-500/5 border border-amber-500/10 text-slate-300 rounded-bl-md"
                      : "bg-slate-800/60 text-slate-300 rounded-bl-md"
                }`}>
                  {msg.content}
                </div>
              </div>
              {msg.role === "user" && (
                <div className="w-8 h-8 rounded-lg bg-slate-800 flex items-center justify-center shrink-0 mt-0.5">
                  <User className="w-4 h-4 text-slate-400" />
                </div>
              )}
            </div>
          ))}
          <div ref={chatEndRef} />
        </div>

        {/* Input Bar */}
        <div className="border-t border-slate-800/60 bg-slate-950/60 backdrop-blur-sm p-4">
          <div className="flex gap-3 max-w-4xl mx-auto">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendMessage()}
              placeholder={`Ask ${identity.name} something...`}
              className="flex-1 bg-slate-900/60 border border-slate-800 rounded-xl px-4 py-3 text-sm text-white placeholder:text-slate-600 focus:outline-none focus:border-indigo-500/50 transition-colors"
            />
            <button
              onClick={() => sendMessage()}
              disabled={!input.trim()}
              className="px-5 py-3 bg-gradient-to-r from-indigo-500 to-indigo-600 text-white font-bold rounded-xl hover:from-indigo-400 hover:to-indigo-500 transition-all shadow-lg shadow-indigo-500/20 flex items-center gap-2 text-sm disabled:opacity-30 disabled:cursor-not-allowed"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
