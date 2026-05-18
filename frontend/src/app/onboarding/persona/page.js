'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import SuccessOverlay from '../../../components/ui/SuccessOverlay'

const PERSONA_QUESTIONS = [
  {
    id: 1,
    question: "Interaction Philosophy: How should your Twin interact with users?",
    placeholder: "e.g., Use formal and precise language, focus on data-heavy responses..."
  },
  {
    id: 2,
    question: "Autonomous Authority: Describe your Digital Twin's level of autonomy.",
    placeholder: "e.g., Supervise all actions but allow high autonomy in low-risk reporting..."
  },
  {
    id: 3,
    question: "Expert Archetype: Which defines your professional digital presence?",
    placeholder: "e.g., The Stoic Analyst, calm under pressure and deeply collaborative..."
  },
  {
    id: 4,
    question: "Critical Feedback: How should the Twin deliver corrections?",
    placeholder: "e.g., Direct and factual, or gentle corrective guidance as a mentor..."
  }
]

export default function PersonaCreationPage() {
  const router = useRouter()
  const [answers, setAnswers] = useState({})
  const [isRecording, setIsRecording] = useState(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isSuccess, setIsSuccess] = useState(false)

  const handleInputChange = (questionId, value) => {
    setAnswers({ ...answers, [questionId]: value })
  }

  const toggleRecording = (questionId) => {
    if (isRecording === questionId) {
      setIsRecording(null)
    } else {
      setIsRecording(questionId)
      // UI Only: Simulate recording start
    }
  }

  const handleSubmit = () => {
    setIsSubmitting(true)
    setTimeout(() => {
      setIsSubmitting(false)
      setIsSuccess(true)
    }, 1500)
  }

  return (
    <div className="fade-up" style={{ height: 'calc(100vh - 100px)', display: 'flex', flexDirection: 'column' }}>
      {/* Stepper Indicator */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 20, justifyContent: 'center', flexShrink: 0 }}>
        {[1, 2, 3, 4, 5].map(s => (
          <div key={s} style={{
            width: 32, height: 4, borderRadius: 2,
            background: s === 5 ? '#0077B6' : s < 5 ? '#0077B6' : '#E2E8F0'
          }} />
        ))}
      </div>

      {isSuccess ? (
        <SuccessOverlay />
      ) : (
        <div style={{
          background: '#FFFFFF',
          borderRadius: 24,
          border: '1px solid #E2E8F0',
          boxShadow: '0 20px 50px rgba(3, 4, 94, 0.05)',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
          flex: 1
        }}>
          {/* FIXED HEADER */}
        <div style={{ padding: '24px 32px', borderBottom: '1px solid #F1F5F9', textAlign: 'center', flexShrink: 0 }}>
          <div style={{ fontSize: 32, marginBottom: 8 }}>✨</div>
          <h1 style={{ fontSize: 24, fontWeight: 800, color: '#03045E', marginBottom: 4 }}>
            Persona Initialization
          </h1>
          <p style={{ color: '#64748B', fontSize: 14 }}>
            Define the unique voice and behavioral logic of your Expert Twin via text or voice.
          </p>
        </div>

        {/* SCROLLABLE CONTENT */}
        <div style={{ 
          flex: 1, 
          overflowY: 'auto', 
          padding: '24px 32px',
          display: 'flex', 
          flexDirection: 'column', 
          gap: 24,
          background: '#FDFEFE'
        }}>
          {PERSONA_QUESTIONS.map((q, idx) => (
            <div key={q.id} style={{
              padding: '20px',
              borderRadius: '16px',
              background: '#FFFFFF',
              border: '1px solid #E2E8F0',
              boxShadow: '0 2px 8px rgba(0,0,0,0.02)'
            }}>
              <div style={{ display: 'flex', gap: 10, marginBottom: 16 }}>
                <span style={{ 
                  width: 24, height: 24, borderRadius: '50%', background: 'linear-gradient(135deg, #7209B7, #3F37C9)', 
                  color: '#FFF', fontSize: 12, fontWeight: 700, display: 'flex', 
                  alignItems: 'center', justifyContent: 'center', flexShrink: 0
                }}>
                  {idx + 1}
                </span>
                <h2 style={{ fontSize: 15, fontWeight: 700, color: '#03045E', lineHeight: 1.4 }}>
                  {q.question}
                </h2>
              </div>

              <div style={{ display: 'flex', gap: 12, alignItems: 'flex-start' }}>
                <textarea 
                  placeholder={q.placeholder}
                  value={answers[q.id] || ''}
                  onChange={(e) => handleInputChange(q.id, e.target.value)}
                  style={{
                    flex: 1,
                    minHeight: '80px',
                    padding: '12px 16px',
                    borderRadius: '12px',
                    border: '1px solid #E2E8F0',
                    fontSize: 14,
                    fontFamily: 'inherit',
                    resize: 'none',
                    background: '#F8FAFC',
                    transition: 'border-color 0.2s ease',
                    outline: 'none'
                  }}
                  onFocus={(e) => e.target.style.borderColor = '#7209B7'}
                  onBlur={(e) => e.target.style.borderColor = '#E2E8F0'}
                />
                
                <button 
                  onClick={() => toggleRecording(q.id)}
                  style={{
                    width: 48,
                    height: 48,
                    borderRadius: '12px',
                    background: isRecording === q.id ? '#EF4444' : '#F1F5F9',
                    border: 'none',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    transition: 'all 0.2s ease',
                    flexShrink: 0
                  }}
                  title={isRecording === q.id ? "Stop Recording" : "Record Answer"}
                >
                  <span style={{ 
                    fontSize: 20, 
                    color: isRecording === q.id ? '#FFF' : '#64748B',
                    animation: isRecording === q.id ? 'pulse 1.5s infinite' : 'none'
                  }}>
                    {isRecording === q.id ? '⏹' : '🎤'}
                  </span>
                </button>
              </div>
              
              {isRecording === q.id && (
                <div style={{ marginTop: 16, display: 'flex', flexDirection: 'column', gap: 10 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                    <div style={{ width: 8, height: 8, borderRadius: '50%', background: '#EF4444' }} className="pulse" />
                    <span style={{ fontSize: 13, color: '#EF4444', fontWeight: 700, letterSpacing: '0.02em' }}>
                      CAPTURING EXPERT VOICE...
                    </span>
                  </div>
                  
                  {/* Voice Wave Animation (High-End GIF Style) */}
                  <div style={{ 
                    display: 'flex', 
                    alignItems: 'flex-end', 
                    gap: 3, 
                    height: 32, 
                    padding: '0 10px',
                    background: 'rgba(239, 68, 68, 0.05)',
                    borderRadius: '8px',
                    width: 'fit-content'
                  }}>
                    {[...Array(12)].map((_, i) => (
                      <div key={i} style={{
                        width: 3,
                        background: '#EF4444',
                        borderRadius: '3px',
                        animation: `wave-grow 1s ease-in-out infinite ${i * 0.1}s`,
                        height: '20%'
                      }} />
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* FIXED FOOTER */}
        <div style={{ padding: '24px 32px', borderTop: '1px solid #F1F5F9', flexShrink: 0 }}>
          <div style={{ display: 'flex', gap: 12 }}>
            <button 
              onClick={() => router.push('/onboarding/interview')}
              style={{
                flex: 1,
                padding: '16px',
                borderRadius: '12px',
                background: '#F1F5F9',
                color: '#475569',
                fontWeight: 700,
                border: '1px solid #E2E8F0',
                cursor: 'pointer',
                fontSize: 14
              }}
            >
              Back
            </button>
            <button 
              onClick={handleSubmit}
              style={{
                flex: 2,
                padding: '16px',
                borderRadius: '12px',
                background: 'linear-gradient(135deg, #7209B7, #3F37C9)',
                color: '#FFF',
                fontWeight: 700,
                border: 'none',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                boxShadow: '0 10px 25px rgba(114, 9, 183, 0.25)',
                fontSize: 14
              }}
            >
              {isSubmitting ? 'Generating Twin Persona...' : 'Finalize Onboarding'}
            </button>
          </div>
        </div>
      </div>
      )}

      {/* Bypass Link */}
      {!isSuccess && (
        <div style={{ marginTop: 12, textAlign: 'center', flexShrink: 0 }}>
          <button 
            onClick={() => router.push('/dashboard')}
            style={{ background: 'none', border: 'none', color: '#94A3B8', fontSize: 11, cursor: 'pointer', textDecoration: 'underline' }}
          >
            Skip to Dashboard (Preview)
          </button>
        </div>
      )}
      <style jsx global>{`
        @keyframes wave-grow {
          0%, 100% { height: 20%; }
          50% { height: 100%; }
        }
      `}</style>
    </div>
  )
}
