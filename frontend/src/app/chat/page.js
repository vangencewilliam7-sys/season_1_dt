'use client'
import { useState, useRef, useEffect } from 'react'
import Sidebar from '../../components/layout/Sidebar'

const API = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000'

export default function ChatPage() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: "Hello. I'm Dr. [Expert]'s Digital Twin. I can answer questions grounded in verified clinical decisions and documented protocols. How can I help you today?",
      confidence: 0.97,
      mode: 'primary',
      sources: [],
    }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function sendMessage() {
    if (!input.trim() || loading) return
    const userMsg = { role: 'user', content: input }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setLoading(true)

    try {
      const res = await fetch(`${API}/api/chat/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ expert_id: 'demo', message: input, session_id: 'demo-session' }),
      })
      const data = await res.json()
      const assistantMessage = {
        role: 'assistant',
        content: data.response || 'No response received.',
        confidence: data.confidence,
        mode: data.persona_mode,
        sources: data.sources || [],
        rationale: data.rationale,
      }
      setMessages(prev => [...prev, assistantMessage])

      // Log trace to localStorage for the Glass Box page
      if (data.rationale) {
        const trace = {
          id: Math.random().toString(36).substr(2, 9),
          query: input,
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
    } catch {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: '⚠ Chat endpoint not yet connected. Build Phase 5 to enable this.',
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
            <h1 style={{ fontSize: 18, fontWeight: 700, color: 'var(--text-primary)' }}>Twin Chat</h1>
            <p style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 2 }}>
              Expert: Fertility Specialist · Domain: Healthcare
            </p>
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            <span className="badge badge-teal">RAG Active</span>
            <span className="badge badge-blue">HIPAA Mode</span>
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
                {msg.role === 'user' ? '👤' : '⚕️'}
              </div>

              {/* Bubble */}
              <div style={{ maxWidth: '68%' }}>
                <div style={{
                  padding: '14px 18px',
                  borderRadius: msg.role === 'user' ? '18px 4px 18px 18px' : '4px 18px 18px 18px',
                  background: msg.role === 'user' ? 'linear-gradient(135deg, #0D9488, #14B8A6)' : '#FFFFFF',
                  border: msg.role === 'user' ? 'none' : '1px solid var(--border)',
                  color: msg.role === 'user' ? '#FFFFFF' : 'var(--text-primary)',
                  fontSize: 14, lineHeight: 1.65,
                  boxShadow: msg.role === 'user' ? '0 4px 12px rgba(13,148,136,0.2)' : 'var(--shadow-card)',
                }}>
                  {msg.content}
                </div>

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
                          {msg.mode === 'primary' ? '⚕ Expert Voice' : '◎ Deputy Mode'}
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
              }}>⚕️</div>
              <div style={{
                padding: '14px 22px', borderRadius: '4px 18px 18px 18px',
                background: '#FFFFFF', border: '1px solid var(--border)',
                display: 'flex', gap: 5, alignItems: 'center',
                boxShadow: 'var(--shadow-card)',
              }}>
                {[0,1,2].map(d => (
                  <span key={d} style={{
                    width: 8, height: 8, borderRadius: '50%',
                    background: 'var(--accent-primary)',
                    animation: `blink 1.2s ease ${d * 0.2}s infinite`,
                    display: 'inline-block',
                  }}/>
                ))}
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <div style={{
          padding: '16px 28px',
          borderTop: '1px solid var(--border)',
          background: '#FFFFFF',
        }}>
          <div style={{ display: 'flex', gap: 10 }}>
            <input
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && !e.shiftKey && sendMessage()}
              placeholder="Ask the Doctor Twin a clinical question..."
              style={{
                flex: 1, padding: '13px 18px',
                background: 'var(--bg-elevated)',
                border: '1px solid var(--border)',
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
            Responses are grounded in verified Master Cases. HIPAA-compliant. Not a substitute for clinical consultation.
          </p>
        </div>
      </main>
    </div>
  )
}
