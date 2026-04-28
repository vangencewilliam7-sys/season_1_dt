'use client'
import Sidebar from '../../components/layout/Sidebar'
import { useState, useEffect } from 'react'

export default function PersonaDashboard() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  
  // Behavioral sliders
  const [safety, setSafety] = useState(85)
  const [socratic, setSocratic] = useState(70)
  const [empathy, setEmpathy] = useState(90)
  const [protocol, setProtocol] = useState(95)
  
  const [compiling, setCompiling] = useState(false)
  const [compileSuccess, setCompileSuccess] = useState(false)

  useEffect(() => {
    fetch('/api/stats?expertId=demo')
      .then(res => res.json())
      .then(data => {
        setStats(data)
        setLoading(false)
      })
      .catch(err => {
        console.error("Failed to fetch stats:", err)
        setLoading(false)
      })
  }, [])

  const handleCompile = () => {
    setCompiling(true)
    setCompileSuccess(false)
    
    // Simulate compilation delay
    setTimeout(() => {
      setCompiling(false)
      setCompileSuccess(true)
      
      // Reset success message after 5 seconds
      setTimeout(() => setCompileSuccess(false), 5000)
    }, 2500)
  }

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <Sidebar active="/persona" />

      <main style={{ flex: 1, padding: '40px', overflow: 'auto', position: 'relative' }}>
        <div className="fade-up" style={{ marginBottom: 40 }}>
          <h1 style={{ fontSize: 28, fontWeight: 700, marginBottom: 8 }}>Expert Persona Architecture</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: 15, maxWidth: '600px' }}>
            Configure the cognitive traits and behavioral matrices of your Digital Twin. 
            The Persona Engine fuses these traits with the Master Cases in your Logic Vault.
          </p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 350px', gap: 32 }}>
          
          {/* LEFT COLUMN: IDENTITY & TUNING */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 32 }}>
            
            {/* Identity Card (Glassmorphism) */}
            <div className="fade-up" style={{
              background: 'linear-gradient(135deg, rgba(66, 133, 244, 0.1) 0%, rgba(15, 23, 42, 0.8) 100%)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(66, 133, 244, 0.2)',
              borderRadius: 'var(--radius-lg)',
              padding: '32px',
              position: 'relative',
              overflow: 'hidden'
            }}>
              <div style={{ position: 'absolute', top: -50, right: -50, width: 200, height: 200, background: 'var(--accent-primary)', filter: 'blur(100px)', opacity: 0.2, borderRadius: '50%' }} />
              
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 24, position: 'relative', zIndex: 1 }}>
                <div>
                  <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--accent-blue)', letterSpacing: 1.5, marginBottom: 8, textTransform: 'uppercase' }}>
                    Active Persona Profile
                  </div>
                  <h2 style={{ fontSize: 24, fontWeight: 700, marginBottom: 4 }}>Dr. Sarah Jenkins (Twin)</h2>
                  <div style={{ color: 'var(--text-secondary)', fontSize: 14 }}>Senior Reproductive Endocrinologist</div>
                </div>
                <div style={{ background: 'rgba(34, 197, 94, 0.1)', color: 'var(--accent-green)', padding: '6px 12px', borderRadius: 'var(--radius-sm)', fontSize: 12, fontWeight: 600, border: '1px solid rgba(34, 197, 94, 0.2)' }}>
                  SHADOW MODE ACTIVE
                </div>
              </div>
              
              <div style={{ background: 'rgba(0, 0, 0, 0.2)', borderRadius: 'var(--radius-md)', padding: '20px', border: '1px solid rgba(255, 255, 255, 0.05)', position: 'relative', zIndex: 1 }}>
                <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 8 }}>CORE SYSTEM INSTRUCTION</div>
                <p style={{ fontSize: 14, lineHeight: 1.6, color: 'var(--text-primary)', fontStyle: 'italic' }}>
                  "You are an expert Reproductive Endocrinologist. You must apply strict clinical safety protocols while maintaining a deeply empathetic, patient-centric bedside manner. You will use Socratic questioning to uncover missing clinical history before jumping to diagnoses. Base all logic strictly on the embedded Master Cases in the Logic Vault."
                </p>
              </div>
            </div>

            {/* Behavioral Tuning Matrix */}
            <div className="fade-up" style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border)',
              borderRadius: 'var(--radius-lg)',
              padding: '32px'
            }}>
              <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 24 }}>Behavioral Tuning Matrix</h2>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
                <SliderControl label="Clinical Safety Strictness" value={safety} setValue={setSafety} color="var(--accent-red)" desc="Threshold for escalating to emergency protocols" />
                <SliderControl label="Socratic Questioning" value={socratic} setValue={setSocratic} color="var(--accent-blue)" desc="Tendency to ask clarifying questions vs giving immediate answers" />
                <SliderControl label="Empathy & Bedside Manner" value={empathy} setValue={setEmpathy} color="var(--accent-green)" desc="Warmth, validation, and emotional support tone" />
                <SliderControl label="Protocol Adherence" value={protocol} setValue={setProtocol} color="var(--accent-orange)" desc="Strictness in following embedded Master Cases exactly" />
              </div>
            </div>
            
          </div>

          {/* RIGHT COLUMN: STATS & COMPILATION */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 32 }}>
            
            {/* Knowledge DNA Stats */}
            <div className="fade-up" style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border)',
              borderRadius: 'var(--radius-lg)',
              padding: '24px'
            }}>
              <h2 style={{ fontSize: 16, fontWeight: 600, marginBottom: 20 }}>Knowledge DNA Integration</h2>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                <StatRow icon="🧠" label="Active Master Cases" value={loading ? "..." : (stats?.masterCases || 0)} />
                <StatRow icon="📄" label="Processed Document Chunks" value={loading ? "..." : (stats?.documentsIngested || 0)} />
                <StatRow icon="⚠️" label="Pending Knowledge Gaps" value={loading ? "..." : (stats?.knowledgeGapsFlagged || 0)} alert={stats?.knowledgeGapsFlagged > 0} />
                <StatRow icon="⚙️" label="Manifest Versions" value={loading ? "..." : (stats?.personaManifests || 0)} />
              </div>
            </div>

            {/* Compilation Engine */}
            <div className="fade-up" style={{
              background: 'linear-gradient(180deg, var(--bg-card) 0%, rgba(30, 41, 59, 0.5) 100%)',
              border: '1px solid var(--border)',
              borderRadius: 'var(--radius-lg)',
              padding: '32px',
              textAlign: 'center',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center'
            }}>
              <div style={{
                width: 64, height: 64, borderRadius: '50%', background: 'var(--bg-elevated)', border: '1px solid var(--border)',
                display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 24, marginBottom: 16,
                boxShadow: compiling ? '0 0 20px var(--accent-primary)' : 'none',
                transition: 'all 0.3s'
              }}>
                {compiling ? '🔄' : '🧬'}
              </div>
              <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 8 }}>Manifest Compiler</h2>
              <p style={{ color: 'var(--text-secondary)', fontSize: 13, marginBottom: 24, lineHeight: 1.5 }}>
                Fuses your Behavioral Matrix with the latest Logic Vault decisions to generate a new Persona Manifest.
              </p>
              
              <button 
                onClick={handleCompile}
                disabled={compiling}
                style={{
                  width: '100%', padding: '14px',
                  background: compiling ? 'var(--bg-elevated)' : 'var(--accent-primary)',
                  color: compiling ? 'var(--text-secondary)' : '#fff',
                  border: 'none', borderRadius: 'var(--radius-sm)', fontWeight: 600, fontSize: 14,
                  cursor: compiling ? 'not-allowed' : 'pointer', transition: 'all 0.2s',
                  position: 'relative', overflow: 'hidden'
                }}
              >
                {compiling ? 'Fusing DNA...' : 'Compile Persona Manifest'}
                
                {compiling && (
                  <div style={{ position: 'absolute', bottom: 0, left: 0, height: 2, background: 'var(--accent-blue)', width: '100%', animation: 'pulse 1s infinite ease-in-out' }}/>
                )}
              </button>
              
              {compileSuccess && (
                <div style={{ marginTop: 16, color: 'var(--accent-green)', fontSize: 13, fontWeight: 500, animation: 'fadeIn 0.3s' }}>
                  ✅ Manifest v2.4 successfully compiled and deployed to Shadow Mode!
                </div>
              )}
            </div>

          </div>
        </div>
      </main>
      
      <style dangerouslySetInnerHTML={{__html: `
        @keyframes pulse { 0% { opacity: 0.4; } 50% { opacity: 1; } 100% { opacity: 0.4; } }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(-5px); } to { opacity: 1; transform: translateY(0); } }
      `}} />
    </div>
  )
}

