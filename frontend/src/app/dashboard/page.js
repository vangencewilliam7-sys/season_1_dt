'use client'
import Sidebar from '../../components/layout/Sidebar'
import { useState, useEffect } from 'react'
import { DashboardService } from '../../lib/api/services/DashboardService'
import {
  KnowledgeIcon,
  BrainIcon,
  PersonaIcon,
  WarningIcon
} from '../../components/ui/SparkleIcons'

const PIPELINE_STAGES = [
  { name: 'Document Ingestion', status: 'built', module: 'knowledge_hub' },
  { name: 'Universal Structure Builder', status: 'built', module: 'knowledge_hub' },
  { name: 'Embedding + RAG Index', status: 'built', module: 'knowledge_hub' },
  { name: 'Divergence Scanner', status: 'built', module: 'knowledge_hub' },
  { name: 'Master Case Generation', status: 'partial', module: 'knowledge_hub' },
  { name: 'Continuous Loop', status: 'partial', module: 'knowledge_hub' },
  { name: 'KB → Persona Bridge', status: 'in_progress', module: 'integration' },
  { name: 'AI Journalist Extraction', status: 'built', module: 'expert_persona' },
  { name: 'Persona Manifestation', status: 'built', module: 'expert_persona' },
  { name: 'Shadow Mode Review', status: 'built', module: 'expert_persona' },
  { name: 'Skills Layer', status: 'built', module: 'skills' },
  { name: 'Runtime Retrieval + Chat', status: 'planned', module: 'retrieval' },
]

const STATUS_STYLE = {
  built: { bg: '#CAF0F8', color: '#03045E', border: '#90E0EF', label: 'Built' },
  partial: { bg: '#FFFBEB', color: '#D97706', border: '#FDE68A', label: 'Partial' },
  in_progress: { bg: '#EFF6FF', color: '#3B82F6', border: '#BFDBFE', label: 'In Progress' },
  planned: { bg: '#F9FAFB', color: '#9CA3AF', border: '#E5E7EB', label: 'Planned' },
}

const MODULE_COLORS = {
  knowledge_hub: '#0077B6',
  expert_persona: '#03045E',
  integration: '#F59E0B',
  skills: '#00B4D8',
  retrieval: '#90E0EF',
}

