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

      <main style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>

        {/* Header */}
        <div style={{
          padding: '20px 28px',
          borderBottom: '1px solid var(--border)',
          background: 'var(--bg-surface)',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        }}>
          <div>
            <h1 style={{ fontSize: 18, fontWeight: 700 }}>Twin Chat</h1>
            <p style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 2 }}>
              Expert: Fertility Specialist · Domain: Healthcare
            </p>
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            <span className="badge badge-blue">RAG Active</span>
            <span className="badge badge-teal">HIPAA Mode</span>
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
                width: 34, height: 34, borderRadius: '50%', flexShrink: 0,
                background: msg.role === 'user' ? 'var(--accent-glow)' : '#14b8a615',
                border: `1px solid ${msg.role === 'user' ? 'var(--accent-primary)' : 'var(--accent-teal)'}30`,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: 14,
              }}>
                {msg.role === 'user' ? '◈' : '⚕'}
              </div>

              {/* Bubble */}
              <div style={{ maxWidth: '68%' }}>
                <div style={{
                  padding: '12px 16px',
                  borderRadius: msg.role === 'user' ? '16px 4px 16px 16px' : '4px 16px 16px 16px',
                  background: msg.role === 'user' ? 'var(--accent-glow)' : 'var(--bg-card)',
                  border: `1px solid ${msg.role === 'user' ? 'var(--accent-primary)' : 'var(--border)'}30`,
                  fontSize: 14, lineHeight: 1.65,
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
                width: 34, height: 34, borderRadius: '50%',
                background: '#14b8a615', border: '1px solid var(--accent-teal)30',
                display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 14,
              }}>⚕</div>
              <div style={{
                padding: '12px 20px', borderRadius: '4px 16px 16px 16px',
                background: 'var(--bg-card)', border: '1px solid var(--border)',
                display: 'flex', gap: 4, alignItems: 'center',
              }}>
                {[0,1,2].map(d => (
                  <span key={d} style={{
                    width: 7, height: 7, borderRadius: '50%',
                    background: 'var(--accent-teal)',
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
          background: 'var(--bg-surface)',
        }}>
          <div style={{ display: 'flex', gap: 10 }}>
            <input
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && !e.shiftKey && sendMessage()}
              placeholder="Ask the Doctor Twin a clinical question..."
              style={{
                flex: 1, padding: '12px 16px',
                background: 'var(--bg-card)',
                border: '1px solid var(--border)',
                borderRadius: 'var(--radius-md)',
                color: 'var(--text-primary)',
                fontSize: 14, outline: 'none',
              }}
            />
            <button
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              style={{
                padding: '12px 22px',
                background: loading ? 'var(--bg-elevated)' : 'var(--accent-primary)',
                color: 'white',
                border: 'none',
                borderRadius: 'var(--radius-md)',
                fontWeight: 600, fontSize: 13,
                cursor: loading ? 'not-allowed' : 'pointer',
                transition: 'all 0.2s',
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
