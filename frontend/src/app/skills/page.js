'use client'
import Sidebar from '../../components/layout/Sidebar'
import { useState } from 'react'
import SkillSandbox from '../../components/skills/SkillSandbox'
import GuardrailEditor from '../../components/skills/GuardrailEditor'
import ExecutionLogViewer from '../../components/skills/ExecutionLogViewer'

const TABS = [
  { id: 'registry',   label: 'Registry',    icon: '📋' },
  { id: 'sandbox',    label: 'Sandbox',     icon: '🧪' },
  { id: 'guardrails', label: 'Guardrails',  icon: '🛡️' },
  { id: 'audit',      label: 'Audit Log',   icon: '📊' },
]

// ─── Universal Skill Registry Data ─────────────────────────────────────────────
const INITIAL_SKILLS = [
  // Functional Skills (F)
  { 
    id: 'SKL_WEB_SCRAPER', 
    label: 'Real-Time Web Scraper', 
    type: 'functional', 
    status: 'implemented',
    flow: ['Target URL Parsing', 'DOM Feature Extraction', 'JSON Payload Synthesis'],
    description: 'Dynamic live acquisition framework extracting targeted web elements and building structured analytical profiles.', 
    params: ['target_url', 'extraction_depth', 'allowed_domains'], 
    composes: ['HTTP_CRAWLER', 'DOM_PARSER'] 
  },
  { 
    id: 'SKL_COMPLIANCE_GATEKEEPER', 
    label: 'Compliance Gatekeeper', 
    type: 'functional', 
    status: 'implemented',
    flow: ['Artifact Audit', 'Metrics Extraction', 'Approval Verdict'],
    description: 'Multi-step compliance readiness verification ensuring prerequisites meet stringent organizational safety baselines.', 
    params: ['client_id', 'target_date', 'required_documents'], 
    composes: ['ACT_CHECKLIST_VERIFY', 'ACT_DOCUMENT_OCR'] 
  },
  { 
    id: 'SKL_EXPERT_SYNTHESIS', 
    label: 'Expert Brief Synthesis', 
    type: 'functional', 
    status: 'implemented',
    flow: ['Stream Aggregation', 'Brief Formatting', 'Conditional Dispatch'],
    description: 'Autonomous data consolidation orchestrating dynamic summaries and securely relaying targeted dispatches.', 
    params: ['client_id', 'data_sources', 'release_approved'], 
    composes: ['KNW_METRIC_SYNTHESIS', 'send_communication'] 
  },
  { 
    id: 'SKL_BASELINE_VIGILANCE', 
    label: 'Baseline Vigilance', 
    type: 'functional', 
    status: 'implemented',
    flow: ['Metrics Ingestion', 'Historical Comparison', 'Anomaly Detection'],
    description: 'Extract operational metrics continuously to compare against primary historical baselines for breach detection.', 
    params: ['client_id', 'baseline_thresholds', 'source_url'], 
    composes: ['ACT_DOCUMENT_OCR'] 
  },

  // Base Skills (B)
  { 
    id: 'book_appointment', 
    label: 'Schedule Session', 
    type: 'base', 
    status: 'implemented',
    description: 'Book an authorized appointment block via unified calendar API gateways.', 
    params: ['client_id', 'appointment_time', 'reason_code'] 
  },
  { 
    id: 'send_communication', 
    label: 'Secure Dispatch', 
    type: 'base', 
    status: 'implemented',
    description: 'Transmit encrypted notifications via integrated external messaging providers.', 
    params: ['template_id', 'recipient_address', 'dynamic_vars'] 
  },
  { 
    id: 'ACT_DOCUMENT_OCR', 
    label: 'Document Parsing OCR', 
    type: 'base', 
    status: 'implemented',
    description: 'Extract highly accurate text structures and tabular arrays from complex source graphics.', 
    params: ['image_url', 'extraction_type'] 
  },
  { 
    id: 'KNW_METRIC_SYNTHESIS', 
    label: 'Metric Aggregation', 
    type: 'base', 
    status: 'implemented',
    description: 'Consolidate distributed multi-stream parameters into structured JSON data models.', 
    params: ['client_id', 'data_sources'] 
  },
  { 
    id: 'ACT_CHECKLIST_VERIFY', 
    label: 'Artifact Verification', 
    type: 'base', 
    status: 'implemented',
    description: 'Audit uploaded materials systematically for strict presence and logical completeness.', 
    params: ['client_id', 'required_documents'] 
  },
]