function SliderControl({ label, value, setValue, color, desc }) {
  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
        <span style={{ fontSize: 14, fontWeight: 600 }}>{label}</span>
        <span style={{ fontSize: 14, fontWeight: 700, color }}>{value}%</span>
      </div>
      <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 12 }}>{desc}</div>
      <input 
        type="range" 
        min="0" max="100" 
        value={value} 
        onChange={(e) => setValue(e.target.value)}
        style={{
          width: '100%',
          accentColor: color,
          height: 6,
          background: 'var(--bg-elevated)',
          borderRadius: 3,
          outline: 'none',
          WebkitAppearance: 'none'
        }}
      />
      <style dangerouslySetInnerHTML={{__html: `
        input[type=range]::-webkit-slider-thumb {
          -webkit-appearance: none;
          height: 16px;
          width: 16px;
          border-radius: 50%;
          background: ${color};
          cursor: pointer;
          margin-top: -5px;
          box-shadow: 0 0 10px ${color}80;
        }
        input[type=range]::-webkit-slider-runnable-track {
          width: 100%;
          height: 6px;
          cursor: pointer;
          background: var(--bg-elevated);
          border-radius: 3px;
        }
      `}} />
    </div>
  )
}

function StatRow({ icon, label, value, alert }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px', background: 'var(--bg-elevated)', borderRadius: 'var(--radius-sm)', border: alert ? '1px solid rgba(239, 68, 68, 0.3)' : '1px solid transparent' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <span style={{ fontSize: 18 }}>{icon}</span>
        <span style={{ fontSize: 14, fontWeight: 500, color: alert ? 'var(--accent-red)' : 'var(--text-primary)' }}>{label}</span>
      </div>
      <span style={{ fontSize: 16, fontWeight: 700 }}>{value}</span>
    </div>
  )
}