export default function DashboardPage() {
  const [health, setHealth] = useState(null)
  const [stats, setStats] = useState(null)

  useEffect(() => {
    DashboardService.getHealth()
      .then(setHealth)
      .catch(() => setHealth({ status: 'offline' }))

    DashboardService.getStats('demo')
      .then(setStats)
      .catch(() => setStats(null))
  }, [])

  const statCards = [
    { label: 'Documents Ingested', value: stats?.documentsIngested ?? '—', color: '#0077B6', bg: '#CAF0F8', border: '#90E0EF', icon: <KnowledgeIcon size={22} /> },
    { label: 'Master Cases', value: stats?.masterCases ?? '—', color: '#03045E', bg: '#CAF0F8', border: '#90E0EF', icon: <BrainIcon size={22} /> },
    { label: 'Persona Manifests', value: stats?.personaManifests ?? '—', color: '#00B4D8', bg: '#CAF0F8', border: '#90E0EF', icon: <PersonaIcon size={22} /> },
    { label: 'Knowledge Gaps Flagged', value: stats?.knowledgeGapsFlagged ?? '—', color: '#EF4444', bg: '#FEF2F2', border: '#FECACA', icon: <WarningIcon size={22} /> },
  ]

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: '#F4F7FB' }}>
      <Sidebar active="/dashboard" />

      <main style={{ flex: 1, padding: '32px 36px', overflow: 'auto' }}>

        {/* Header */}
        <div className="fade-up" style={{ marginBottom: 36 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <h1 style={{ fontSize: 26, fontWeight: 700, marginBottom: 4, color: '#03045E' }}>Expert Digital Twin</h1>
              <p style={{ color: '#475569', fontSize: 14 }}>
                Active Domain: Professional Services · Persona Engine
              </p>
            </div>

          </div>
        </div>

        {/* Stat Cards */}
        <div className="fade-up" style={{
          display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 32
        }}>
          {statCards.map((card, i) => (
            <div key={i} style={{
              background: '#FFFFFF',
              border: '1px solid #E2E8F0',
              borderRadius: '12px',
              padding: '22px 24px',
              position: 'relative',
              overflow: 'hidden',
              transition: 'all 0.2s',
              boxShadow: '0 4px 12px rgba(3, 4, 94, 0.03)',
            }}>
              <div style={{
                width: 44, height: 44, borderRadius: '8px',
                background: card.bg, border: `1px solid ${card.border}`,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                marginBottom: 14,
              }}>{card.icon}</div>
              <div style={{ fontSize: 30, fontWeight: 800, color: card.color, lineHeight: 1 }}>
                {card.value}
              </div>
              <div style={{ fontSize: 13, color: '#475569', marginTop: 6, fontWeight: 500 }}>
                {card.label}
              </div>
            </div>
          ))}
        </div>

        {/* Active Persona Manifest */}
        <div className="fade-up" style={{
          display: 'grid', gridTemplateColumns: '1fr 2fr', gap: 16, marginBottom: 32
        }}>
          <div style={{
            background: '#FFFFFF',
            border: '1px solid #E2E8F0',
            borderRadius: '16px',
            padding: '24px',
            boxShadow: '0 4px 12px rgba(3, 4, 94, 0.03)',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            textAlign: 'center',
            justifyContent: 'center'
          }}>
            <div style={{
              width: 80, height: 80, borderRadius: '50%',
              background: 'linear-gradient(135deg, #7209B7, #3F37C9)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 32, color: '#FFF', marginBottom: 16,
              boxShadow: '0 10px 20px rgba(114, 9, 183, 0.2)'
            }}>✨</div>
            <h3 style={{ fontSize: 18, fontWeight: 700, color: '#03045E', marginBottom: 4 }}>Expert Twin v1.0</h3>
            <p style={{ fontSize: 13, color: '#64748B' }}>Persona Manifest Status: <b>Active</b></p>
          </div>

          <div style={{
            background: '#FFFFFF',
            border: '1px solid #E2E8F0',
            borderRadius: '16px',
            padding: '24px',
            boxShadow: '0 4px 12px rgba(3, 4, 94, 0.03)',
          }}>
            <h2 style={{ fontSize: 16, fontWeight: 700, color: '#03045E', marginBottom: 16 }}>Behavioral Logic Configuration</h2>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              {[
                { label: 'Interaction Philosophy', value: 'Formal & Precise', icon: '🗣️' },
                { label: 'Autonomous Authority', value: 'High (Supervised)', icon: '⚖️' },
                { label: 'Expert Archetype', value: 'The Stoic Sage', icon: '🧠' },
                { label: 'Critical Feedback', value: 'Nuanced Critique', icon: '📝' },
              ].map((t, i) => (
                <div key={i} style={{
                  padding: '12px 16px',
                  borderRadius: '12px',
                  background: '#F8FAFC',
                  border: '1px solid #E2E8F0',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 12
                }}>
                  <span style={{ fontSize: 18 }}>{t.icon}</span>
                  <div>
                    <div style={{ fontSize: 11, color: '#94A3B8', fontWeight: 700, textTransform: 'uppercase' }}>{t.label}</div>
                    <div style={{ fontSize: 13, color: '#03045E', fontWeight: 600 }}>{t.value}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Pipeline Status */}
        <div className="fade-up" style={{
          background: '#FFFFFF',
          border: '1px solid #E2E8F0',
          borderRadius: '16px',
          padding: '28px 30px',
          boxShadow: '0 4px 12px rgba(3, 4, 94, 0.03)',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
            <h2 style={{ fontSize: 17, fontWeight: 700, color: '#03045E' }}>Pipeline Status</h2>
            <span style={{ background: '#CAF0F8', color: '#03045E', padding: '4px 12px', borderRadius: 99, fontSize: 12, fontWeight: 700 }}>12 STAGES</span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16 }}>
            {PIPELINE_STAGES.map((stage, i) => {
              const style = STATUS_STYLE[stage.status]
              return (
                <div key={i} style={{
                  padding: '16px 20px',
                  borderRadius: '12px',
                  background: '#F8FAFC',
                  border: '1px solid #E2E8F0',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between'
                }}>
                  <div>
                    <div style={{ fontSize: 13.5, fontWeight: 600, color: '#03045E', marginBottom: 4 }}>{stage.name}</div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                      <span style={{ width: 6, height: 6, borderRadius: '50%', background: MODULE_COLORS[stage.module] }} />
                      <span style={{ fontSize: 11, color: '#475569', textTransform: 'uppercase', letterSpacing: '0.5px', fontWeight: 600 }}>{stage.module.replace('_', ' ')}</span>
                    </div>
                  </div>
                  <span style={{
                    padding: '4px 10px',
                    borderRadius: '99px',
                    fontSize: 11,
                    fontWeight: 700,
                    background: style.bg,
                    color: style.color,
                    border: `1px solid ${style.border}`,
                    textTransform: 'uppercase'
                  }}>{style.label}</span>
                </div>
              )
            })}
          </div>
        </div>

      </main>
    </div>
  )
}
