'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { DEMO_LOGIC_VAULT, DEMO_STATS } from '../../../lib/demo/demo_seed'

const TRIAGE_STYLES = {
  YELLOW_ZONE: { bg: 'rgba(234,179,8,0.08)', border: 'rgba(234,179,8,0.25)', badge_bg: '#FEF3C7', badge_color: '#D97706', emoji: '🟡', label: 'YELLOW ZONE' },
  GREEN_ZONE:  { bg: 'rgba(16,185,129,0.08)', border: 'rgba(16,185,129,0.25)', badge_bg: '#D1FAE5', badge_color: '#059669', emoji: '🟢', label: 'GREEN ZONE' },
  RED_ZONE:    { bg: 'rgba(239,68,68,0.08)', border: 'rgba(239,68,68,0.25)', badge_bg: '#FEE2E2', badge_color: '#DC2626', emoji: '🔴', label: 'RED ZONE' },
}

export default function DemoInspectorPage() {
  const router = useRouter()
  const [expandedCase, setExpandedCase] = useState(null)
  const cases = Object.values(DEMO_LOGIC_VAULT)
  const totalApplications = cases.reduce((s, c) => s + c.times_used, 0)
  const avgThreshold = Math.round(cases.reduce((s, c) => s + c.confidence_trigger, 0) / cases.length * 100)

  return (
    <div style={{ minHeight: '100vh', background: '#0F172A', fontFamily: 'Inter, system-ui, sans-serif' }}>
      {/* Top Bar */}
      <div style={{ padding: '16px 32px', borderBottom: '1px solid rgba(255,255,255,0.08)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <button onClick={() => router.push('/demo')} style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', padding: '6px 14px', color: '#94A3B8', fontSize: '13px', cursor: 'pointer', fontWeight: 600 }}>
            ← Back to Demo Hub
          </button>
          <span style={{ color: '#94A3B8', fontSize: '13px' }}>
            <span style={{ color: '#F1F5F9', fontWeight: 700 }}>Logic Vault Inspector</span>
            {' · '}{cases.length} MasterCases Active
          </span>
        </div>
        <button onClick={() => router.push('/demo/audit')} style={{ background: 'rgba(13,148,136,0.1)', border: '1px solid rgba(13,148,136,0.3)', borderRadius: '8px', padding: '6px 16px', color: '#14B8A6', fontSize: '13px', cursor: 'pointer', fontWeight: 700 }}>
          📋 View Audit Transcript →
        </button>
      </div>

      <div style={{ padding: '40px 48px', maxWidth: '1100px', margin: '0 auto' }}>
        {/* Header */}
        <div style={{ marginBottom: '36px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '14px', marginBottom: '24px' }}>
            <div style={{ width: '52px', height: '52px', borderRadius: '14px', background: 'rgba(124,58,237,0.15)', border: '1px solid rgba(124,58,237,0.3)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '26px' }}>🧠</div>
            <div>
              <h1 style={{ fontSize: '28px', fontWeight: 800, color: '#F1F5F9' }}>Logic Vault</h1>
              <p style={{ fontSize: '14px', color: '#64748B' }}>All verified MasterCases powering the AI twin's clinical decisions</p>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '14px', flexWrap: 'wrap' }}>
            {[
              { label: 'Total MasterCases', value: cases.length, color: '#60A5FA' },
              { label: 'Doctor Verified', value: cases.length, color: '#10B981' },
              { label: 'Avg Confidence Threshold', value: `${avgThreshold}%`, color: '#FBBF24' },
              { label: 'Total Applications', value: totalApplications, color: '#A78BFA' },
            ].map((stat, i) => (
              <div key={i} style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.07)', borderRadius: '10px', padding: '14px 20px', minWidth: '140px' }}>
                <div style={{ fontSize: '22px', fontWeight: 800, color: stat.color }}>{stat.value}</div>
                <div style={{ fontSize: '11px', color: '#475569', fontWeight: 600, marginTop: '2px' }}>{stat.label}</div>
              </div>
            ))}
          </div>
        </div>

        {/* MasterCase Cards */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {cases.map((entry) => {
            const triage = TRIAGE_STYLES[entry.triage_decision] || TRIAGE_STYLES.YELLOW_ZONE
            const isExpanded = expandedCase === entry.id

            return (
              <div key={entry.id} style={{
                background: 'rgba(255,255,255,0.03)',
                border: `1px solid ${isExpanded ? 'rgba(124,58,237,0.4)' : 'rgba(255,255,255,0.07)'}`,
                borderRadius: '16px', overflow: 'hidden', transition: 'border-color 0.2s',
              }}>
                <div onClick={() => setExpandedCase(isExpanded ? null : entry.id)} style={{ padding: '24px 28px', cursor: 'pointer', display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '16px' }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '10px' }}>
                      <span style={{ background: 'rgba(59,130,246,0.15)', color: '#60A5FA', fontSize: '11px', fontWeight: 700, padding: '3px 10px', borderRadius: '6px', border: '1px solid rgba(59,130,246,0.2)' }}>{entry.id}</span>
                      <span style={{ background: 'rgba(255,255,255,0.05)', color: '#64748B', fontSize: '11px', fontWeight: 600, padding: '3px 10px', borderRadius: '6px' }}>{entry.version}</span>
                      <span style={{ background: triage.bg, color: triage.badge_color, border: `1px solid ${triage.border}`, fontSize: '11px', fontWeight: 700, padding: '3px 10px', borderRadius: '6px' }}>
                        {triage.emoji} {triage.label}
                      </span>
                    </div>
                    <h3 style={{ fontSize: '17px', fontWeight: 800, color: '#F1F5F9', marginBottom: '6px' }}>{entry.title}</h3>
                    <p style={{ fontSize: '13px', color: '#64748B' }}>
                      {entry.workflow} · Confidence threshold: ≥{Math.round(entry.confidence_trigger * 100)}% · Used {entry.times_used}× in consultations
                    </p>
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '12px', flexShrink: 0 }}>
                    <div style={{ background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.2)', borderRadius: '8px', padding: '6px 12px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <span style={{ fontSize: '12px' }}>✅</span>
                      <span style={{ fontSize: '11px', fontWeight: 700, color: '#10B981' }}>Doctor Verified</span>
                    </div>
                    <div style={{ color: '#475569', fontSize: '18px', transform: isExpanded ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s' }}>▾</div>
                  </div>
                </div>

                {isExpanded && (
                  <div style={{ borderTop: '1px solid rgba(255,255,255,0.07)', padding: '28px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
                    <div>
                      <div style={{ fontSize: '11px', fontWeight: 700, color: '#475569', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '10px' }}>📜 Clinical Decision Rule</div>
                      <div style={{ background: '#0B1121', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '10px', padding: '20px', fontSize: '13px', color: '#94A3B8', lineHeight: 1.9, whiteSpace: 'pre-line', fontFamily: 'monospace' }}>
                        {entry.rule}
                      </div>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px' }}>
                      {[
                        { label: 'Domain', value: entry.domain, icon: '🏥' },
                        { label: 'Workflow', value: entry.workflow, icon: '⚙️' },
                        { label: 'Times Applied', value: `${entry.times_used}×`, icon: '🔁' },
                        { label: 'Confidence Trigger', value: `≥ ${Math.round(entry.confidence_trigger * 100)}%`, icon: '🎯' },
                        { label: 'Approval Date', value: entry.approved_date, icon: '📅' },
                        { label: 'Last Updated', value: entry.last_updated, icon: '🔄' },
                      ].map((item, i) => (
                        <div key={i} style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.07)', borderRadius: '8px', padding: '12px' }}>
                          <div style={{ fontSize: '11px', color: '#475569', fontWeight: 600, textTransform: 'uppercase', marginBottom: '4px' }}>{item.icon} {item.label}</div>
                          <div style={{ fontSize: '13px', color: '#94A3B8', fontWeight: 600 }}>{item.value}</div>
                        </div>
                      ))}
                    </div>

                    <div style={{ background: 'rgba(16,185,129,0.05)', border: '1px solid rgba(16,185,129,0.15)', borderRadius: '10px', padding: '16px', display: 'flex', alignItems: 'center', gap: '14px' }}>
                      <div style={{ width: '42px', height: '42px', borderRadius: '50%', background: 'rgba(16,185,129,0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '20px', flexShrink: 0 }}>👨‍⚕️</div>
                      <div>
                        <div style={{ fontSize: '12px', color: '#10B981', fontWeight: 700, marginBottom: '2px' }}>✓ Peer-Reviewed &amp; Approved</div>
                        <div style={{ fontSize: '14px', color: '#94A3B8', fontWeight: 600 }}>{entry.approved_by}</div>
                        <div style={{ fontSize: '12px', color: '#475569' }}>Approved on {entry.approved_date}</div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
