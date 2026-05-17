'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { OnboardingService } from '../../../lib/api/services/OnboardingService'

// No local dummy questions. Fetching strictly from backend.

export default function TacitExtractionPage() {
  const router = useRouter()
  const [questions, setQuestions] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [answers, setAnswers] = useState({})
  const [isSubmitting, setIsSubmitting] = useState(false)

  useEffect(() => {
    OnboardingService.getInterviewQuestions()
      .then(data => {
        if (data && Array.isArray(data)) {
          setQuestions(data)
        }
      })
      .catch(err => console.error("Failed to fetch questions:", err))
      .finally(() => setIsLoading(false))
  }, [])

  const handleSelect = (questionId, option) => {
    setAnswers({ ...answers, [questionId]: option })
  }

  const allAnswered = questions.length > 0 && Object.keys(answers).length === questions.length

  const handleSubmit = async () => {
    setIsSubmitting(true);
    try {
      await OnboardingService.submitInterviewAnswers({ answers });
      router.push('/onboarding/persona');
    } catch (err) {
      console.error(err);
      alert('Failed to submit answers: ' + err.message);
      setIsSubmitting(false);
    }
  }

  return (
    <div className="fade-up" style={{ height: 'calc(100vh - 100px)', display: 'flex', flexDirection: 'column' }}>
      {/* Stepper Indicator */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 20, justifyContent: 'center', flexShrink: 0 }}>
        {[1, 2, 3, 4, 5].map(s => (
          <div key={s} style={{
            width: 32, height: 4, borderRadius: 2,
            background: s === 4 ? '#0077B6' : s < 4 ? '#0077B6' : '#E2E8F0'
          }} />
        ))}
      </div>

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
          <h1 style={{ fontSize: 24, fontWeight: 800, color: '#03045E', marginBottom: 4 }}>
            Tacit Knowledge Profiling
          </h1>
          <p style={{ color: '#64748B', fontSize: 14 }}>
            Select the options that best represent your professional intuition.
          </p>
        </div>

        {/* SCROLLABLE CONTENT */}
        <div style={{ 
          flex: 1, 
          overflowY: 'auto', 
          padding: '24px 32px',
          display: 'flex', 
          flexDirection: 'column', 
          gap: 20,
          background: '#FAFBFC'
        }}>
          {isLoading ? (
            <div style={{ textAlign: 'center', padding: '40px', color: '#64748B' }}>
              <div style={{ width: 32, height: 32, border: '3px solid #E2E8F0', borderTop: '3px solid #0077B6', borderRadius: '50%', animation: 'spin 1s linear infinite', margin: '0 auto 16px' }} />
              Loading Tacit Questions...
            </div>
          ) : questions.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '40px', color: '#64748B', background: '#FFFFFF', borderRadius: 16, border: '1px solid #E2E8F0' }}>
              No tacit extraction questions available. Please ensure the backend is connected and master cases are uploaded.
            </div>
          ) : (
            questions.map((q, idx) => (
              <div key={q.id} style={{
                padding: '16px 20px',
                borderRadius: '16px',
                background: '#FFFFFF',
                border: '1px solid #E2E8F0',
                boxShadow: '0 2px 8px rgba(0,0,0,0.02)'
              }}>
                <div style={{ display: 'flex', gap: 10, marginBottom: 12 }}>
                  <span style={{ 
                    width: 20, height: 20, borderRadius: '50%', background: '#03045E', 
                    color: '#FFF', fontSize: 11, fontWeight: 700, display: 'flex', 
                    alignItems: 'center', justifyContent: 'center', flexShrink: 0
                  }}>
                    {idx + 1}
                  </span>
                  <h2 style={{ fontSize: 14, fontWeight: 700, color: '#03045E', lineHeight: 1.4 }}>
                    {q.question}
                  </h2>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
                  {q.options.map((opt, i) => {
                    const isSelected = answers[q.id] === opt
                    return (
                      <div 
                        key={i}
                        onClick={() => handleSelect(q.id, opt)}
                        style={{
                          padding: '12px 16px',
                          borderRadius: '10px',
                          background: isSelected ? '#0077B6' : '#FFFFFF',
                          border: `1px solid ${isSelected ? '#0077B6' : '#E2E8F0'}`,
                          color: isSelected ? '#FFFFFF' : '#475569',
                          fontSize: 12,
                          fontWeight: 500,
                          cursor: 'pointer',
                          transition: 'all 0.2s ease',
                          boxShadow: isSelected ? '0 4px 12px rgba(0, 119, 182, 0.2)' : 'none',
                          display: 'flex',
                          alignItems: 'center'
                        }}
                      >
                        {opt}
                      </div>
                    )
                  })}
                </div>
              </div>
            ))
          )}
        </div>

        {/* FIXED FOOTER */}
        <div style={{ padding: '24px 32px', borderTop: '1px solid #F1F5F9', flexShrink: 0 }}>
          <div style={{ display: 'flex', gap: 12 }}>
            <button 
              onClick={() => router.push('/onboarding/analysis')}
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
              disabled={!allAnswered || isSubmitting}
              onClick={handleSubmit}
              style={{
                flex: 2,
                padding: '16px',
                borderRadius: '12px',
                background: allAnswered ? 'linear-gradient(135deg, #03045E 0%, #0077B6 100%)' : '#CBD5E1',
                color: '#FFF',
                fontWeight: 700,
                border: 'none',
                cursor: allAnswered ? 'pointer' : 'not-allowed',
                transition: 'all 0.3s ease',
                boxShadow: allAnswered ? '0 10px 25px rgba(0, 119, 182, 0.25)' : 'none',
                fontSize: 14
              }}
            >
              {isSubmitting ? 'Syncing Profile...' : allAnswered ? 'Proceed to Persona' : 'Please answer all questions'}
            </button>
          </div>
        </div>
      </div>

      {/* Bypass Link */}
      <div style={{ marginTop: 12, textAlign: 'center', flexShrink: 0 }}>
        <button 
          onClick={() => router.push('/onboarding/persona')}
          style={{ background: 'none', border: 'none', color: '#94A3B8', fontSize: 11, cursor: 'pointer', textDecoration: 'underline' }}
        >
          Skip to Persona (Preview)
        </button>
      </div>
    </div>
  )
}
