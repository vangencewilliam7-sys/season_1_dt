'use client'
import { useState, useRef, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { ChatService } from '../../lib/api/services/ChatService'

export default function ClientPortal() {
  const router = useRouter()
  const [sessionId, setSessionId] = useState('demo-session')
  const [domain, setDomain] = useState('education')
  const [role, setRole] = useState('tutor')

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
          // Set welcome message dynamically
          const welcome = dom === 'healthcare'
            ? "Hello! I am your AI Health Twin. I've initialized your patient profile and am ready to support your clinical triage screening. How are you feeling today?"
            : "Hello! I am your AI assistant. I'm here to help you manage your tasks and answer your questions."
          setMessages([
            {
              role: 'assistant',
              content: welcome,
              sender: 'twin'
            }
          ])
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
      } catch (e) {
        console.error("Failed polling history:", e)
      }
    }, 2500)

    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function sendMessage() {
    if (!input.trim() || loading) return
    const currentInput = input
    setInput('')
    setLoading(true)

    try {
      await ChatService.sendMessage({ 
        expert_id: 'demo', 
        message: currentInput, 
        session_id: sessionId, 
        domain: domain, 
        role: role 
      });
      const data = await ChatService.getHistory(sessionId)
      if (data && data.messages) {
        setMessages(data.messages)
      }
    } catch {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: '⚠ Connection Error.',
        sender: 'twin'
      }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: '#F8FAFC' }}>
      
      {/* Left Sidebar - Client Cockpit */}
      <div style={{ width: '320px', background: '#FFFFFF', borderRight: '1px solid #E2E8F0', display: 'flex', flexDirection: 'column' }}>
        <div style={{ padding: '24px', borderBottom: '1px solid #E2E8F0' }}>
          <h2 style={{ fontSize: '20px', fontWeight: 'bold', color: '#1E293B', marginBottom: '4px' }}>My Dashboard</h2>
          <p style={{ fontSize: '14px', color: '#64748B', textTransform: 'capitalize' }}>{domain} Domain ({role})</p>
        </div>
        
        <div style={{ padding: '24px', flex: 1, overflowY: 'auto' }}>
          {domain === 'healthcare' ? (
            <>
              {/* Healthcare Domain Stats */}
              <div style={{ background: '#FEF2F2', borderRadius: '12px', padding: '20px', marginBottom: '24px', border: '1px solid #FCA5A5' }}>
                <h3 style={{ fontSize: '14px', fontWeight: 'bold', color: '#991B1B', marginBottom: '16px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Vitals & Triage</h3>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                  <span style={{ color: '#EF4444', fontSize: '14px' }}>Patient State</span>
                  <span style={{ fontWeight: 'bold', color: '#991B1B' }}>Initialized</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: '#EF4444', fontSize: '14px' }}>Triage Level</span>
                  <span style={{ fontWeight: 'bold', color: '#10B981', background: '#D1FAE5', padding: '2px 8px', borderRadius: '4px', fontSize: '12px' }}>GREEN_ZONE</span>
                </div>
              </div>

              <div style={{ background: '#F0FDF4', borderRadius: '12px', padding: '20px', border: '1px solid #BBF7D0' }}>
                <h3 style={{ fontSize: '14px', fontWeight: 'bold', color: '#14532D', marginBottom: '16px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Screening Tasks</h3>
                <ul style={{ margin: 0, paddingLeft: '16px', color: '#166534', fontSize: '14px', lineHeight: '1.6' }}>
                  <li>Telemedicine Onboarding</li>
                  <li>Symptomatic BP Proxy</li>
                  <li>Perform Neck Check</li>
                </ul>
              </div>
            </>
          ) : domain === 'it' ? (
            <>
              {/* IT Domain Stats */}
              <div style={{ background: '#F5F3FF', borderRadius: '12px', padding: '20px', marginBottom: '24px', border: '1px solid #DDD6FE' }}>
                <h3 style={{ fontSize: '14px', fontWeight: 'bold', color: '#5B21B6', marginBottom: '16px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Sprint Analytics</h3>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                  <span style={{ color: '#8B5CF6', fontSize: '14px' }}>Sprint Tasks</span>
                  <span style={{ fontWeight: 'bold', color: '#5B21B6' }}>12/15</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: '#8B5CF6', fontSize: '14px' }}>Velocity</span>
                  <span style={{ fontWeight: 'bold', color: '#5B21B6' }}>85%</span>
                </div>
              </div>

              <div style={{ background: '#F0FDF4', borderRadius: '12px', padding: '20px', border: '1px solid #BBF7D0' }}>
                <h3 style={{ fontSize: '14px', fontWeight: 'bold', color: '#14532D', marginBottom: '16px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Next Steps</h3>
                <ul style={{ margin: 0, paddingLeft: '16px', color: '#166534', fontSize: '14px', lineHeight: '1.6' }}>
                  <li>Audit Divergence Logs</li>
                  <li>Manifest Production Persona</li>
                </ul>
              </div>
            </>
          ) : (
            <>
              {/* Education Domain Stats (Default) */}
              <div style={{ background: '#EFF6FF', borderRadius: '12px', padding: '20px', marginBottom: '24px', border: '1px solid #BFDBFE' }}>
                <h3 style={{ fontSize: '14px', fontWeight: 'bold', color: '#1E3A8A', marginBottom: '16px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Progress Stats</h3>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                  <span style={{ color: '#3B82F6', fontSize: '14px' }}>Assignments</span>
                  <span style={{ fontWeight: 'bold', color: '#1E3A8A' }}>8/10</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: '#3B82F6', fontSize: '14px' }}>Curiosity Score</span>
                  <span style={{ fontWeight: 'bold', color: '#1E3A8A' }}>92%</span>
                </div>
              </div>

              <div style={{ background: '#F0FDF4', borderRadius: '12px', padding: '20px', border: '1px solid #BBF7D0' }}>
                <h3 style={{ fontSize: '14px', fontWeight: 'bold', color: '#14532D', marginBottom: '16px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Next Steps</h3>
                <ul style={{ margin: 0, paddingLeft: '16px', color: '#166534', fontSize: '14px', lineHeight: '1.6' }}>
                  <li>Review Chapter 4</li>
                  <li>Complete Quiz 2</li>
                </ul>
              </div>
            </>
          )}
        </div>
        
        <div style={{ padding: '24px', borderTop: '1px solid #E2E8F0' }}>
           <button onClick={() => router.push(`/chat?session_id=${sessionId}&domain=${domain}&role=${role}`)} style={{ width: '100%', padding: '12px', background: '#FFFFFF', border: '1px solid #E2E8F0', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold', color: '#64748B' }}>
             Switch to Expert View
           </button>
        </div>
      </div>

      {/* Main Chat Area */}
      <main style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {/* Header */}
        <div style={{
          padding: '20px 32px',
          background: '#FFFFFF',
          borderBottom: '1px solid #E2E8F0',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          boxShadow: '0 1px 2px rgba(0,0,0,0.02)'
        }}>
          <div>
            <h1 style={{ fontSize: '24px', fontWeight: 700, color: '#0F172A' }}>Support Chat</h1>
          </div>
        </div>

        {/* Messages */}
        <div style={{ flex: 1, overflow: 'auto', padding: '32px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
          {messages.map((msg, i) => (
            <div key={i} style={{
              display: 'flex',
              flexDirection: msg.role === 'user' ? 'row-reverse' : 'row',
              gap: '16px', alignItems: 'flex-start',
            }}>
              {/* Avatar */}
              <div style={{
                width: '44px', height: '44px', borderRadius: '50%', flexShrink: 0,
                background: msg.role === 'user' ? '#3B82F6' : (msg.sender === 'human_expert' ? '#10B981' : '#6366F1'),
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                color: 'white', fontSize: '20px', fontWeight: 'bold',
                boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
              }}>
                {msg.role === 'user' ? 'U' : (msg.sender === 'human_expert' ? '👨‍🏫' : '🤖')}
              </div>

              {/* Bubble */}
              <div style={{ maxWidth: '75%' }}>
                {msg.role === 'assistant' && (
                  <div style={{ fontSize: '12px', color: '#64748B', marginBottom: '4px', paddingLeft: '4px' }}>
                    {msg.sender === 'human_expert' ? 'Expert Tutor' : 'AI Assistant'}
                  </div>
                )}
                <div style={{
                  padding: '16px 20px',
                  borderRadius: msg.role === 'user' ? '20px 4px 20px 20px' : '4px 20px 20px 20px',
                  background: msg.role === 'user' ? '#3B82F6' : '#FFFFFF',
                  color: msg.role === 'user' ? '#FFFFFF' : '#1E293B',
                  fontSize: '15px', lineHeight: '1.6',
                  boxShadow: msg.role === 'user' ? '0 4px 6px rgba(59,130,246,0.2)' : '0 1px 3px rgba(0,0,0,0.05)',
                  border: msg.role === 'user' ? 'none' : '1px solid #E2E8F0',
                  whiteSpace: 'pre-wrap'
                }}>
                  {msg.content}
                </div>
              </div>
            </div>
          ))}

          {loading && (
            <div style={{ display: 'flex', gap: '16px', alignItems: 'flex-start' }}>
               <div style={{
                width: '44px', height: '44px', borderRadius: '50%', flexShrink: 0,
                background: '#6366F1', display: 'flex', alignItems: 'center', justifyContent: 'center',
                color: 'white', fontSize: '20px', fontWeight: 'bold'
              }}>🤖</div>
              <div style={{ padding: '16px 20px', borderRadius: '4px 20px 20px 20px', background: '#FFFFFF', border: '1px solid #E2E8F0', display: 'flex', gap: '6px', alignItems: 'center' }}>
                <span style={{ width: '8px', height: '8px', background: '#94A3B8', borderRadius: '50%', animation: 'blink 1s infinite' }}></span>
                <span style={{ width: '8px', height: '8px', background: '#94A3B8', borderRadius: '50%', animation: 'blink 1s infinite 0.2s' }}></span>
                <span style={{ width: '8px', height: '8px', background: '#94A3B8', borderRadius: '50%', animation: 'blink 1s infinite 0.4s' }}></span>
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Input area */}
        <div style={{ padding: '24px 32px', background: '#FFFFFF', borderTop: '1px solid #E2E8F0' }}>
          <div style={{ display: 'flex', gap: '12px' }}>
            <input
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && !e.shiftKey && sendMessage()}
              placeholder="Type your message..."
              style={{
                flex: 1, padding: '16px 20px',
                background: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: '12px',
                color: '#1E293B', fontSize: '15px', outline: 'none',
                transition: 'border-color 0.2s'
              }}
            />
            <button
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              style={{
                padding: '0 28px',
                background: loading ? '#E2E8F0' : '#3B82F6',
                color: loading ? '#94A3B8' : '#FFFFFF',
                border: 'none', borderRadius: '12px',
                fontWeight: 'bold', fontSize: '15px',
                cursor: loading ? 'not-allowed' : 'pointer',
                transition: 'background-color 0.2s'
              }}
            >
              Send
            </button>
          </div>
        </div>
      </main>
    </div>
  )
}