export default function SkillsPage() {
  const [activeTab, setActiveTab] = useState('registry')
  
  // Track toggle states for each skill dynamically
  const [skillStates, setSkillStates] = useState(() => {
    const initial = {}
    INITIAL_SKILLS.forEach(s => {
      initial[s.id] = true // default all to ON
    })
    return initial
  })

  const toggleSkillState = (id, newState) => {
    setSkillStates(prev => ({
      ...prev,
      [id]: newState
    }))
  }

  const baseSkills = INITIAL_SKILLS.filter(s => s.type === 'base')
  const functionalSkills = INITIAL_SKILLS.filter(s => s.type === 'functional')

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: '#F4F7FB' }}>
      <Sidebar active="/skills" />
      <main style={{ flex: 1, padding: '32px 36px', overflow: 'auto' }}>

        {/* Header */}
        <div className="fade-up" style={{ marginBottom: 28 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <h1 style={{ fontSize: 24, fontWeight: 700, color: '#03045E' }}>Skills Enablement Pillar</h1>
              <p style={{ color: '#475569', fontSize: 13.5, marginTop: 4 }}>
                Base Skills (B) are atomic primitives. Functional Skills (F) orchestrate Base Skills into dynamic workflows with toggleable execution gates.
              </p>
            </div>
            <div style={{ display: 'flex', gap: 8 }}>
              <span className="badge" style={{ background: '#CAF0F8', color: '#03045E', fontWeight: 700, padding: '6px 12px', fontSize: 12 }}>
                {baseSkills.length} Base Primitives
              </span>
              <span className="badge" style={{ background: '#D1FAE5', color: '#065F46', fontWeight: 700, padding: '6px 12px', fontSize: 12 }}>
                {functionalSkills.length} Orchestrations
              </span>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="fade-up" style={{
          display: 'flex', gap: 4, marginBottom: 24,
          borderBottom: '1px solid #E2E8F0', paddingBottom: 0,
        }}>
          {TABS.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                padding: '12px 20px',
                border: 'none',
                background: activeTab === tab.id ? '#FFFFFF' : 'transparent',
                borderBottom: activeTab === tab.id ? '2px solid #0077B6' : '2px solid transparent',
                color: activeTab === tab.id ? '#0077B6' : '#64748B',
                fontWeight: activeTab === tab.id ? 700 : 500,
                fontSize: 13.5, cursor: 'pointer',
                transition: 'all 0.2s',
                borderRadius: '8px 8px 0 0',
                display: 'flex', alignItems: 'center', gap: 8,
                boxShadow: activeTab === tab.id ? '0 -2px 8px rgba(0,0,0,0.02)' : 'none'
              }}
            >
              <span style={{ fontSize: 16 }}>{tab.icon}</span> {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div className="fade-up">
          {/* Registry Tab */}
          {activeTab === 'registry' && (
            <div>
              {/* Functional Skills */}
              <section style={{ marginBottom: 36 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 18 }}>
                  <h2 style={{ fontSize: 16, fontWeight: 700, color: '#03045E' }}>Functional Skills (F)</h2>
                  <span className="badge" style={{ background: '#E0F2FE', color: '#0369A1', fontSize: 11, fontWeight: 600 }}>Composite Orchestrations</span>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                  {functionalSkills.map(skill => (
                    <SkillCard 
                      key={skill.id} 
                      skill={skill} 
                      isActive={skillStates[skill.id]} 
                      onToggle={(state) => toggleSkillState(skill.id, state)} 
                    />
                  ))}
                </div>
              </section>

              {/* Base Skills */}
              <section>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 18 }}>
                  <h2 style={{ fontSize: 16, fontWeight: 700, color: '#03045E' }}>Base Skills (B)</h2>
                  <span className="badge" style={{ background: '#F1F5F9', color: '#475569', fontSize: 11, fontWeight: 600 }}>Atomic Primitives</span>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                  {baseSkills.map(skill => (
                    <SkillCard 
                      key={skill.id} 
                      skill={skill} 
                      isActive={skillStates[skill.id]} 
                      onToggle={(state) => toggleSkillState(skill.id, state)} 
                    />
                  ))}
                </div>
              </section>
            </div>
          )}

          {/* Sandbox Tab */}
          {activeTab === 'sandbox' && (
            <div style={{ background: '#FFFFFF', padding: 24, borderRadius: 16, border: '1px solid #E2E8F0' }}>
              <div style={{ marginBottom: 16 }}>
                <h2 style={{ fontSize: 16, fontWeight: 700, color: '#03045E', marginBottom: 4 }}>Skill Sandbox Payload Runner</h2>
                <p style={{ color: '#64748B', fontSize: 12.5 }}>
                  Test skill execution safely with direct input simulation. Select a registered skill, input parameters, and trigger real-time evaluation.
                </p>
              </div>
              <SkillSandbox />
            </div>
          )}

          {/* Guardrails Tab */}
          {activeTab === 'guardrails' && (
            <div style={{ background: '#FFFFFF', padding: 24, borderRadius: 16, border: '1px solid #E2E8F0' }}>
              <div style={{ marginBottom: 16 }}>
                <h2 style={{ fontSize: 16, fontWeight: 700, color: '#03045E', marginBottom: 4 }}>Global Guardrail Gatekeeper</h2>
                <p style={{ color: '#64748B', fontSize: 12.5 }}>
                  Administer platform-wide restrictions. Disabled boundaries immediately prevent autonomous API dispatch.
                </p>
              </div>
              <GuardrailEditor />
            </div>
          )}

          {/* Audit Log Tab */}
          {activeTab === 'audit' && (
            <div style={{ background: '#FFFFFF', padding: 24, borderRadius: 16, border: '1px solid #E2E8F0' }}>
              <div style={{ marginBottom: 16 }}>
                <h2 style={{ fontSize: 16, fontWeight: 700, color: '#03045E', marginBottom: 4 }}>Autonomous Execution Telemetry</h2>
                <p style={{ color: '#64748B', fontSize: 12.5 }}>
                  Immutable event stream logging tool execution parameters, timestamps, and return codes automatically.
                </p>
              </div>
              <ExecutionLogViewer />
            </div>
          )}
        </div>

      </main>
    </div>
  )
}

