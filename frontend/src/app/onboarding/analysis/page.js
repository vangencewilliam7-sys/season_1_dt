'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'

export default function CrossAnalysisPage() {
  const router = useRouter()
  const [stage, setStage] = useState(0)

  const stages = [
    "Scanning Knowledge Fragments...",
    "Indexing Case Patterns...",
    "Comparing Guidelines vs. Reality...",
    "Identifying Expert Intuition Gaps...",
    "Finalizing Tacit Strategy..."
  ]

  useEffect(() => {
    if (stage < stages.length) {
      const timer = setTimeout(() => setStage(stage + 1), 1800)
      return () => clearTimeout(timer)
    } else {
      const timer = setTimeout(() => router.push('/onboarding/interview'), 1500)
      return () => clearTimeout(timer)
    }
  }, [stage])

  return (
    <div className="fade-up">
      {/* Stepper Indicator */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 32, justifyContent: 'center' }}>
        {[1, 2, 3, 4, 5].map(s => (
          <div key={s} style={{
            width: 32, height: 4, borderRadius: 2,
            background: s === 3 ? '#0077B6' : s < 3 ? '#0077B6' : '#E2E8F0'
          }} />
        ))}
      </div>

      <div style={{
        background: '#FFFFFF',
        borderRadius: 24,
        padding: '60px 48px',
        border: '1px solid #E2E8F0',
        boxShadow: '0 20px 50px rgba(3, 4, 94, 0.05)',
        textAlign: 'center',
        position: 'relative',
        overflow: 'hidden'
      }}>
        {/* Background Animation Effect */}
        <div style={{
          position: 'absolute',
          top: '-50%',
          left: '-50%',
          width: '200%',
          height: '200%',
          background: 'radial-gradient(circle at center, rgba(0, 180, 216, 0.05) 0%, transparent 70%)',
          animation: 'rotate 10s linear infinite'
        }} />

        <div style={{ position: 'relative', zIndex: 1 }}>
          <div style={{
            width: 120,
            height: 120,
            borderRadius: '50%',
            background: 'linear-gradient(135deg, #03045E 0%, #0077B6 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 40px',
            boxShadow: '0 0 40px rgba(0, 119, 182, 0.4)',
            fontSize: 48
          }} className="float">
            🧬
          </div>

          <h1 style={{ fontSize: 28, fontWeight: 800, color: '#03045E', marginBottom: 12 }}>
            Synthesizing Your Twin
          </h1>
          <p style={{ color: '#64748B', fontSize: 16, marginBottom: 48 }}>
            The system is cross-referencing your documents with your master cases to find unique decision logic.
          </p>

          <div style={{ maxWidth: 400, margin: '0 auto' }}>
            {stages.map((text, i) => (
              <div key={i} style={{
                display: 'flex',
                alignItems: 'center',
                gap: 16,
                padding: '14px 0',
                borderBottom: i === stages.length - 1 ? 'none' : '1px solid #F1F5F9',
                opacity: stage > i ? 0.4 : stage === i ? 1 : 0.2,
                transition: 'all 0.5s ease',
                transform: stage === i ? 'translateX(10px)' : 'none'
              }}>
                <div style={{
                  width: 20, height: 20, borderRadius: '50%',
                  border: `2px solid ${stage > i ? '#0077B6' : stage === i ? '#0077B6' : '#CBD5E1'}`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  background: stage > i ? '#0077B6' : 'transparent'
                }}>
                  {stage > i && <span style={{ color: '#FFF', fontSize: 10 }}>✓</span>}
                  {stage === i && <div style={{ width: 8, height: 8, borderRadius: '50%', background: '#0077B6' }} className="pulse" />}
                </div>
                <span style={{ 
                  fontSize: 14, 
                  fontWeight: stage === i ? 700 : 500,
                  color: stage === i ? '#03045E' : '#64748B'
                }}>
                  {text}
                </span>
              </div>
            ))}
          </div>

          <div style={{ marginTop: 48, display: 'flex', gap: 12, justifyContent: 'center' }}>
            <button 
              onClick={() => router.push('/onboarding/cases')}
              style={{
                width: '100%',
                padding: '18px',
                borderRadius: '14px',
                background: '#F1F5F9',
                color: '#475569',
                fontWeight: 700,
                border: '1px solid #E2E8F0',
                cursor: 'pointer',
                fontSize: 15
              }}
            >
              Back to Cases
            </button>
          </div>
        </div>
      </div>

      {/* Bypass Link */}
      <div style={{ marginTop: 24, textAlign: 'center' }}>
        <button 
          onClick={() => router.push('/onboarding/interview')}
          style={{ background: 'none', border: 'none', color: '#94A3B8', fontSize: 12, cursor: 'pointer', textDecoration: 'underline' }}
        >
          Skip to Step 4 (Preview)
        </button>
      </div>
    </div>
  )
}
