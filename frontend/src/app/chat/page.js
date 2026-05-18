'use client'
import { useState, useRef, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Sidebar from '../../components/layout/Sidebar'
import { getSupabaseClient, hasSupabaseConfig } from '../../lib/supabase'
import { ChatService } from '../../lib/api/services/ChatService'

const API = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'

export default function ChatPage() {
  const router = useRouter()
  const [messages, setMessages] = useState([])
  const [hasHydrated, setHasHydrated] = useState(false)
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [isOverride, setIsOverride] = useState(false)
  const [sessionId, setSessionId] = useState('demo-session')
  const [domain, setDomain] = useState('education')
  const [role, setRole] = useState('tutor')
  const bottomRef = useRef(null)
  const fileInputRef = useRef(null)

  const handleFileUpload = (e) => {
    const file = e.target.files[0]
    if (file) {
      setInput(prev => prev + (prev ? ' ' : '') + `[Document Attached: ${file.name}]`)
    }
  }

  const formatMarkdown = (text) => {
    if (!text) return null;
    const lines = text.split('\n');
    return lines.map((line, lineIndex) => {
      const parts = line.split(/(\*\*.*?\*\*)/g);
      return (
        <div key={lineIndex} style={{ minHeight: line.trim() === '' ? '0.8em' : 'auto' }}>
          {parts.map((part, index) => {
            if (part.startsWith('**') && part.endsWith('**')) {
              return <strong key={index}>{part.slice(2, -2)}</strong>;
            }
            return <span key={index}>{part}</span>;
          })}
        </div>
      );
    });
  };

  useEffect(() => {
    let sId = 'demo-session'
    let dom = 'education'
    let rol = 'tutor'
    
    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search)
      sId = params.get('session_id') || 'demo-session'
      dom = params.get('domain') || 'education'
      rol = params.get('role') || 'tutor'
      setSessionId(sId)
      setDomain(dom)
      setRole(rol)
    }

    async function initialFetch() {
      try {
        const data = await ChatService.getHistory(sId)
        if (data && data.messages && data.messages.length > 0) {
          setMessages(data.messages)
        } else {
          setMessages([
            {
              role: 'assistant',
              content: dom === 'healthcare'
                ? "Hello. I'm the Expert Digital Twin. I can answer questions grounded in verified professional decisions and clinical RAG protocols. How can I help you triage today?"
                : "Hello. I'm the Expert Digital Twin. I can answer questions grounded in verified professional decisions and documented protocols. How can I help you today?",
              confidence: 0.97,
              mode: 'primary',
              sources: [],
            }
          ])
        }
        if (data && data.status) {
          setIsOverride(data.status === 'human_intervention')
        }
      } catch (e) {
        console.error("Failed to fetch history", e)
      }
    }

    initialFetch()

    const interval = setInterval(async () => {
      try {
        const data = await ChatService.getHistory(sId)
        if (data && data.messages && data.messages.length > 0) {
          setMessages(data.messages)
        }
        if (data && data.status) {
          setIsOverride(data.status === 'human_intervention')
        }
      } catch (e) {
        console.error("Failed polling history:", e)
      }
    }, 2500)

    setHasHydrated(true)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function handleSignOut() {
    if (hasSupabaseConfig) {
      const supabase = getSupabaseClient()
      await supabase.auth.signOut()
    }

    router.push('/auth/signin')
  }

  async function sendMessage() {
    if (!input.trim() || loading) return
    const currentInput = input
    setInput('')
    setLoading(true)

    try {
      if (isOverride) {
        // Human Intervention Mode: Send expert message directly to the backend
        await ChatService.sendExpertMessage({
          expert_id: 'demo',
          message: currentInput,
          session_id: sessionId,
          domain: domain,
          role: role
        });
      } else {
        // Normal Twin Mode
        const data = await ChatService.sendMessage({ 
          expert_id: 'demo', 
          message: currentInput, 
          session_id: sessionId, 
          domain: domain, 
          role: role 
        });

        // Log trace to localStorage for the Glass Box page
        if (data.rationale) {
          const trace = {
            id: Math.random().toString(36).substr(2, 9),
            query: currentInput,
            rationale: data.rationale,
            response: data.response,
            sources: data.sources,
            confidence: data.confidence,
            latency: data.latency_ms,
            timestamp: new Date().toISOString()
          }
          const existing = JSON.parse(localStorage.getItem('glass_box_traces') || '[]')
          localStorage.setItem('glass_box_traces', JSON.stringify([trace, ...existing]))
        }
      } // end if (isOverride) else
      
      // Instantly refresh history to show sent messages immediately
      const res = await ChatService.getHistory(sessionId)
      if (res && res.messages) {
        setMessages(res.messages)
      }
    } catch {
      // If endpoint is offline, show fallback
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: '⚠ Chat endpoint offline or connection error.',
        confidence: null,
        mode: 'offline',
        sources: [],
      }])
    } finally {
      setLoading(false)
    }
  }


  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <Sidebar active="/chat" />

      <main style={{ flex: 1, display: 'flex', flexDirection: 'column', background: 'var(--bg-base)' }}>

        {/* Header */}
        <div style={{
          padding: '20px 28px',
          borderBottom: '1px solid var(--border)',
          background: '#FFFFFF',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          boxShadow: '0 1px 4px rgba(0,0,0,0.03)',
        }}>
          <div>
            <h1 style={{ fontSize: 18, fontWeight: 700, color: 'var(--text-primary)' }}>Twin Chat</h1>            <p style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 2, textTransform: 'capitalize' }}>
              Expert: Principal Specialist · Domain: {domain} ({role})
            </p>
          </div>
          <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginRight: '16px' }}>
              <span style={{ fontSize: '12px', fontWeight: 'bold', color: isOverride ? '#0D9488' : 'var(--text-secondary)' }}>
                {isOverride ? '🔴 ACTIVE OVERRIDE' : 'TWIN AUTOPILOT'}
              </span>
              <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
                <div style={{ position: 'relative' }}>
                  <input type="checkbox" className="sr-only" checked={isOverride} onChange={async (e) => {
                    const active = e.target.checked;
                    setIsOverride(active);
                    try {
                      await ChatService.setOverride({ session_id: sessionId, active });
                    } catch(err) { console.error("Override failed", err); }
                  }} style={{ display: 'none' }} />
                  <div style={{
                    width: '40px', height: '24px', backgroundColor: isOverride ? '#0D9488' : '#E5E7EB',
                    borderRadius: '9999px', transition: 'background-color 0.2s',
                    boxShadow: isOverride ? '0 0 10px #0D9488' : 'none'
                  }}></div>
                  <div style={{
                    position: 'absolute', top: '2px', left: isOverride ? '18px' : '2px',
                    width: '20px', height: '20px', backgroundColor: 'white',
                    borderRadius: '50%', transition: 'left 0.2s'
                  }}></div>
                </div>
              </label>
            </div>
            <button
              onClick={() => window.open(`/portal?session_id=${sessionId}&domain=${domain}&role=${role}`, '_blank')}
              style={{
                border: '1px solid #BFDBFE',
                background: '#EFF6FF',
                color: '#1E40AF',
                borderRadius: '999px',
                fontSize: 12,
                fontWeight: 700,
                padding: '8px 14px',
                cursor: 'pointer',
                marginRight: '8px',
                display: 'flex',
                alignItems: 'center',
                gap: '4px'
              }}
            >
              🌐 Open Patient Portal
            </button>
            <span className="badge badge-teal">RAG Active</span>
            <span className="badge badge-blue">HIPAA Mode</span>
            <button
              onClick={handleSignOut}
              style={{
                border: '1px solid var(--border)',
                background: '#FFFFFF',
                color: 'var(--text-secondary)',
                borderRadius: '999px',
                fontSize: 12,
                fontWeight: 700,
                padding: '8px 14px',
                cursor: 'pointer',
              }}
            >
              Sign Out
            </button>
          </div>
        </div>

        {/* Messages */}
        <div style={{ flex: 1, overflow: 'auto', padding: '24px 28px', display: 'flex', flexDirection: 'column', gap: 16 }}>
          {messages.map((msg, i) => (
            <div key={i} className="fade-up" style={{
              display: 'flex',
              flexDirection: msg.role === 'user' ? 'row-reverse' : 'row',
              gap: 12, alignItems: 'flex-start',
            }}>
              {/* Avatar */}
              <div style={{
                width: 38, height: 38, borderRadius: 'var(--radius-sm)', flexShrink: 0,
                background: msg.role === 'user' ? '#EFF6FF' : '#F0FDFA',
                border: `2px solid ${msg.role === 'user' ? '#BFDBFE' : '#99F6E4'}`,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: 16,
              }}>
                {msg.role === 'user' ? '👤' : '✨'}
              </div>

              {/* Bubble */}
              <div style={{ maxWidth: '68%' }}>
                {msg.intent_type === 'action' ? (
                  <div style={{
                    padding: '16px',
                    borderRadius: '8px',
                    background: msg.skill_status === 'DISABLED' ? '#FEF2F2' : (msg.skill_status === 'NOT_REGISTERED' ? '#FFFBEB' : '#F0FDFA'),
                    border: `1px solid ${msg.skill_status === 'DISABLED' ? '#FCA5A5' : (msg.skill_status === 'NOT_REGISTERED' ? '#FCD34D' : '#5EEAD4')}`,
                    color: 'var(--text-primary)',
                    fontSize: 14, lineHeight: 1.65,
                    boxShadow: 'var(--shadow-card)',
                    display: 'flex', flexDirection: 'column', gap: '12px'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontWeight: 600, color: msg.skill_status === 'DISABLED' ? '#B91C1C' : (msg.skill_status === 'NOT_REGISTERED' ? '#D97706' : '#0F766E') }}>
                        {msg.skill_status === 'DISABLED' ? '🚫 ACTION RESTRICTED' : (msg.skill_status === 'NOT_REGISTERED' ? '🔧 ACTION NOT AVAILABLE' : '⚡ ACTION EXECUTED')}
                      </span>
                      <span className={`badge ${msg.skill_status === 'DISABLED' ? 'badge-red' : (msg.skill_status === 'NOT_REGISTERED' ? 'badge-amber' : 'badge-green')}`}>
                        {msg.skill_status}
                      </span>
                    </div>

                    <div style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
                      <strong>Skill:</strong> {msg.detected_skill}<br />
                      {msg.extracted_params && Object.keys(msg.extracted_params).length > 0 && (
                        <><strong>Params:</strong> {JSON.stringify(msg.extracted_params)}<br /></>
                      )}
                    </div>

                    <div style={{
                      paddingTop: '12px',
                      borderTop: `1px solid ${msg.skill_status === 'DISABLED' ? '#FECACA' : (msg.skill_status === 'NOT_REGISTERED' ? '#FDE68A' : '#99F6E4')}`,
                      whiteSpace: 'pre-wrap'
                    }}>
                      {formatMarkdown(msg.content)}
                    </div>
                  </div>
                ) : (
                  <div style={{
                    padding: '14px 18px',
                    borderRadius: msg.role === 'user' ? '18px 4px 18px 18px' : '4px 18px 18px 18px',
                    background: msg.role === 'user' ? 'linear-gradient(135deg, #0D9488, #14B8A6)' : '#FFFFFF',
                    border: msg.role === 'user' ? 'none' : '1px solid var(--border)',
                    color: msg.role === 'user' ? '#FFFFFF' : 'var(--text-primary)',
                    fontSize: 14, lineHeight: 1.65,
                    boxShadow: msg.role === 'user' ? '0 4px 12px rgba(13,148,136,0.2)' : 'var(--shadow-card)',
                    whiteSpace: 'pre-wrap'
                  }}>
                    {formatMarkdown(msg.content)}
                  </div>
                )}

                {/* Metadata for assistant messages */}
                {msg.role === 'assistant' && msg.confidence !== null && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 12, marginTop: 12 }}>
                    <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                      {msg.confidence !== undefined && (
                        <span className={`badge ${msg.confidence >= 0.7 ? 'badge-green' : 'badge-amber'}`}>
                          {msg.confidence !== null ? `${Math.round(msg.confidence * 100)}% confidence` : '—'}
                        </span>
                      )}
                      {msg.mode && (
                        <span className={`badge ${msg.mode === 'primary' ? 'badge-teal' : 'badge-amber'}`}>
                          {msg.mode === 'primary' ? '✨ Expert Voice' : '◎ Deputy Mode'}
                        </span>
                      )}
                      {msg.sources?.length > 0 && (
                        <span className="badge badge-blue">{msg.sources.length} sources</span>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
              <div style={{
                width: 38, height: 38, borderRadius: 'var(--radius-sm)',
                background: '#F0FDFA', border: '2px solid #99F6E4',
                display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 16,
              }}>✨</div>
              <div style={{
                padding: '14px 22px', borderRadius: '4px 18px 18px 18px',
                background: '#FFFFFF', border: '1px solid var(--border)',
                display: 'flex', gap: 5, alignItems: 'center',
                boxShadow: 'var(--shadow-card)',
              }}>
                {[0, 1, 2].map(d => (
                  <span key={d} style={{
                    width: 8, height: 8, borderRadius: '50%',
                    background: 'var(--accent-primary)',
                    animation: `blink 1.2s ease ${d * 0.2}s infinite`,
                    display: 'inline-block',
                  }} />
                ))}
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Input */}
        {isOverride && (
          <div style={{ padding: '8px 28px', background: '#F0FDFA', borderTop: '1px solid #99F6E4', fontSize: '12px', color: '#0F766E', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div className="spinner" style={{ width: '12px', height: '12px', borderTopColor: '#0F766E' }}></div>
            Twin is actively listening and extracting logic from your manual intervention...
          </div>
        )}
        <div style={{
          padding: '16px 28px',
          borderTop: '1px solid var(--border)',
          background: isOverride ? '#F8FAFC' : '#FFFFFF',
          transition: 'background-color 0.2s'
        }}>
          <div style={{ display: 'flex', gap: 10 }}>
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileUpload}
              style={{ display: 'none' }}
              accept=".pdf,.doc,.docx,.png,.jpg,.jpeg"
            />
            <button
              onClick={() => fileInputRef.current?.click()}
              style={{
                padding: '0 12px',
                background: '#F9FAFB',
                border: '1px solid var(--border)',
                borderRadius: 'var(--radius-md)',
                cursor: 'pointer',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: 20
              }}
              title="Upload Document"
            >
              📎
            </button>
            <input
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && !e.shiftKey && sendMessage()}
              placeholder={isOverride ? "Direct message to user (Bypassing Twin)..." : "Ask the Expert Twin a professional question..."}
              style={{
                flex: 1, padding: '13px 18px',
                background: isOverride ? '#FFFFFF' : 'var(--bg-elevated)',
                border: isOverride ? '2px solid #0D9488' : '1px solid var(--border)',
                borderRadius: 'var(--radius-md)',
                color: 'var(--text-primary)',
                fontSize: 14, outline: 'none',
                transition: 'border-color 0.2s',
              }}
            />
            <button
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              style={{
                padding: '13px 24px',
                background: loading ? 'var(--bg-elevated)' : 'linear-gradient(135deg, #0D9488, #14B8A6)',
                color: loading ? 'var(--text-secondary)' : 'white',
                border: 'none',
                borderRadius: 'var(--radius-md)',
                fontWeight: 600, fontSize: 14,
                cursor: loading ? 'not-allowed' : 'pointer',
                transition: 'all 0.2s',
                boxShadow: loading ? 'none' : '0 4px 12px rgba(13,148,136,0.25)',
              }}
            >
              {loading ? '...' : 'Send'}
            </button>
          </div>
          <p style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 8 }}>
            Responses are grounded in verified Master Cases. Secure & Confidential. Not a substitute for primary consultation.
          </p>
        </div>
      </main>
    </div>
  )
}
