'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { DEMO_STATS, DEMO_PATIENT } from '../../lib/demo/demo_seed'

export default function DemoHubPage() {
  const router = useRouter()
  const [hoveredCard, setHoveredCard] = useState(null)

  const cards = [
    {
      id: 'live',
      icon: '🩺',
      title: 'Start Live Patient Chat',
      description: 'Open the patient portal and chat with the AI twin in real time. The doctor dashboard updates live.',
      action: () => window.open('/portal?session_id=demo-session&domain=healthcare&role=doctor', '_blank'),
      color: '#3B82F6',
      bg: '#EFF6FF',
      border: '#BFDBFE',
    },
    {
      id: 'audit',
      icon: '📋',
      title: 'Review Completed Consultation',
      description: 'Walk through a finished consultation log. See every AI decision and click "Why?" to inspect the reasoning.',
      action: () => router.push('/demo/audit'),
      color: '#0D9488',
      bg: '#F0FDFA',
      border: '#99F6E4',
      highlight: true,
    },
    {
      id: 'inspector',
      icon: '🧠',
      title: 'Open Logic Vault',
      description: 'Browse all verified MasterCases used by the AI. See which clinical rules drive every decision.',
      action: () => router.push('/demo/inspector'),
      color: '#7C3AED',
      bg: '#F5F3FF',
      border: '#DDD6FE',
    },
  ]

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #0F172A 100%)',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '40px 24px',
      fontFamily: 'Inter, system-ui, sans-serif',
    }}>
      <div style={{ textAlign: 'center', marginBottom: '48px' }}>
        <div style={{
          display: 'inline-flex', alignItems: 'center', gap: '12px',
          background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)',
          borderRadius: '12px', padding: '10px 20px', marginBottom: '24px',
        }}>
          <span style={{ fontSize: '20px' }}>✨</span>
          <span style={{ color: '#94A3B8', fontSize: '13px', fontWeight: 600, letterSpacing: '0.1em', textTransform: 'uppercase' }}>
            Expert Digital Twin — Demo Mode
          </span>
        </div>

        <h1 style={{
          fontSize: '42px', fontWeight: 800, color: '#F8FAFC',
          lineHeight: 1.2, marginBottom: '16px', letterSpacing: '-0.02em',
        }}>
          AI That Works.<br />
          <span style={{
            background: 'linear-gradient(135deg, #0EA5E9, #14B8A6)',
            WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
          }}>Doctor Who Reviews.</span>
        </h1>
        <p style={{ color: '#94A3B8', fontSize: '17px', maxWidth: '520px', lineHeight: 1.6, margin: '0 auto' }}>
          The twin handles the consultation. You review the logic. Your time is saved.
        </p>
      </div>

      <div style={{
        background: 'rgba(20, 184, 166, 0.08)',
        border: '1px solid rgba(20, 184, 166, 0.3)',
        borderRadius: '16px', padding: '20px 32px',
        marginBottom: '48px',
        display: 'flex', alignItems: 'center', gap: '32px',
        flexWrap: 'wrap', justifyContent: 'center',
      }}>
        {[
          { value: `${DEMO_STATS.bot_handled_pct}%`, label: 'Handled by AI', color: '#14B8A6' },
          { value: `${DEMO_STATS.session_duration_min} min`, label: 'Full Consultation', color: '#F8FAFC' },
          { value: `${Math.round(DEMO_STATS.avg_confidence * 100)}%`, label: 'Avg Confidence', color: '#A78BFA' },
          { value: DEMO_STATS.expert_corrections, label: 'Expert Correction', color: '#FBBF24' },
        ].map((stat, i) => (
          <div key={i} style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '36px', fontWeight: 800, color: stat.color }}>{stat.value}</div>
            <div style={{ fontSize: '12px', color: '#64748B', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>{stat.label}</div>
          </div>
        )).reduce((acc, el, i) => {
          if (i > 0) acc.push(<div key={`div-${i}`} style={{ width: '1px', height: '48px', background: 'rgba(255,255,255,0.1)' }} />)
          acc.push(el)
          return acc
        }, [])}
      </div>

      <div style={{
        display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)',
        gap: '20px', maxWidth: '960px', width: '100%',
        marginBottom: '48px',
      }}>
        {cards.map((card) => (
          <div
            key={card.id}
            onClick={card.action}
            onMouseEnter={() => setHoveredCard(card.id)}
            onMouseLeave={() => setHoveredCard(null)}
            style={{
              background: hoveredCard === card.id ? 'rgba(255,255,255,0.06)' : 'rgba(255,255,255,0.03)',
              border: `1px solid ${hoveredCard === card.id ? 'rgba(255,255,255,0.15)' : 'rgba(255,255,255,0.07)'}`,
              borderRadius: '20px', padding: '32px',
              cursor: 'pointer',
              transition: 'all 0.25s ease',
              transform: hoveredCard === card.id ? 'translateY(-4px)' : 'none',
              boxShadow: hoveredCard === card.id ? '0 20px 40px rgba(0,0,0,0.3)' : 'none',
              position: 'relative', overflow: 'hidden',
            }}
          >
            {card.highlight && (
              <div style={{
                position: 'absolute', top: '12px', right: '12px',
                background: '#0D9488', color: '#FFF',
                fontSize: '10px', fontWeight: 800, letterSpacing: '0.08em',
                padding: '3px 10px', borderRadius: '99px', textTransform: 'uppercase',
              }}>
                Start Here
              </div>
            )}
            <div style={{
              width: '56px', height: '56px', borderRadius: '14px',
              background: card.bg, border: `1px solid ${card.border}`,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: '26px', marginBottom: '20px',
            }}>
              {card.icon}
            </div>
            <h3 style={{ fontSize: '17px', fontWeight: 700, color: '#F1F5F9', marginBottom: '10px' }}>
              {card.title}
            </h3>
            <p style={{ fontSize: '14px', color: '#64748B', lineHeight: 1.6 }}>
              {card.description}
            </p>
            <div style={{ marginTop: '24px', color: card.color, fontSize: '13px', fontWeight: 700 }}>
              Open →
            </div>
          </div>
        ))}
      </div>

      <div style={{
        background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.07)',
        borderRadius: '12px', padding: '16px 24px',
        display: 'flex', gap: '24px', alignItems: 'center', flexWrap: 'wrap', justifyContent: 'center',
        maxWidth: '700px',
      }}>
        <span style={{ color: '#475569', fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.08em' }}>Demo Patient</span>
        <span style={{ color: '#94A3B8', fontSize: '13px' }}>👤 {DEMO_PATIENT.name}, {DEMO_PATIENT.age}yr {DEMO_PATIENT.gender}</span>
        <span style={{ color: '#94A3B8', fontSize: '13px' }}>⚖️ BMI {DEMO_PATIENT.bmi}</span>
        <span style={{ color: '#94A3B8', fontSize: '13px' }}>🩸 BP {DEMO_PATIENT.bp}</span>
        <span style={{
          background: 'rgba(234, 179, 8, 0.15)', color: '#FBBF24',
          border: '1px solid rgba(234,179,8,0.3)',
          padding: '2px 10px', borderRadius: '99px', fontSize: '12px', fontWeight: 700,
        }}>
          🟡 YELLOW ZONE
        </span>
      </div>

      <p style={{ color: '#334155', fontSize: '12px', marginTop: '32px' }}>
        Demo Mode — All consultation data is hardcoded for presentation purposes. No live API calls.
      </p>
    </div>
  )
}
