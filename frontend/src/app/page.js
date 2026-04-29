'use client'
import Sidebar from '../components/layout/Sidebar'
import { useState, useEffect } from 'react'

const PIPELINE_STAGES = [
  { name: 'Document Ingestion',          status: 'built',       module: 'knowledge_hub'    },
  { name: 'Universal Structure Builder', status: 'built',       module: 'knowledge_hub'    },
  { name: 'Embedding + RAG Index',       status: 'built',       module: 'knowledge_hub'    },
  { name: 'Divergence Scanner',          status: 'built',       module: 'knowledge_hub'    },
  { name: 'Master Case Generation',      status: 'partial',     module: 'knowledge_hub'    },
  { name: 'Continuous Loop',             status: 'partial',     module: 'knowledge_hub'    },
  { name: 'KB → Persona Bridge',         status: 'in_progress', module: 'integration'      },
  { name: 'AI Journalist Extraction',    status: 'built',       module: 'expert_persona'   },
  { name: 'Persona Manifestation',       status: 'built',       module: 'expert_persona'   },
  { name: 'Shadow Mode Review',          status: 'built',       module: 'expert_persona'   },
  { name: 'Skills Layer',                status: 'in_progress', module: 'skills'           },
  { name: 'Runtime Retrieval + Chat',    status: 'planned',     module: 'retrieval'        },
]

const STATUS_STYLE = {
  built:       { bg: '#22c55e15', color: '#22c55e', label: 'Built' },
  partial:     { bg: '#f59e0b15', color: '#f59e0b', label: 'Partial' },
  in_progress: { bg: '#3b82f615', color: '#3b82f6', label: 'In Progress' },
  planned:     { bg: '#94a3b815', color: '#94a3b8', label: 'Planned' },
}

const MODULE_COLORS = {
  knowledge_hub:   '#14b8a6',
  expert_persona:  '#3b82f6',
  integration:     '#f59e0b',
  skills:          '#a855f7',
  retrieval:       '#ec4899',
}

export default function DashboardPage() {
  const [health, setHealth] = useState(null)
  const [stats, setStats]   = useState(null)

  useEffect(() => {
    // Backend health check
    fetch('http://127.0.0.1:8000/health')
      .then(r => r.json())
      .then(setHealth)
      .catch(() => setHealth({ status: 'offline' }))

    // Real DB stats via Python Backend → Supabase
    fetch('http://127.0.0.1:8000/api/stats')
      .then(r => r.json())
      .then(setStats)
      .catch(() => setStats(null))
  }, [])

  // Stat cards — values populated from DB once loaded
  const statCards = [
    { label: 'Documents Ingested',     value: stats?.documentsIngested    ?? '—', color: 'var(--accent-primary)', icon: '⬡' },
    { label: 'Master Cases',           value: stats?.masterCases           ?? '—', color: 'var(--accent-teal)',    icon: '◎' },
    { label: 'Persona Manifests',      value: stats?.personaManifests      ?? '—', color: 'var(--accent-amber)',   icon: '◈' },
    { label: 'Knowledge Gaps Flagged', value: stats?.knowledgeGapsFlagged  ?? '—', color: 'var(--accent-red)',     icon: '⚠' },
  ]

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <Sidebar active="/" />

      <main style={{ flex: 1, padding: '32px 36px', overflow: 'auto' }}>

        {/* Header */}
        <div className="fade-up" style={{ marginBottom: 36 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <h1 style={{ fontSize: 26, fontWeight: 700, marginBottom: 4 }}>Doctor Digital Twin</h1>
              <p style={{ color: 'var(--text-secondary)', fontSize: 14 }}>
                Fertility Specialist · Knowledge Hub + Persona Engine · Season 1
              </p>
            </div>
            <div style={{
              display: 'flex', alignItems: 'center', gap: 8,
              padding: '8px 16px',
              borderRadius: 'var(--radius-md)',
              border: '1px solid var(--border)',
              background: health?.status === 'healthy' ? '#22c55e10' : '#ef444410',
              fontSize: 13,
              color: health?.status === 'healthy' ? 'var(--accent-green)' : 'var(--accent-red)',
            }}>
              <span style={{
                width: 7, height: 7, borderRadius: '50%',
                background: health?.status === 'healthy' ? 'var(--accent-green)' : 'var(--accent-red)',
                display: 'inline-block',
                animation: 'blink 2s ease infinite',
              }}/>
              {health?.status === 'healthy' ? `Backend online · ${health.active_domain}` : 'Backend offline'}
            </div>
          </div>
        </div>

        {/* Stat Cards — live from Prisma/Supabase */}
        <div className="fade-up" style={{
          display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 32
        }}>
          {statCards.map((card, i) => (
            <div key={i} style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border)',
              borderRadius: 'var(--radius-md)',
              padding: '20px 22px',
              position: 'relative',
              overflow: 'hidden',
              transition: 'border-color 0.2s',
            }}>
              <div style={{
                position: 'absolute', top: 0, left: 0, right: 0, height: 3,
                background: card.color, borderRadius: '12px 12px 0 0'
              }}/>
              <div style={{ fontSize: 20, marginBottom: 10 }}>{card.icon}</div>
              <div style={{ fontSize: 28, fontWeight: 700, color: card.color, lineHeight: 1 }}>
                {card.value}
              </div>
              <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 4 }}>
                {card.label}
              </div>
            </div>
          ))}
        </div>

        {/* Pipeline Status */}
        <div className="fade-up" style={{
          background: 'var(--bg-card)',
          border: '1px solid var(--border)',
          borderRadius: 'var(--radius-lg)',
          padding: '24px 28px',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
            <h2 style={{ fontSize: 16, fontWeight: 600 }}>Pipeline Status</h2>
            <span className="badge badge-blue">12 stages</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {PIPELINE_STAGES.map((stage, i) => {
              const s = STATUS_STYLE[stage.status]
              const moduleColor = MODULE_COLORS[stage.module]
              return (
                <div key={i} style={{
                  display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                  padding: '10px 14px',
                  borderRadius: 'var(--radius-sm)',
                  background: 'var(--bg-elevated)',
                  border: '1px solid var(--border)',
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                    <span style={{
                      width: 8, height: 8, borderRadius: '50%',
                      background: moduleColor, flexShrink: 0,
                    }}/>
                    <span style={{ fontSize: 13 }}>{stage.name}</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span style={{
                      fontSize: 10, color: moduleColor, fontWeight: 600,
                      textTransform: 'uppercase', letterSpacing: '0.05em',
                    }}>
                      {stage.module.replace('_', ' ')}
                    </span>
                    <span style={{
                      padding: '2px 10px', borderRadius: 99,
                      background: s.bg, color: s.color,
                      fontSize: 11, fontWeight: 600,
                    }}>
                      {s.label}
                    </span>
                  </div>
                </div>
              )
            })}
          </div>
        </div>

      </main>
    </div>
  )
}
