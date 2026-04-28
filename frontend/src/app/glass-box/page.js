'use client'
import { useState, useEffect } from 'react'
import Sidebar from '../../components/layout/Sidebar'

export default function GlassBoxPage() {
  const [traces, setTraces] = useState([])

  useEffect(() => {
    const savedTraces = JSON.parse(localStorage.getItem('glass_box_traces') || '[]')
    setTraces(savedTraces)
  }, [])

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: 'var(--bg-base)' }}>
      <Sidebar active="/glass-box" />

      <main style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        
        {/* Header */}
        <div style={{
          padding: '24px 32px',
          borderBottom: '1px solid var(--border)',
          background: 'var(--bg-surface)',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        }}>
          <div>
            <h1 style={{ fontSize: 22, fontWeight: 700, display: 'flex', alignItems: 'center', gap: 10 }}>
              <span style={{ fontSize: 20 }}>🔍</span> Glass Box Execution Trace
            </h1>
            <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginTop: 4 }}>
              Transparent node-by-node audit log of the Digital Twin's clinical reasoning.
            </p>
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            <span className="badge badge-teal">Node Tracer Active</span>
            <span className="badge badge-purple">{traces.length} Sessions Logged</span>
          </div>
        </div>

        {/* Content */}
        <div style={{ flex: 1, overflow: 'auto', padding: '32px' }}>
          {traces.length === 0 ? (
            <div style={{
              textAlign: 'center', padding: '60px 20px',
              border: '1px dashed var(--border)', borderRadius: 'var(--radius-lg)',
              color: 'var(--text-secondary)'
            }}>
              <div style={{ fontSize: 40, opacity: 0.5, marginBottom: 16 }}>🕸️</div>
              <h3 style={{ fontSize: 16, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 8 }}>No Traces Yet</h3>
              <p style={{ fontSize: 13 }}>Go to Twin Chat and ask a question to generate a nodal reasoning trace.</p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
              {traces.map((trace) => (
                <div key={trace.id} className="fade-up" style={{
                  background: 'var(--bg-card)',
                  border: '1px solid var(--border)',
                  borderRadius: 'var(--radius-lg)',
                  overflow: 'hidden',
                  boxShadow: '0 4px 20px rgba(0,0,0,0.05)'
                }}>
                  {/* Header Row */}
                  <div style={{
                    padding: '16px 20px',
                    background: 'var(--bg-surface)',
                    borderBottom: '1px solid var(--border)',
                    display: 'flex', justifyContent: 'space-between', alignItems: 'center'
                  }}>
                    <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
                      <span className="badge badge-blue">ID: {trace.id.toUpperCase()}</span>
                      <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                        {new Date(trace.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                    <div style={{ display: 'flex', gap: 8 }}>
                      <span className="badge badge-green">{trace.latency}ms Latency</span>
                      <span className="badge badge-amber">{Math.round(trace.confidence * 100)}% Match</span>
                    </div>
                  </div>

                  {/* Nodes Wrapper */}
                  <div style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: 20 }}>
                    
                    {/* Node 1: Input */}
                    <div style={{ display: 'flex', gap: 16 }}>
                      <div style={{ width: 40, height: 40, borderRadius: '50%', background: 'var(--accent-blue)20', color: 'var(--accent-blue)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold' }}>1</div>
                      <div style={{ flex: 1 }}>
                        <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 4, textTransform: 'uppercase', letterSpacing: 1 }}>Trigger (User Query)</div>
                        <div style={{ fontSize: 15, padding: 12, background: 'var(--bg-base)', borderRadius: 6, border: '1px solid var(--border)' }}>
                          {trace.query}
                        </div>
                      </div>
                    </div>

                    {/* Path Line */}
                    <div style={{ width: 2, height: 20, background: 'var(--border)', marginLeft: 19 }} />

                    {/* Node 2: Retrieval */}
                    <div style={{ display: 'flex', gap: 16 }}>
                      <div style={{ width: 40, height: 40, borderRadius: '50%', background: 'var(--accent-green)20', color: 'var(--accent-green)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold' }}>2</div>
                      <div style={{ flex: 1 }}>
                        <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 4, textTransform: 'uppercase', letterSpacing: 1 }}>Retrieval (Logic Vault)</div>
                        <div style={{ fontSize: 13, padding: 12, background: 'var(--bg-base)', borderRadius: 6, border: '1px solid var(--border)' }}>
                          {trace.sources && trace.sources.length > 0 ? (
                            <ul style={{ paddingLeft: 20, margin: 0, color: 'var(--accent-green)' }}>
                              {trace.sources.map((s, i) => <li key={i}>{s}</li>)}
                            </ul>
                          ) : (
                            <span style={{ color: 'var(--text-muted)' }}>No Master Cases matched the similarity threshold.</span>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Path Line */}
                    <div style={{ width: 2, height: 20, background: 'var(--border)', marginLeft: 19 }} />

                    {/* Node 3: Rationale */}
                    <div style={{ display: 'flex', gap: 16 }}>
                      <div style={{ width: 40, height: 40, borderRadius: '50%', background: 'var(--accent-purple)20', color: 'var(--accent-purple)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold' }}>3</div>
                      <div style={{ flex: 1 }}>
                        <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 4, textTransform: 'uppercase', letterSpacing: 1 }}>Reasoning Engine (Chain of Thought)</div>
                        <div style={{ 
                          fontSize: 13, padding: 16, background: 'var(--bg-base)', 
                          borderRadius: 6, border: '1px solid var(--accent-purple)50',
                          borderLeft: '4px solid var(--accent-purple)',
                          fontFamily: 'monospace', whiteSpace: 'pre-wrap', lineHeight: 1.6
                        }}>
                          {trace.rationale}
                        </div>
                      </div>
                    </div>

                    {/* Path Line */}
                    <div style={{ width: 2, height: 20, background: 'var(--border)', marginLeft: 19 }} />

                    {/* Node 4: Generation */}
                    <div style={{ display: 'flex', gap: 16 }}>
                      <div style={{ width: 40, height: 40, borderRadius: '50%', background: 'var(--accent-orange)20', color: 'var(--accent-orange)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold' }}>4</div>
                      <div style={{ flex: 1 }}>
                        <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 4, textTransform: 'uppercase', letterSpacing: 1 }}>Generation (Final Persona Synthesis)</div>
                        <div style={{ fontSize: 14, padding: 16, background: 'var(--bg-base)', borderRadius: 6, border: '1px solid var(--accent-orange)50', lineHeight: 1.6 }}>
                          {trace.response}
                        </div>
                      </div>
                    </div>

                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
