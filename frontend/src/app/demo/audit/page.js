'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { DEMO_TRANSCRIPT, DEMO_LOGIC_VAULT, DEMO_STATS, DEMO_PATIENT } from '../../../lib/demo/demo_seed'

const TRIAGE_COLORS = {
  YELLOW_ZONE: { bg: 'rgba(234,179,8,0.1)', border: 'rgba(234,179,8,0.3)', color: '#FBBF24', emoji: '🟡' },
  GREEN_ZONE:  { bg: 'rgba(16,185,129,0.1)', border: 'rgba(16,185,129,0.3)', color: '#10B981', emoji: '🟢' },
  RED_ZONE:    { bg: 'rgba(239,68,68,0.1)', border: 'rgba(239,68,68,0.3)', color: '#EF4444', emoji: '🔴' },
}

function ConfidenceBadge({ score }) {
  if (score === null || score === undefined) return null
  const pct = Math.round(score * 100)
  const color = score >= 0.85 ? '#10B981' : score >= 0.70 ? '#FBBF24' : '#EF4444'
  const bg = score >= 0.85 ? 'rgba(16,185,129,0.1)' : score >= 0.70 ? 'rgba(234,179,8,0.1)' : 'rgba(239,68,68,0.1)'
  return (
    <span style={{
      fontSize: '11px', fontWeight: 700, padding: '2px 8px', borderRadius: '99px',
      background: bg, color, border: `1px solid ${color}30`, marginLeft: '6px'
    }}>
      {pct}% confidence
    </span>
  )
}

function LogicVaultDrawer({ caseId, onClose }) {
  const entry = DEMO_LOGIC_VAULT[caseId]
  if (!entry) return null
  const triage = TRIAGE_COLORS[entry.triage_decision] || TRIAGE_COLORS.YELLOW_ZONE

  return (
    <>
      <div onClick={onClose} style={{
        position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)',
        zIndex: 100, backdropFilter: 'blur(4px)',
      }} />
      <div style={{
        position: 'fixed', right: 0, top: 0, bottom: 0,
        width: '480px', background: '#0F172A',
        borderLeft: '1px solid rgba(255,255,255,0.1)',
        zIndex: 101, overflowY: 'auto', padding: '32px',
        fontFamily: 'Inter, system-ui, sans-serif',
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '24px' }}>
          <div>
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center', marginBottom: '8px' }}>
              <span style={{ background: 'rgba(59,130,246,0.15)', color: '#60A5FA', fontSize: '11px', fontWeight: 700, padding: '2px 10px', borderRadius: '6px' }}>
                {entry.id}
              </span>
              <span style={{ background: 'rgba(255,255,255,0.05)', color: '#64748B', fontSize: '11px', fontWeight: 600, padding: '2px 8px', borderRadius: '6px' }}>
                {entry.version}
              </span>
            </div>
            <h2 style={{ fontSize: '18px', fontWeight: 800, color: '#F1F5F9', lineHeight: 1.3 }}>{entry.title}</h2>
          </div>
          <button onClick={onClose} style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', padding: '6px 12px', color: '#94A3B8', fontSize: '13px', cursor: 'pointer', fontWeight: 600, flexShrink: 0 }}>
            ✕ Close
          </button>
        </div>

        <div style={{ background: triage.bg, border: `1px solid ${triage.border}`, borderRadius: '10px', padding: '12px 16px', marginBottom: '24px', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ fontSize: '20px' }}>{triage.emoji}</span>
          <div>
            <div style={{ fontSize: '11px', color: '#64748B', fontWeight: 600, textTransform: 'uppercase' }}>Triage Decision</div>
            <div style={{ fontSize: '15px', fontWeight: 800, color: triage.color }}>{entry.triage_decision.replace('_', ' ')}</div>
          </div>
        </div>

        <div style={{ marginBottom: '24px' }}>
          <div style={{ fontSize: '11px', fontWeight: 700, color: '#475569', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '10px' }}>📜 Clinical Rule</div>
          <div style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '10px', padding: '16px', fontSize: '13px', color: '#CBD5E1', lineHeight: 1.8, whiteSpace: 'pre-line', fontFamily: 'monospace' }}>
            {entry.rule}
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '24px' }}>
          {[
            { label: 'Confidence Threshold', value: `≥ ${Math.round(entry.confidence_trigger * 100)}%` },
            { label: 'Times Applied', value: `${entry.times_used} consultations` },
            { label: 'Last Updated', value: entry.last_updated },
            { label: 'Workflow', value: entry.workflow },
          ].map((item, i) => (
            <div key={i} style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.07)', borderRadius: '8px', padding: '12px' }}>
              <div style={{ fontSize: '11px', color: '#475569', fontWeight: 600, textTransform: 'uppercase', marginBottom: '4px' }}>{item.label}</div>
              <div style={{ fontSize: '13px', color: '#94A3B8', fontWeight: 600 }}>{item.value}</div>
            </div>
          ))}
        </div>

        <div style={{ background: 'rgba(16,185,129,0.05)', border: '1px solid rgba(16,185,129,0.15)', borderRadius: '10px', padding: '14px 16px', display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ width: '36px', height: '36px', borderRadius: '50%', background: 'rgba(16,185,129,0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '18px', flexShrink: 0 }}>👨‍⚕️</div>
          <div>
            <div style={{ fontSize: '12px', color: '#10B981', fontWeight: 700 }}>✓ Verified &amp; Approved</div>
            <div style={{ fontSize: '13px', color: '#94A3B8', fontWeight: 500 }}>{entry.approved_by}</div>
            <div style={{ fontSize: '11px', color: '#475569' }}>on {entry.approved_date}</div>
          </div>
        </div>
      </div>
    </>
  )
}

