'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'

export default function MasterCasesPage() {
  const router = useRouter()
  const [cases, setCases] = useState([])
  const [isProcessing, setIsProcessing] = useState(false)

  const handleFileChange = (e) => {
    const newFiles = Array.from(e.target.files)
    setCases([...cases, ...newFiles])
  }

  const startProcessing = () => {
    setIsProcessing(true)
    setTimeout(() => router.push('/onboarding/analysis'), 2500)
  }

  return (
    <div className="fade-up">
      {/* Stepper Indicator */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 20, justifyContent: 'center' }}>
        {[1, 2, 3, 4, 5].map(s => (
          <div key={s} style={{
            width: 32, height: 4, borderRadius: 2,
            background: s === 2 ? '#0077B6' : s < 2 ? '#0077B6' : '#E2E8F0'
          }} />
        ))}
      </div>

      <div style={{
        background: '#FFFFFF',
        borderRadius: 24,
        padding: '32px',
        border: '1px solid #E2E8F0',
        boxShadow: '0 20px 50px rgba(3, 4, 94, 0.05)',
        textAlign: 'center'
      }}>
        <h1 style={{ fontSize: 28, fontWeight: 800, color: '#03045E', marginBottom: 8 }}>
          Upload Master Cases
        </h1>
        <p style={{ color: '#475569', fontSize: 14, marginBottom: 32, maxWidth: 500, marginInline: 'auto' }}>
          Share examples of your best work to help the AI understand your unique "Expert Intuition."
        </p>

        {!isProcessing ? (
          <>
            <div 
              style={{
                border: '2px dashed #CBD5E1',
                borderRadius: 16,
                padding: '40px 20px',
                background: '#F8FAFC',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                position: 'relative'
              }}
              onDragOver={(e) => e.preventDefault()}
              onDrop={(e) => {
                e.preventDefault()
                const droppedFiles = Array.from(e.dataTransfer.files)
                setCases([...cases, ...droppedFiles])
              }}
            >
              <input 
                type="file" 
                multiple 
                onChange={handleFileChange}
                style={{ position: 'absolute', inset: 0, opacity: 0, cursor: 'pointer' }}
              />
              <div style={{ fontSize: 32, marginBottom: 12 }}>💼</div>
              <div style={{ fontWeight: 600, color: '#1E293B', marginBottom: 4 }}>
                Drop your case studies here
              </div>
              <div style={{ fontSize: 12, color: '#64748B' }}>
                PDF, CSV, or TXT
              </div>
            </div>

            {cases.length > 0 && (
              <div style={{ marginTop: 24, textAlign: 'left' }}>
                <div style={{ fontSize: 13, fontWeight: 700, color: '#334155', marginBottom: 8 }}>
                  Experience Files ({cases.length})
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                  {cases.slice(0, 5).map((f, i) => (
                    <div key={i} style={{
                      padding: '10px 14px',
                      background: '#F0F9FF',
                      borderRadius: '10px',
                      fontSize: 12,
                      display: 'flex',
                      alignItems: 'center',
                      border: '1px solid #BAE6FD'
                    }}>
                      <span style={{ fontSize: 14, marginRight: 10 }}>📄</span>
                      <span style={{ color: '#0369A1', fontWeight: 600 }}>{f.name}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div style={{ display: 'flex', gap: 12, marginTop: 32 }}>
              <button 
                onClick={() => router.push('/onboarding/knowledge')}
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
                disabled={cases.length === 0}
                onClick={startProcessing}
                style={{
                  flex: 2,
                  padding: '16px',
                  borderRadius: '12px',
                  background: cases.length > 0 ? 'linear-gradient(135deg, #03045E 0%, #0077B6 100%)' : '#CBD5E1',
                  color: '#FFF',
                  fontWeight: 700,
                  border: 'none',
                  cursor: cases.length > 0 ? 'pointer' : 'not-allowed',
                  boxShadow: cases.length > 0 ? '0 10px 20px rgba(0, 119, 182, 0.2)' : 'none',
                  fontSize: 14
                }}
              >
                Confirm Experience
              </button>
            </div>
          </>
        ) : (
          <div style={{ padding: '24px 0' }}>
            <div style={{ fontSize: 40, marginBottom: 16 }} className="pulse">📁</div>
            <h2 style={{ fontSize: 18, fontWeight: 700, color: '#03045E', marginBottom: 6 }}>
              Processing Patterns
            </h2>
            <p style={{ color: '#64748B', fontSize: 13, marginBottom: 24 }}>
              Linking experience to your knowledge hub...
            </p>
            <div className="loading-dots" style={{ fontSize: 20, color: '#0077B6' }}>
              <span>.</span><span>.</span><span>.</span>
            </div>
          </div>
        )}
      </div>

      {/* Bypass Link */}
      <div style={{ marginTop: 20, textAlign: 'center' }}>
        <button 
          onClick={() => router.push('/onboarding/analysis')}
          style={{ background: 'none', border: 'none', color: '#94A3B8', fontSize: 11, cursor: 'pointer', textDecoration: 'underline' }}
        >
          Skip to Step 3 (Preview)
        </button>
      </div>
    </div>
  )
}