// ─── Universal Interactive Skill Card Component ─────────────────────────────────────────────
function SkillCard({ skill, isActive, onToggle }) {
  return (
    <div style={{
      background: isActive ? '#FFFFFF' : '#FAFAFA',
      border: `1px solid ${isActive ? '#E2E8F0' : '#E5E7EB'}`,
      borderRadius: '14px',
      padding: '20px 24px',
      display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 20,
      boxShadow: isActive ? '0 4px 16px rgba(3, 4, 94, 0.04)' : 'none',
      transition: 'all 0.25s cubic-bezier(0.4, 0, 0.2, 1)',
      opacity: isActive ? 1 : 0.75,
      position: 'relative',
      overflow: 'hidden'
    }}>
      {/* Accent pill indicator strip on left border */}
      <div style={{
        position: 'absolute',
        left: 0, top: 0, bottom: 0, width: 4,
        background: isActive ? (skill.type === 'functional' ? '#0EA5E9' : '#0077B6') : '#CBD5E1',
        transition: 'background 0.2s'
      }} />

      <div style={{ flex: 1, marginLeft: 6 }}>
        {/* Top line: Name, Code, Status badge */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8 }}>
          <span style={{ fontWeight: 700, fontSize: 15.5, color: isActive ? '#03045E' : '#64748B' }}>
            {skill.label}
          </span>
          <code style={{
            fontSize: 11, color: '#475569', fontWeight: 600,
            background: '#F1F5F9', padding: '2px 8px', borderRadius: 6,
            border: '1px solid #E2E8F0'
          }}>
            {skill.id}
          </code>
          <span className={`badge ${isActive ? 'badge-green' : 'badge-slate'}`} style={{ fontSize: 10, padding: '2px 8px' }}>
            {isActive ? '● ENABLED' : '○ MUTED'}
          </span>
        </div>

        {/* Small description */}
        <p style={{ fontSize: 13, color: '#475569', marginBottom: 12, lineHeight: 1.5, maxWidth: '92%' }}>
          {skill.description}
        </p>

        {/* Flow below the name of the skills */}
        {skill.flow && (
          <div style={{ 
            display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: 6, 
            marginBottom: 12, padding: '6px 12px', background: '#F8FAFC', 
            borderRadius: 8, border: '1px solid #F1F5F9', width: 'fit-content'
          }}>
            <span style={{ fontSize: 11, fontWeight: 700, color: '#0284C7', textTransform: 'uppercase', letterSpacing: '0.5px', marginRight: 4 }}>
              Execution Flow:
            </span>
            {skill.flow.map((step, idx) => (
              <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <span style={{ 
                  fontSize: 11.5, fontWeight: 600, color: '#0F172A', 
                  background: '#FFFFFF', padding: '2px 8px', borderRadius: 4,
                  boxShadow: '0 1px 2px rgba(0,0,0,0.04)', border: '1px solid #E2E8F0'
                }}>
                  {step}
                </span>
                {idx < skill.flow.length - 1 && (
                  <span style={{ color: '#94A3B8', fontWeight: 700, fontSize: 12 }}>→</span>
                )}
              </div>
            ))}
          </div>
        )}

      </div>

      {/* On / Off Button Toggle Switch area */}
      <div style={{ 
        display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 8, flexShrink: 0 
      }}>
        <span style={{ fontSize: 10.5, fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
          Skill State
        </span>
        
        {/* Button pill selector group where clicking anywhere toggles the state */}
        <div 
          onClick={() => onToggle(!isActive)}
          style={{
            display: 'flex',
            background: '#F1F5F9',
            padding: 3,
            borderRadius: '10px',
            border: '1px solid #E2E8F0',
            cursor: 'pointer',
            userSelect: 'none'
          }}
          title="Click anywhere to toggle state"
        >
          <div
            style={{
              padding: '6px 14px',
              background: isActive ? '#10B981' : 'transparent',
              color: isActive ? '#FFFFFF' : '#64748B',
              fontWeight: 700,
              fontSize: 12,
              borderRadius: '8px',
              transition: 'all 0.2s',
              boxShadow: isActive ? '0 2px 6px rgba(16, 185, 129, 0.25)' : 'none',
              pointerEvents: 'none'
            }}
          >
            ON
          </div>
          <div
            style={{
              padding: '6px 14px',
              background: !isActive ? '#EF4444' : 'transparent',
              color: !isActive ? '#FFFFFF' : '#64748B',
              fontWeight: 700,
              fontSize: 12,
              borderRadius: '8px',
              transition: 'all 0.2s',
              boxShadow: !isActive ? '0 2px 6px rgba(239, 68, 68, 0.25)' : 'none',
              pointerEvents: 'none'
            }}
          >
            OFF
          </div>
        </div>
      </div>
    </div>
  )
}
