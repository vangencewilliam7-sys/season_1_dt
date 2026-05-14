'use client';

/**
 * HealthcareSkillIndex.js — Healthcare Skills Landing Component
 * ==============================================================
 * Placeholder component that will render the Healthcare-specific
 * skill cards (Pre-Op Gatekeeper, Expert Synthesis, Baseline Vigilance).
 *
 * Owner: Dev A (Healthcare)
 *
 * TODO: Replace this placeholder with actual skill card grid.
 */

export default function HealthcareSkillIndex() {
  return (
    <div style={{
      padding: '24px',
      background: 'linear-gradient(135deg, rgba(0, 119, 182, 0.05), rgba(0, 180, 216, 0.05))',
      borderRadius: 'var(--radius-md, 18px)',
      border: '1px solid rgba(0, 119, 182, 0.12)',
    }}>
      <h3 style={{
        color: 'var(--text-primary, #03045E)',
        fontSize: '1.1rem',
        fontWeight: 600,
        marginBottom: '8px',
      }}>
        🏥 Healthcare Skills
      </h3>
      <p style={{
        color: 'var(--text-secondary, #475569)',
        fontSize: '0.875rem',
      }}>
        Pre-Op Gatekeeper · Expert Synthesis · Baseline Vigilance
      </p>
      {/* TODO: Dev A — Render skill cards here */}
    </div>
  );
}
