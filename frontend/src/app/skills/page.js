'use client'
import Sidebar from '../../components/layout/Sidebar'

const SKILLS = [
  {
    id: 'doctor_patient_followup',
    label: 'Patient Follow-Up',
    type: 'functional',
    status: 'implemented',
    base: 'send_notification',
    description: 'Send a follow-up message to a patient in the doctor\'s voice, grounded in clinical history.',
    params: ['patient_name', 'patient_contact', 'topic', 'clinical_summary', 'channel', 'urgency'],
  },
  {
    id: 'doctor_pre_cycle_instructions',
    label: 'Pre-Cycle Instructions',
    type: 'functional',
    status: 'placeholder',
    base: 'send_notification',
    description: 'Send standardized pre-IVF cycle preparation instructions to a patient.',
    params: ['patient_name', 'patient_contact', 'cycle_start_date', 'protocol_type'],
  },
  {
    id: 'doctor_case_escalation',
    label: 'Case Escalation',
    type: 'functional',
    status: 'placeholder',
    base: 'send_notification',
    description: 'Escalate a patient query to the real doctor\'s coordinator. Auto-triggered when confidence < threshold.',
    params: ['query_summary', 'urgency', 'patient_id'],
  },
  {
    id: 'doctor_treatment_summary',
    label: 'Treatment Summary Report',
    type: 'functional',
    status: 'placeholder',
    base: 'draft_text',
    description: 'Generate a structured IVF cycle summary report in the doctor\'s voice.',
    params: ['patient_id', 'cycle_number', 'stimulation_response', 'retrieval_outcome'],
  },
  {
    id: 'doctor_flag_knowledge_gap',
    label: 'Flag Knowledge Gap',
    type: 'functional',
    status: 'placeholder',
    base: 'send_notification',
    description: 'Flag an unanswerable query back to the Knowledge Hub loop for the doctor to resolve.',
    params: ['query', 'context', 'priority'],
  },
  {
    id: 'draft_text',
    label: 'Draft Text',
    type: 'base',
    status: 'implemented',
    base: null,
    description: 'Raw capability: generate a structured text draft (email, report, clinical note).',
    params: ['template', 'subject', 'key_points', 'recipient', 'tone_hint'],
  },
  {
    id: 'send_notification',
    label: 'Send Notification',
    type: 'base',
    status: 'implemented',
    base: null,
    description: 'Raw capability: send a notification through a specified channel (email, SMS, in-app).',
    params: ['channel', 'recipient', 'subject', 'body', 'priority'],
  },
  {
    id: 'search_kb',
    label: 'Search Knowledge Base',
    type: 'base',
    status: 'implemented',
    base: null,
    description: 'Semantic search over the expert\'s Knowledge Hub and Master Cases.',
    params: ['query', 'expert_id', 'top_k', 'min_score'],
  },
]

const STATUS_STYLE = {
  implemented: { bg: '#22c55e15', color: '#22c55e', label: '✓ Implemented' },
  placeholder:  { bg: '#f59e0b15', color: '#f59e0b', label: '○ Placeholder' },
}

export default function SkillsPage() {
  const functional = SKILLS.filter(s => s.type === 'functional')
  const base       = SKILLS.filter(s => s.type === 'base')

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <Sidebar active="/skills" />
      <main style={{ flex: 1, padding: '32px 36px', overflow: 'auto' }}>

        <div className="fade-up" style={{ marginBottom: 28 }}>
          <h1 style={{ fontSize: 22, fontWeight: 700 }}>Skills Registry</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: 13, marginTop: 4 }}>
            Base skills are infrastructure. Functional skills are expert-contextualized executions.
          </p>
        </div>

        {/* Functional Skills */}
        <section className="fade-up" style={{ marginBottom: 32 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
            <h2 style={{ fontSize: 15, fontWeight: 600 }}>Functional Skills</h2>
            <span className="badge badge-teal">Doctor / Healthcare</span>
            <span className="badge badge-amber">5 registered</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {functional.map(skill => (
              <SkillCard key={skill.id} skill={skill} />
            ))}
          </div>
        </section>

        {/* Base Skills */}
        <section className="fade-up">
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
            <h2 style={{ fontSize: 15, fontWeight: 600 }}>Base Skills</h2>
            <span className="badge badge-blue">Infrastructure</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {base.map(skill => (
              <SkillCard key={skill.id} skill={skill} />
            ))}
          </div>
        </section>

      </main>
    </div>
  )
}

function SkillCard({ skill }) {
  const s = STATUS_STYLE[skill.status]
  return (
    <div style={{
      background: 'var(--bg-card)',
      border: '1px solid var(--border)',
      borderRadius: 'var(--radius-md)',
      padding: '16px 20px',
      display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 16,
    }}>
      <div style={{ flex: 1 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
          <span style={{ fontWeight: 600, fontSize: 14 }}>{skill.label}</span>
          <code style={{
            fontSize: 11, color: 'var(--text-muted)',
            background: 'var(--bg-elevated)', padding: '1px 7px', borderRadius: 4,
          }}>
            {skill.id}
          </code>
          {skill.base && (
            <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
              → wraps <code style={{ color: 'var(--accent-teal)' }}>{skill.base}</code>
            </span>
          )}
        </div>
        <p style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 8 }}>
          {skill.description}
        </p>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
          {skill.params.map(p => (
            <code key={p} style={{
              fontSize: 10, color: 'var(--accent-primary)',
              background: 'var(--accent-glow)', padding: '1px 7px',
              borderRadius: 4, border: '1px solid var(--accent-primary)20',
            }}>
              {p}
            </code>
          ))}
        </div>
      </div>
      <span style={{
        padding: '4px 12px', borderRadius: 99,
        background: s.bg, color: s.color,
        fontSize: 11, fontWeight: 600, whiteSpace: 'nowrap',
      }}>
        {s.label}
      </span>
    </div>
  )
}
