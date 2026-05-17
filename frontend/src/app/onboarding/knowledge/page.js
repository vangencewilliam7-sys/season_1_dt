'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { OnboardingService } from '../../../lib/api/services/OnboardingService'

export default function KnowledgeIngestionPage() {
  const router = useRouter()
  const [files, setFiles] = useState([])
  const [isIngesting, setIsIngesting] = useState(false)
  const [progress, setProgress] = useState(0)

  const handleFileChange = (e) => {
    const newFiles = Array.from(e.target.files)
    setFiles([...files, ...newFiles])
  }

  const startIngestion = async () => {
    if (files.length === 0) return;
    setIsIngesting(true);
    setProgress(10); // initial
    
    try {
      const formData = new FormData();
      files.forEach(f => formData.append('files', f));
      
      await OnboardingService.uploadKnowledgeFiles(formData);
      
      setProgress(100);
      setTimeout(() => router.push('/onboarding/cases'), 800);
    } catch (err) {
      console.error(err);
      alert('Failed to ingest knowledge: ' + err.message);
      setIsIngesting(false);
      setProgress(0);
    }
  }

  return (
    <div className="fade-up">
      {/* Stepper Indicator */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 20, justifyContent: 'center' }}>
        {[1, 2, 3, 4, 5].map(s => (
          <div key={s} style={{
            width: 32, height: 4, borderRadius: 2,
            background: s === 1 ? '#0077B6' : s < 1 ? '#0077B6' : '#E2E8F0'
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
          Build your Knowledge Hub
        </h1>
        <p style={{ color: '#475569', fontSize: 14, marginBottom: 32, maxWidth: 500, marginInline: 'auto' }}>
          Upload your core documentation. This forms the foundation of your Digital Twin's expertise.
        </p>

        {!isIngesting ? (
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
                setFiles([...files, ...droppedFiles])
              }}
            >
              <input 
                type="file" 
                multiple 
                onChange={handleFileChange}
                style={{ position: 'absolute', inset: 0, opacity: 0, cursor: 'pointer' }}
              />
              <div style={{ fontSize: 32, marginBottom: 12 }}>📂</div>
              <div style={{ fontWeight: 600, color: '#1E293B', marginBottom: 4 }}>
                Click or drag files to upload
              </div>
              <div style={{ fontSize: 12, color: '#64748B' }}>
                PDF, DOCX, or TXT
              </div>
            </div>

            {files.length > 0 && (
              <div style={{ marginTop: 24, textAlign: 'left' }}>
                <div style={{ fontSize: 13, fontWeight: 700, color: '#334155', marginBottom: 8 }}>
                  Files ready ({files.length})
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                  {files.slice(0, 5).map((f, i) => (
                    <div key={i} style={{
                      padding: '8px 12px',
                      background: '#F1F5F9',
                      borderRadius: '8px',
                      fontSize: 12,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between'
                    }}>
                      <span style={{ color: '#1E293B', fontWeight: 500 }}>{f.name}</span>
                      <span style={{ color: '#64748B', fontSize: 10 }}>{(f.size / 1024).toFixed(0)} KB</span>
                    </div>
                  ))}
                  {files.length > 5 && <div style={{ fontSize: 11, color: '#94A3B8' }}>+ {files.length - 5} more files</div>}
                </div>
              </div>
            )}

            <div style={{ display: 'flex', gap: 12, marginTop: 32 }}>
              <button 
                onClick={() => router.push('/')}
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
                disabled={files.length === 0}
                onClick={startIngestion}
                style={{
                  flex: 2,
                  padding: '16px',
                  borderRadius: '12px',
                  background: files.length > 0 ? 'linear-gradient(135deg, #03045E 0%, #0077B6 100%)' : '#CBD5E1',
                  color: '#FFF',
                  fontWeight: 700,
                  border: 'none',
                  cursor: files.length > 0 ? 'pointer' : 'not-allowed',
                  boxShadow: files.length > 0 ? '0 10px 20px rgba(0, 119, 182, 0.2)' : 'none',
                  fontSize: 14
                }}
              >
                Start Ingestion
              </button>
            </div>
          </>
        ) : (
          <div style={{ padding: '24px 0' }}>
            <div style={{ fontSize: 40, marginBottom: 16 }} className="pulse">🧠</div>
            <h2 style={{ fontSize: 18, fontWeight: 700, color: '#03045E', marginBottom: 6 }}>
              Ingesting Knowledge
            </h2>
            <p style={{ color: '#64748B', fontSize: 13, marginBottom: 24 }}>
              Breaking down documents into semantic fragments...
            </p>
            
            <div style={{ 
              width: '100%', 
              height: 6, 
              background: '#F1F5F9', 
              borderRadius: 3, 
              overflow: 'hidden',
              marginBottom: 8
            }}>
              <div style={{ 
                width: `${progress}%`, 
                height: '100%', 
                background: '#0077B6', 
                transition: 'width 0.4s ease' 
              }} />
            </div>
            <div style={{ fontSize: 12, fontWeight: 700, color: '#0077B6' }}>
              {progress.toFixed(0)}%
            </div>
          </div>
        )}
      </div>

      {/* Bypass Link */}
      <div style={{ marginTop: 20, textAlign: 'center' }}>
        <button 
          onClick={() => router.push('/onboarding/cases')}
          style={{ background: 'none', border: 'none', color: '#94A3B8', fontSize: 11, cursor: 'pointer', textDecoration: 'underline' }}
        >
          Skip to Step 2 (Preview)
        </button>
      </div>
    </div>
  )
}
