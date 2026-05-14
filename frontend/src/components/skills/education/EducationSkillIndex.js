'use client';

/**
 * EducationSkillIndex.js — Education Skills Landing Component
 * =============================================================
 * Placeholder component that will render the Education-specific
 * skill cards (Mastery Check, Learning Gap Detector, etc.).
 *
 * Owner: Dev C (Education)
 *
 * TODO: Replace this placeholder with actual skill card grid.
 */

export default function EducationSkillIndex() {
  return (
    <div style={{
      padding: '24px',
      background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.05), rgba(52, 211, 153, 0.05))',
      borderRadius: 'var(--radius-md, 18px)',
      border: '1px solid rgba(16, 185, 129, 0.12)',
    }}>
      <h3 style={{
        color: 'var(--text-primary, #03045E)',
        fontSize: '1.1rem',
        fontWeight: 600,
        marginBottom: '8px',
      }}>
        🎓 Education Skills
      </h3>
      <p style={{
        color: 'var(--text-secondary, #475569)',
        fontSize: '0.875rem',
      }}>
        Mastery Check · Learning Gap Detector · Progress Tracker
      </p>
      {/* TODO: Dev C — Render skill cards here */}
    </div>
  );
}
