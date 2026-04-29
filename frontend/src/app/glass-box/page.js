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
    <div style={{ display: 'flex', minHeight: '100vh', background: '#F8FAFC', fontFamily: 'var(--font-sans), Inter, system-ui, sans-serif' }}>
      <Sidebar active="/glass-box" />

      <main style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        
        {/* Header */}
        <div style={{
          padding: '24px 32px',
          borderBottom: '1px solid #E2E8F0',
          background: '#FFFFFF',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        }}>
          <div>
            <h1 style={{ fontSize: 22, fontWeight: 700, color: '#0F172A' }}>Execution Tree Hierarchy</h1>
            <p style={{ fontSize: 13, color: '#64748B', marginTop: 4 }}>
              Transparent node-by-node audit log of the Digital Twin's clinical reasoning.
            </p>
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            <span className="badge badge-teal">Hierarchy Map Active</span>
            <span className="badge badge-purple">{traces.length} Logs</span>
          </div>
        </div>

        {/* Content */}
        <div style={{ flex: 1, overflow: 'auto', padding: '32px' }}>
          {traces.length === 0 ? (
            <div style={{
              textAlign: 'center', padding: '60px 20px',
              border: '1px dashed #E2E8F0', borderRadius: '16px',
              color: '#64748B', background: '#FFFFFF', boxShadow: '0 4px 20px rgba(0,0,0,0.02)'
            }}>
              <div style={{ fontSize: 40, opacity: 0.5, marginBottom: 16 }}>🌿</div>
              <h3 style={{ fontSize: 16, fontWeight: 600, color: '#0F172A', marginBottom: 8 }}>No Execution Paths Logged</h3>
              <p style={{ fontSize: 13 }}>Send a message in the Twin Chat to inspect the logic node graph.</p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 40 }}>
              {traces.map((trace) => {
                const hasMatch = trace.sources && trace.sources.length > 0;

                return (
                  <div key={trace.id} className="fade-up" style={{
                    background: '#FFFFFF',
                    border: '1px solid #E2E8F0',
                    borderRadius: '20px',
                    padding: '32px',
                    boxShadow: '0 4px 24px rgba(15, 23, 42, 0.04)',
                    overflowX: 'auto'
                  }}>
                    {/* Trace Metadata */}
                    <div style={{
                      display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                      borderBottom: '1px solid #F1F5F9', paddingBottom: '20px', marginBottom: '40px'
                    }}>
                      <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
                        <span style={{ background: '#EFF6FF', color: '#3B82F6', padding: '4px 12px', borderRadius: 99, fontSize: 11, fontWeight: 700 }}>ID: {trace.id.toUpperCase()}</span>
                        <span style={{ fontSize: 13, color: '#94A3B8' }}>{new Date(trace.timestamp).toLocaleTimeString()}</span>
                      </div>
                      <div style={{ display: 'flex', gap: 12 }}>
                        <span style={{ background: '#F0FDFA', color: '#16A34A', padding: '4px 12px', borderRadius: 99, fontSize: 11, fontWeight: 700 }}>{trace.latency}MS LATENCY</span>
                        <span style={{ background: '#FFFBEB', color: '#D97706', padding: '4px 12px', borderRadius: 99, fontSize: 11, fontWeight: 700 }}>{Math.round((trace.confidence || 0) * 100)}% MATCH</span>
                      </div>
                    </div>

                    {/* ── SIDEWAYS HIERARCHY GRAPH (LEFT-TO-RIGHT) ── */}
                    <div style={{ display: 'flex', alignItems: 'center', gap: 0, minWidth: '1500px', padding: '20px 0' }}>
                      
                      {/* COLUMN 1: TRIGGER NODE */}
                      <div style={{
                        background: '#FFFFFF', border: '1px solid #E2E8F0', borderRadius: '12px',
                        padding: '16px 20px', width: '220px', minHeight: '120px', display: 'flex', flexDirection: 'column', justifyContent: 'center',
                        boxShadow: '0 4px 12px rgba(15, 23, 42, 0.03)', position: 'relative'
                      }}>
                        <div style={{ fontSize: 13, color: '#0F172A', fontWeight: 700, marginBottom: 8 }}>Trigger Query</div>
                        <div style={{ 
                          fontSize: 13, color: '#475569', fontWeight: 500,
                          background: '#F8FAFC', padding: '12px', borderRadius: '8px', 
                          border: '1px solid #E2E8F0', lineHeight: 1.4
                        }}>
                          "{trace.query}"
                        </div>
                      </div>

                      {/* SVG CONNECTOR 1 */}
                      <svg width="60" height="240" style={{ display: 'block', overflow: 'visible' }}>
                        <circle cx="2" cy="120" r="4" fill="#FFFFFF" stroke="#475569" strokeWidth="2" />
                        <path d="M 6 120 L 16 120 C 30 120, 30 60, 44 60 L 54 60" stroke="#475569" strokeWidth="2" fill="none" />
                        <path d="M 6 120 L 16 120 C 30 120, 30 180, 44 180 L 54 180" stroke="#475569" strokeWidth="2" fill="none" />
                        <circle cx="56" cy="60" r="4" fill="#FFFFFF" stroke="#475569" strokeWidth="2" />
                        <circle cx="56" cy="180" r="4" fill="#FFFFFF" stroke="#475569" strokeWidth="2" />
                      </svg>

                      {/* COLUMN 2: RETRIEVAL FORKS */}
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 40, width: '240px' }}>
                        {/* TOP FORK: VERIFIED CASES */}
                        <div style={{
                          background: '#FFFFFF', border: '1px solid #E2E8F0',
                          borderRadius: '12px', padding: '14px 18px', minHeight: '100px',
                          opacity: hasMatch ? 1 : 0.4, transition: 'all 0.3s', display: 'flex', flexDirection: 'column', justifyContent: 'center'
                        }}>
                          <div style={{ fontSize: 13, color: '#10B981', fontWeight: 700, marginBottom: 8 }}>Logic Vault Match</div>
                          <div style={{ 
                            fontSize: 13, color: '#475569', fontWeight: 500,
                            background: '#F8FAFC', padding: '10px', borderRadius: '8px', 
                            border: '1px solid #E2E8F0'
                          }}>
                            {hasMatch ? (
                              <ul style={{ margin: 0, paddingLeft: 12, listStyle: 'circle' }}>
                                {trace.sources.map((s, idx) => <li key={idx}>{s}</li>)}
                              </ul>
                            ) : "Similarity check failed."}
                          </div>
                        </div>

                        {/* BOTTOM FORK: FALLBACK MODE */}
                        <div style={{
                          background: '#FFFFFF', border: '1px solid #E2E8F0',
                          borderRadius: '12px', padding: '14px 18px', minHeight: '100px',
                          opacity: !hasMatch ? 1 : 0.4, transition: 'all 0.3s', display: 'flex', flexDirection: 'column', justifyContent: 'center'
                        }}>
                          <div style={{ fontSize: 13, color: '#F59E0B', fontWeight: 700, marginBottom: 8 }}>Fallback Mode</div>
                          <div style={{ 
                            fontSize: 13, color: '#475569', fontWeight: 500,
                            background: '#F8FAFC', padding: '10px', borderRadius: '8px', 
                            border: '1px solid #E2E8F0'
                          }}>
                            {!hasMatch ? "Declining clinical authority. Guardrail path." : "Retrieval safe."}
                          </div>
                        </div>
                      </div>

                      {/* SVG CONNECTOR 2 */}
                      <svg width="60" height="240" style={{ display: 'block', overflow: 'visible' }}>
                        <circle cx="4" cy="60" r="4" fill="#FFFFFF" stroke="#475569" strokeWidth="2" />
                        <circle cx="4" cy="180" r="4" fill="#FFFFFF" stroke="#475569" strokeWidth="2" />
                        <path d="M 8 60 L 18 60 C 30 60, 30 120, 44 120 L 54 120" stroke="#475569" strokeWidth="2" fill="none" />
                        <path d="M 8 180 L 18 180 C 30 180, 30 120, 44 120 L 54 120" stroke="#475569" strokeWidth="2" fill="none" />
                        <circle cx="56" cy="120" r="4" fill="#FFFFFF" stroke="#475569" strokeWidth="2" />
                      </svg>

                      {/* COLUMN 3: REASONING ENGINE */}
                      <div style={{
                        background: '#FFFFFF', border: '1px solid #E2E8F0', borderRadius: '12px',
                        padding: '16px 20px', width: '280px', minHeight: '120px', display: 'flex', flexDirection: 'column', justifyContent: 'center',
                        boxShadow: '0 4px 12px rgba(15, 23, 42, 0.03)'
                      }}>
                        <div style={{ fontSize: 13, color: '#0F172A', fontWeight: 700, marginBottom: 8 }}>Chain of Thought</div>
                        <div style={{ 
                          fontSize: 13, color: '#475569', fontWeight: 500,
                          background: '#F8FAFC', padding: '12px', borderRadius: '8px', 
                          border: '1px solid #E2E8F0', maxHeight: '180px', overflowY: 'auto'
                        }}>
                          {trace.rationale}
                        </div>
                      </div>

                      {/* SVG CONNECTOR 3 */}
                      <svg width="60" height="240" style={{ display: 'block', overflow: 'visible' }}>
                        <circle cx="4" cy="120" r="4" fill="#FFFFFF" stroke="#475569" strokeWidth="2" />
                        <line x1="8" y1="120" x2="52" y2="120" stroke="#475569" strokeWidth="2" />
                        <circle cx="56" cy="120" r="4" fill="#FFFFFF" stroke="#475569" strokeWidth="2" />
                      </svg>

                      {/* COLUMN 4: GENERATION */}
                      <div style={{
                        background: '#FFFFFF', border: '1px solid #E2E8F0', borderRadius: '12px',
                        padding: '24px', width: '750px', minHeight: '120px', display: 'flex', flexDirection: 'column', justifyContent: 'center',
                        boxShadow: '0 4px 12px rgba(15, 23, 42, 0.03)'
                      }}>
                        <div style={{ fontSize: 13, color: '#0F172A', fontWeight: 700, marginBottom: 8 }}>Final Output</div>
                        <div style={{ 
                          fontSize: 13, fontWeight: 500, color: '#475569', lineHeight: 1.5,
                          background: '#F8FAFC', padding: '16px', borderRadius: '8px', 
                          border: '1px solid #E2E8F0', maxHeight: '350px', overflowY: 'auto'
                        }}>
                          "{trace.response}"
                        </div>
                      </div>

                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
