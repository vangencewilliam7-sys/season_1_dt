'use client'
import Sidebar from '../../components/layout/Sidebar'
import { useState, useEffect } from 'react'

export default function KnowledgeHubPage() {
  const [files, setFiles] = useState([])
  const [isProcessing, setIsProcessing] = useState(false)
  
  // HITL Resolution State
  const [activeResolution, setActiveResolution] = useState(null)
  const [scenarios, setScenarios] = useState([])
  const [isFetchingState, setIsFetchingState] = useState(false)
  const [expertDecision, setExpertDecision] = useState('')
  const [extractedCases, setExtractedCases] = useState([])

  // Load state from localStorage on mount
  useEffect(() => {
    const savedQueue = localStorage.getItem('kh_ingestion_queue')
    if (savedQueue) {
      try {
        const parsed = JSON.parse(savedQueue)
        // We must drop the actual File objects because they can't be serialized,
        // but for a queue visualizer, we just need the metadata.
        // Wait, if we drop the File object, we can't upload it if it was queued!
        // We only persist files that are 'done' or 'archived' or 'error'.
        // Queued/uploading files that lost their File object will fail.
        setFiles(parsed.filter(f => f.status !== 'queued' && f.status !== 'uploading'))
      } catch (e) { console.error('Failed to parse queue') }
    }
  }, [])

  // Save state to localStorage on change
  useEffect(() => {
    if (files.length > 0) {
      // Strip out the File object to prevent serialization errors
      const serializableFiles = files.map(f => ({ ...f, file: { name: f.file?.name, size: f.file?.size } }))
      localStorage.setItem('kh_ingestion_queue', JSON.stringify(serializableFiles))
    }
  }, [files])

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      const newFiles = Array.from(e.target.files).map(file => ({
        id: Math.random().toString(36).substr(2, 9),
        file,
        status: 'queued', // queued, uploading, done, archived, error
        message: '',
        document_id: null
      }))
      setFiles(prev => [...prev, ...newFiles])
    }
  }

  const removeFile = (id) => {
    if (isProcessing) return
    setFiles(prev => prev.filter(f => f.id !== id))
  }

  const handleProcessQueue = async () => {
    if (isProcessing) return
    setIsProcessing(true)

    for (let i = 0; i < files.length; i++) {
      if (files[i].status === 'queued' || files[i].status === 'error') {
        
        setFiles(prev => prev.map((f, index) => 
          index === i ? { ...f, status: 'uploading', message: 'Ingesting document into pipeline...' } : f
        ))

        const formData = new FormData()
        // If it was loaded from localStorage, f.file might be a dummy object without the actual File blob.
        // But we filtered out queued/error files on reload, so if it's queued, it has the real File.
        if (!files[i].file || !files[i].file.stream) {
           setFiles(prev => prev.map((f, index) => 
            index === i ? { ...f, status: 'error', message: 'File data lost due to refresh. Please re-upload.' } : f
          ))
          continue;
        }

        formData.append('file', files[i].file)

        try {
          const res = await fetch('http://127.0.0.1:8000/api/ingest', {
            method: 'POST',
            body: formData,
          })

          if (!res.ok) {
            const errorData = await res.json()
            throw new Error(errorData.detail || 'Upload failed')
          }

          const data = await res.json()
          
          setFiles(prev => prev.map((f, index) => 
            index === i ? { 
              ...f, 
              status: 'done', 
              message: 'Success! Paused at HITL Node.', 
              document_id: data.document_id 
            } : f
          ))
        } catch (err) {
          console.error(err)
          setFiles(prev => prev.map((f, index) => 
            index === i ? { ...f, status: 'error', message: err.message || 'Failed to connect.' } : f
          ))
        }
      }
    }
    
    setIsProcessing(false)
  }

  const handleOpenResolution = async (file) => {
    setActiveResolution(file)
    setIsFetchingState(true)
    setScenarios([])
    setExpertDecision('')
    setExtractedCases([])
    
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/state/${file.document_id}`)
      if (!res.ok) throw new Error("Failed to fetch LangGraph state")
      const data = await res.json()
      setScenarios(data.synthetic_scenarios || [])
      setExtractedCases(data.parsed_cases || [])
    } catch (e) {
      console.error(e)
      alert("Failed to load synthetic scenarios.")
    }
    setIsFetchingState(false)
  }

  const handleCommitResolution = async (scenario_id) => {
    if (!expertDecision.trim()) {
      alert("Please provide an expert decision.")
      return
    }

    try {
      const res = await fetch(`http://127.0.0.1:8000/api/commit?scenario_id=${scenario_id}&expert_decision=${encodeURIComponent(expertDecision)}&archetype=Safety`, {
        method: 'POST'
      })
      if (!res.ok) throw new Error("Commit failed")
      
      alert("Expert logic committed to Logic Vault successfully!")
      
      // Update file status to archived
      setFiles(prev => prev.map(f => f.id === activeResolution.id ? { ...f, status: 'archived', message: 'Committed to Logic Vault' } : f))
      setActiveResolution(null)
      
    } catch (e) {
      console.error(e)
      alert("Failed to commit resolution.")
    }
  }

  const queuedCount = files.filter(f => f.status === 'queued' || f.status === 'error').length

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <Sidebar active="/knowledge-hub" />

      <main style={{ flex: 1, padding: '32px 36px', overflow: 'auto', position: 'relative' }}>
        <div className="fade-up" style={{ marginBottom: 36 }}>
          <h1 style={{ fontSize: 26, fontWeight: 700, marginBottom: 4 }}>Knowledge Hub Ingestion</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: 14 }}>
            Upload multiple clinical documents (.pdf or .docx) to batch-process them through the pipeline.
          </p>
        </div>

        <div style={{ display: 'flex', gap: 24, alignItems: 'flex-start' }}>
          {/* UPLOAD SECTION */}
          <div className="fade-up" style={{
            background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 'var(--radius-lg)',
            padding: '32px', flex: '1', maxWidth: '450px', position: 'sticky', top: 32
          }}>
            <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 24 }}>Upload Source Material</h2>

            <div style={{
              border: '2px dashed var(--border)', borderRadius: 'var(--radius-md)', padding: '40px',
              textAlign: 'center', marginBottom: 24, background: 'var(--bg-elevated)', transition: 'border-color 0.2s',
            }}>
              <input type="file" accept=".pdf,.docx" multiple onChange={handleFileChange} style={{ display: 'none' }} id="file-upload" />
              <label htmlFor="file-upload" style={{ cursor: 'pointer', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <span style={{ fontSize: 32, marginBottom: 12 }}>📁</span>
                <span style={{ fontSize: 15, fontWeight: 500, color: 'var(--accent-primary)', marginBottom: 8 }}>Select multiple files</span>
                <span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>Supports .PDF and .DOCX</span>
              </label>
            </div>

            <button 
              onClick={handleProcessQueue}
              disabled={queuedCount === 0 || isProcessing}
              style={{
                width: '100%', padding: '12px',
                background: (queuedCount === 0 || isProcessing) ? 'var(--bg-elevated)' : 'var(--accent-primary)',
                color: (queuedCount === 0 || isProcessing) ? 'var(--text-secondary)' : '#fff',
                border: 'none', borderRadius: 'var(--radius-sm)', fontWeight: 600, fontSize: 14,
                cursor: (queuedCount === 0 || isProcessing) ? 'not-allowed' : 'pointer', transition: 'all 0.2s'
              }}
            >
              {isProcessing ? 'Processing Queue...' : `Start Pipeline (${queuedCount} pending)`}
            </button>
          </div>

          {/* QUEUE VISUALIZER SECTION */}
          <div className="fade-up" style={{ flex: '1', minWidth: '400px' }}>
            <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 16 }}>Processing Queue</h2>
            
            {files.length === 0 ? (
              <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-secondary)', border: '1px solid var(--border)', borderRadius: 'var(--radius-md)', background: 'var(--bg-card)' }}>
                No documents in queue.
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                {files.map((f) => (
                  <div key={f.id} style={{
                    background: 'var(--bg-card)', border: '1px solid',
                    borderColor: f.status === 'error' ? 'var(--accent-red)50' : 
                                 f.status === 'done' ? 'var(--accent-orange)50' : 
                                 f.status === 'archived' ? 'var(--accent-green)50' :
                                 f.status === 'uploading' ? 'var(--accent-blue)50' : 'var(--border)',
                    borderRadius: 'var(--radius-md)', padding: '16px', position: 'relative', overflow: 'hidden'
                  }}>
                    {f.status === 'uploading' && (
                      <div style={{ position: 'absolute', bottom: 0, left: 0, height: 2, background: 'var(--accent-blue)', width: '100%', animation: 'pulse 2s infinite ease-in-out' }}/>
                    )}
                    {f.status === 'done' && (
                      <div style={{ position: 'absolute', bottom: 0, left: 0, height: 2, background: 'var(--accent-orange)', width: '100%', animation: 'pulse 2s infinite ease-in-out' }}/>
                    )}
                    {f.status === 'archived' && (
                      <div style={{ position: 'absolute', bottom: 0, left: 0, height: 2, background: 'var(--accent-green)', width: '100%' }}/>
                    )}
                    {f.status === 'error' && (
                      <div style={{ position: 'absolute', bottom: 0, left: 0, height: 2, background: 'var(--accent-red)', width: '100%' }}/>
                    )}

                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                        <span style={{ fontSize: 18 }}>
                          {f.status === 'archived' ? '✅' : f.status === 'done' ? '⚠️' : f.status === 'error' ? '❌' : f.status === 'uploading' ? '⏳' : '📄'}
                        </span>
                        <div>
                          <div style={{ fontSize: 14, fontWeight: 600 }}>{f.file?.name || 'Restored Document'}</div>
                          <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{f.file?.size ? (f.file.size / 1024 / 1024).toFixed(2) + ' MB' : 'Size Unknown'}</div>
                        </div>
                      </div>
                      
                      {!isProcessing && (
                        <button onClick={() => removeFile(f.id)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-secondary)', fontSize: 16 }}>✕</button>
                      )}
                      
                      {f.status === 'done' && (
                        <button 
                          onClick={() => handleOpenResolution(f)}
                          style={{
                            background: 'var(--accent-orange)20', color: 'var(--accent-orange)',
                            border: '1px solid var(--accent-orange)50', padding: '6px 12px',
                            borderRadius: 'var(--radius-sm)', fontSize: 12, fontWeight: 600, cursor: 'pointer'
                          }}
                        >
                          Action Required
                        </button>
                      )}
                    </div>

                    {f.message && (
                      <div style={{ 
                        fontSize: 12, marginTop: 8, 
                        color: f.status === 'error' ? 'var(--accent-red)' : 
                               f.status === 'done' ? 'var(--accent-orange)' : 
                               f.status === 'archived' ? 'var(--accent-green)' : 'var(--accent-blue)' 
                      }}>
                        {f.message}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* HITL RESOLUTION MODAL OVERLAY */}
        {activeResolution && (
          <div style={{
            position: 'absolute', top: 0, left: 0, right: 0, bottom: 0,
            background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(4px)',
            display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100, padding: 40
          }}>
            <div style={{
              background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 'var(--radius-lg)',
              width: '100%', maxWidth: '800px', maxHeight: '90vh', overflow: 'hidden', display: 'flex', flexDirection: 'column'
            }}>
              <div style={{ padding: '24px', borderBottom: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h3 style={{ fontSize: 20, fontWeight: 600 }}>Human-in-the-Loop Resolution</h3>
                <button onClick={() => setActiveResolution(null)} style={{ background: 'none', border: 'none', fontSize: 20, cursor: 'pointer', color: 'var(--text-secondary)' }}>✕</button>
              </div>
              
              <div style={{ padding: '24px', overflowY: 'auto', flex: 1 }}>
                <p style={{ color: 'var(--text-secondary)', marginBottom: 24 }}>
                  The AI pipeline successfully detected clinical decision gaps and generated Synthetic Scenarios to test edge cases. 
                  Provide your Expert Decision to commit this logic to the vault.
                </p>

                {isFetchingState ? (
                  <div style={{ textAlign: 'center', padding: 40, color: 'var(--accent-blue)' }}>Fetching state from LangGraph...</div>
                ) : scenarios.length === 0 ? (
                  <div style={{ textAlign: 'center', padding: 40, color: 'var(--text-secondary)' }}>No scenarios found in state.</div>
                ) : (
                  <div>
                    {/* Automatically Extracted Cases Section */}
                    {extractedCases.length > 0 && (
                      <div style={{ marginBottom: 32 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
                          <h4 style={{ fontSize: 16, fontWeight: 600 }}>Automatically Extracted Logic</h4>
                          <span className="badge badge-teal">Verified grounding</span>
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                          {extractedCases.map((c, i) => (
                            <div key={i} style={{ 
                              background: 'var(--bg-elevated)', border: '1px solid var(--border)', 
                              padding: 16, borderRadius: 'var(--radius-md)' 
                            }}>
                              <div style={{ fontWeight: 600, fontSize: 14, marginBottom: 4, color: 'var(--accent-teal)' }}>
                                Expert Rule: {c.expert_decision}
                              </div>
                              <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
                                <strong>Logic:</strong> {c.chain_of_thought.join(' → ')}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
                      <h4 style={{ fontSize: 16, fontWeight: 600 }}>Synthetic Scenarios (HITL)</h4>
                      <span className="badge badge-amber">Action required</span>
                    </div>

                    {scenarios.map((scene, idx) => (
                      <div key={idx} style={{ background: 'var(--bg-elevated)', padding: 20, borderRadius: 'var(--radius-md)', marginBottom: 24, border: '1px solid var(--border)' }}>
                        <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--accent-orange)', marginBottom: 8 }}>SCENARIO {idx + 1}</div>
                        <div style={{ fontSize: 15, lineHeight: 1.6, marginBottom: 16 }}>{scene.scenario_text}</div>
                        
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                          <label style={{ fontSize: 13, fontWeight: 500, color: 'var(--text-secondary)' }}>Your Expert Decision:</label>
                          <textarea 
                            value={expertDecision}
                            onChange={(e) => setExpertDecision(e.target.value)}
                            placeholder="Type your medical logic or protocol for handling this specific scenario..."
                            style={{
                              width: '100%', minHeight: 100, background: 'var(--bg-card)', border: '1px solid var(--border)',
                              borderRadius: 'var(--radius-sm)', padding: 12, color: 'var(--text-primary)', fontFamily: 'inherit', resize: 'vertical'
                            }}
                          />
                          <button 
                            onClick={() => handleCommitResolution(scene.id)}
                            style={{
                              alignSelf: 'flex-end', background: 'var(--accent-green)', color: '#fff', border: 'none',
                              padding: '8px 16px', borderRadius: 'var(--radius-sm)', fontWeight: 600, cursor: 'pointer', marginTop: 8
                            }}
                          >
                            Commit Logic to Vault
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </main>
      
      <style dangerouslySetInnerHTML={{__html: `
        @keyframes pulse { 0% { opacity: 0.4; } 50% { opacity: 1; } 100% { opacity: 0.4; } }
      `}} />
    </div>
  )
}