export default function DemoAuditPage() {
  const router = useRouter()
  const [activeDrawer, setActiveDrawer] = useState(null)

  const formatTime = (iso) => new Date(iso).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', second: '2-digit' })

  return (
    <div style={{ minHeight: '100vh', background: '#F8FAFC', fontFamily: 'Inter, system-ui, sans-serif', display: 'flex', flexDirection: 'column' }}>
      {/* Top Bar */}
      <div style={{ background: '#0F172A', padding: '16px 32px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid rgba(255,255,255,0.08)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <button onClick={() => router.push('/demo')} style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', padding: '6px 14px', color: '#94A3B8', fontSize: '13px', cursor: 'pointer', fontWeight: 600 }}>
            ← Back to Demo Hub
          </button>
          <div style={{ color: '#64748B', fontSize: '13px' }}>
            <span style={{ color: '#F1F5F9', fontWeight: 700 }}>Consultation Audit</span>
            {' · '}Session: {DEMO_STATS.session_id}
          </div>
        </div>
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <span style={{ fontSize: '12px', color: '#64748B' }}>Click</span>
          <span style={{ background: 'rgba(59,130,246,0.15)', color: '#60A5FA', fontSize: '12px', fontWeight: 700, padding: '4px 12px', borderRadius: '6px', border: '1px solid rgba(59,130,246,0.3)' }}>ℹ️ Why?</span>
          <span style={{ fontSize: '12px', color: '#64748B' }}>on any AI response to see the reasoning</span>
        </div>
      </div>

      <div style={{ display: 'flex', flex: 1 }}>
        {/* LEFT SIDEBAR */}
        <div style={{ width: '300px', flexShrink: 0, background: '#FFFFFF', borderRight: '1px solid #E2E8F0', padding: '24px 20px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {/* Patient Card */}
          <div>
            <div style={{ fontSize: '11px', fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '10px' }}>Patient Profile</div>
            <div style={{ background: '#F8FAFC', borderRadius: '12px', padding: '14px', border: '1px solid #E2E8F0' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
                <div style={{ width: '40px', height: '40px', borderRadius: '50%', background: 'linear-gradient(135deg, #3B82F6, #6366F1)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '18px' }}>👤</div>
                <div>
                  <div style={{ fontSize: '14px', fontWeight: 700, color: '#0F172A' }}>{DEMO_PATIENT.name}</div>
                  <div style={{ fontSize: '12px', color: '#64748B' }}>{DEMO_PATIENT.age}yr, {DEMO_PATIENT.gender}</div>
                </div>
              </div>
              {[
                { label: 'BMI', value: DEMO_PATIENT.bmi },
                { label: 'Blood Pressure', value: DEMO_PATIENT.bp },
                { label: 'Waist', value: `${DEMO_PATIENT.waist_inches} inches` },
              ].map((row, i) => (
                <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '7px 0', borderBottom: i < 2 ? '1px solid #F1F5F9' : 'none' }}>
                  <span style={{ fontSize: '12px', color: '#64748B' }}>{row.label}</span>
                  <span style={{ fontSize: '12px', fontWeight: 600, color: '#1E293B' }}>{row.value}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Triage */}
          <div>
            <div style={{ fontSize: '11px', fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '10px' }}>Triage Outcome</div>
            <div style={{ background: 'rgba(234,179,8,0.08)', border: '1px solid rgba(234,179,8,0.25)', borderRadius: '12px', padding: '14px', textAlign: 'center' }}>
              <div style={{ fontSize: '28px', marginBottom: '4px' }}>🟡</div>
              <div style={{ fontSize: '15px', fontWeight: 800, color: '#D97706' }}>YELLOW ZONE</div>
              <div style={{ fontSize: '12px', color: '#78716C', marginTop: '2px' }}>Elevated Priority</div>
            </div>
          </div>

          {/* Autonomy Stats */}
          <div>
            <div style={{ fontSize: '11px', fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '10px' }}>Session Autonomy</div>
            <div style={{ background: '#F0FDFA', border: '1px solid #99F6E4', borderRadius: '12px', padding: '14px' }}>
              {[
                { label: 'AI Handled', value: `${DEMO_STATS.bot_handled_pct}%`, color: '#0D9488' },
                { label: 'Duration', value: `${DEMO_STATS.session_duration_min} min`, color: '#0F172A' },
                { label: 'Avg Confidence', value: `${Math.round(DEMO_STATS.avg_confidence * 100)}%`, color: '#0F172A' },
                { label: 'Expert Corrections', value: DEMO_STATS.expert_corrections, color: '#D97706' },
              ].map((row, i) => (
                <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: i < 3 ? '1px solid #CCFBF1' : 'none' }}>
                  <span style={{ fontSize: '12px', color: '#64748B' }}>{row.label}</span>
                  <span style={{ fontSize: '13px', fontWeight: 800, color: row.color }}>{row.value}</span>
                </div>
              ))}
            </div>
          </div>

          <button onClick={() => router.push('/demo/inspector')} style={{ width: '100%', padding: '10px', borderRadius: '10px', background: '#F5F3FF', border: '1px solid #DDD6FE', color: '#7C3AED', fontSize: '13px', fontWeight: 700, cursor: 'pointer' }}>
            🧠 Open Logic Vault →
          </button>
        </div>

        {/* TRANSCRIPT */}
        <main style={{ flex: 1, overflowY: 'auto', padding: '32px 36px' }}>
          <h1 style={{ fontSize: '20px', fontWeight: 800, color: '#0F172A', marginBottom: '4px' }}>Consultation Transcript</h1>
          <p style={{ fontSize: '13px', color: '#64748B', marginBottom: '28px' }}>
            {DEMO_STATS.session_date} · {DEMO_STATS.session_duration_min} minute session · {DEMO_TRANSCRIPT.length} messages
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', maxWidth: '720px' }}>
            {DEMO_TRANSCRIPT.map((msg) => {
              const isUser = msg.role === 'user'
              const isExpert = msg.sender === 'human_expert'
              return (
                <div key={msg.id} style={{ display: 'flex', flexDirection: isUser ? 'row-reverse' : 'row', gap: '12px', alignItems: 'flex-start' }}>
                  <div style={{
                    width: '38px', height: '38px', borderRadius: '50%', flexShrink: 0,
                    background: isUser ? 'linear-gradient(135deg, #3B82F6, #6366F1)' : isExpert ? 'linear-gradient(135deg, #059669, #10B981)' : 'linear-gradient(135deg, #0EA5E9, #6366F1)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '16px',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                  }}>
                    {isUser ? '👤' : isExpert ? '👨‍⚕️' : '🤖'}
                  </div>

                  <div style={{ maxWidth: '74%' }}>
                    <div style={{ fontSize: '11px', fontWeight: 700, color: '#94A3B8', marginBottom: '5px', textAlign: isUser ? 'right' : 'left', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                      {isUser ? 'Patient' : isExpert ? 'Dr. Venkatesh (Expert Override)' : 'AI Twin'}
                      {!isUser && <ConfidenceBadge score={msg.confidence} />}
                    </div>

                    {isExpert && (
                      <div style={{ background: 'rgba(16,185,129,0.08)', border: '1px solid rgba(16,185,129,0.2)', borderRadius: '8px 8px 0 0', padding: '7px 12px', fontSize: '11px', color: '#059669', fontWeight: 700 }}>
                        ✋ HUMAN EXPERT OVERRIDE — Twin is learning from this correction
                      </div>
                    )}

                    <div style={{
                      padding: '13px 16px',
                      borderRadius: isUser ? '18px 4px 18px 18px' : isExpert ? '0 18px 18px 18px' : '4px 18px 18px 18px',
                      background: isUser ? 'linear-gradient(135deg, #3B82F6, #6366F1)' : isExpert ? '#ECFDF5' : '#FFFFFF',
                      color: isUser ? '#FFFFFF' : '#1E293B',
                      fontSize: '14px', lineHeight: 1.7,
                      boxShadow: isUser ? '0 4px 12px rgba(99,102,241,0.25)' : '0 1px 4px rgba(0,0,0,0.06)',
                      border: isUser ? 'none' : isExpert ? '1px solid #A7F3D0' : '1px solid #E2E8F0',
                      whiteSpace: 'pre-wrap', position: 'relative',
                      paddingBottom: (!isUser && !isExpert && msg.source_case_id) ? '38px' : '13px',
                    }}>
                      {msg.content}
                      {!isUser && !isExpert && msg.source_case_id && (
                        <button
                          onClick={() => setActiveDrawer(msg.source_case_id)}
                          style={{
                            position: 'absolute', bottom: '8px', right: '8px',
                            background: '#EFF6FF', border: '1px solid #BFDBFE',
                            borderRadius: '8px', padding: '4px 10px',
                            fontSize: '11px', fontWeight: 700, color: '#3B82F6',
                            cursor: 'pointer',
                          }}
                        >
                          ℹ️ Why?
                        </button>
                      )}
                    </div>

                    {!isUser && msg.rationale && (
                      <div style={{ marginTop: '5px', paddingLeft: '4px', fontSize: '11px', color: '#94A3B8', lineHeight: 1.5, fontStyle: 'italic' }}>
                        📌 {msg.rationale.length > 110 ? msg.rationale.slice(0, 110) + '…' : msg.rationale}
                      </div>
                    )}
                    <div style={{ fontSize: '11px', color: '#CBD5E1', marginTop: '3px', textAlign: isUser ? 'right' : 'left', paddingLeft: '4px' }}>
                      {formatTime(msg.created_at)}
                    </div>
                  </div>
                </div>
              )
            })}

            <div style={{ textAlign: 'center', padding: '24px', border: '1px dashed #E2E8F0', borderRadius: '12px', color: '#94A3B8', fontSize: '13px' }}>
              <div style={{ fontSize: '24px', marginBottom: '8px' }}>✅</div>
              Consultation completed · Flagged for physician review
            </div>
          </div>
        </main>
      </div>

      {activeDrawer && <LogicVaultDrawer caseId={activeDrawer} onClose={() => setActiveDrawer(null)} />}
    </div>
  )
}
