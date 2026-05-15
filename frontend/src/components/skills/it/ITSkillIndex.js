'use client';
import ITProjectPredictionPanel from './ITProjectPredictionPanel';

/**
 * ITSkillIndex.js — IT Skills Landing Component
 * ================================================
 * Placeholder component that will render the IT-specific
 * skill cards (Sprint Risk Monitor, Escalation Brief, etc.).
 *
 * Owner: Dev B (IT)
 *
 * TODO: Replace this placeholder with actual skill card grid.
 */

export default function ITSkillIndex() {
  return (
    <div style={{
      padding: '24px',
      background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.05), rgba(139, 92, 246, 0.05))',
      borderRadius: 'var(--radius-md, 18px)',
      border: '1px solid rgba(99, 102, 241, 0.12)',
    }}>
      <h3 style={{
        color: 'var(--text-primary, #03045E)',
        fontSize: '1.1rem',
        fontWeight: 600,
        marginBottom: '8px',
      }}>
        💻 IT / Project Management Skills
      </h3>
      <p style={{
        color: 'var(--text-secondary, #475569)',
        fontSize: '0.875rem',
      }}>
        Sprint Risk Monitor · Escalation Brief · Velocity Tracker
      </p>
      
      <div style={{ marginTop: 24 }}>
        <ITProjectPredictionPanel />
      </div>
    </div>
  );
}
