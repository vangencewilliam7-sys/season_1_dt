'use client'
import Sidebar from '../../components/layout/Sidebar'
import { useState, useEffect } from 'react'
import { 
  BrainIcon, 
  KnowledgeIcon, 
  WarningIcon, 
  GearIcon,
  PersonaIcon
} from '../../components/ui/SparkleIcons'

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
    <div style={{ display: 'flex', minHeight: '100vh', background: '#F4F7FB', fontFamily: 'var(--font-sans), Inter, system-ui, sans-serif' }}>
      <Sidebar active="/persona" />

      <main style={{ flex: 1, padding: '40px', overflow: 'auto' }}>
        <div className="fade-up" style={{ marginBottom: 40 }}>
          <h1 style={{ fontSize: 28, fontWeight: 700, marginBottom: 8, color: '#03045E' }}>Expert Persona Architecture</h1>
          <p style={{ color: '#475569', fontSize: 15, maxWidth: '600px' }}>
            Configure the cognitive traits and behavioral matrices of your Digital Twin. 
            The Persona Engine fuses these traits with the Master Cases in your Logic Vault.
          </p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 350px', gap: 32 }}>
          
          {/* LEFT COLUMN: IDENTITY & TUNING */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 32 }}>
            
            {/* Identity Card */}
            <div className="fade-up" style={{
              background: 'linear-gradient(135deg, #03045E 0%, #0077B6 50%, #00B4D8 100%)',
              borderRadius: '20px',
              padding: '32px',
              position: 'relative',
              overflow: 'hidden',
              boxShadow: '0 8px 32px rgba(3, 4, 94, 0.2)',
            }}>
              <div style={{ position: 'absolute', top: -50, right: -50, width: 200, height: 200, background: 'rgba(255,255,255,0.1)', filter: 'blur(60px)', borderRadius: '50%' }} />
              
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 24, position: 'relative', zIndex: 1 }}>
                <div>
                  <div style={{ fontSize: 11, fontWeight: 700, color: 'rgba(255,255,255,0.7)', letterSpacing: 1.5, marginBottom: 8, textTransform: 'uppercase' }}>
                    Active Persona Profile
                  </div>
                  <h2 style={{ fontSize: 24, fontWeight: 700, marginBottom: 4, color: '#FFFFFF' }}>Dr. Sarah Jenkins (Twin)</h2>
                  <div style={{ color: 'rgba(255,255,255,0.8)', fontSize: 14 }}>Senior Reproductive Endocrinologist</div>
                </div>
                <div style={{ background: 'rgba(255,255,255,0.15)', color: '#fff', padding: '6px 14px', borderRadius: '8px', fontSize: 12, fontWeight: 600, border: '1px solid rgba(255,255,255,0.25)', backdropFilter: 'blur(4px)' }}>
                  SHADOW MODE ACTIVE
                </div>
              </div>
              
              <div style={{ background: 'rgba(255,255,255,0.1)', borderRadius: '12px', padding: '20px', border: '1px solid rgba(255,255,255,0.15)', position: 'relative', zIndex: 1, backdropFilter: 'blur(8px)' }}>
                <div style={{ fontSize: 11, fontWeight: 700, color: 'rgba(255,255,255,0.6)', marginBottom: 8, textTransform: 'uppercase', letterSpacing: '1px' }}>CORE SYSTEM INSTRUCTION</div>
                <p style={{ fontSize: 14, lineHeight: 1.7, color: '#FFFFFF', fontStyle: 'italic' }}>
                  "You are an expert Reproductive Endocrinologist. You must apply strict clinical safety protocols while maintaining a deeply empathetic, patient-centric bedside manner. You will use Socratic questioning to uncover missing clinical history before jumping to diagnoses. Base all logic strictly on the embedded Master Cases in the Logic Vault."
                </p>
              </div>
            </div>

            {/* Behavioral Tuning Matrix */}
            <div className="fade-up" style={{
              background: '#FFFFFF',
              border: '1px solid #E2E8F0',
              borderRadius: '20px',
              padding: '32px',
              boxShadow: '0 4px 12px rgba(3, 4, 94, 0.03)',
            }}>
              <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 24, color: '#03045E' }}>Behavioral Tuning Matrix</h2>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
                <SliderControl label="Clinical Safety Strictness" value={safety} setValue={setSafety} color="#03045E" bg="#CAF0F8" desc="Threshold for escalating to emergency protocols" />
                <SliderControl label="Socratic Questioning" value={socratic} setValue={setSocratic} color="#0077B6" bg="#CAF0F8" desc="Tendency to ask clarifying questions vs giving immediate answers" />
                <SliderControl label="Empathy & Bedside Manner" value={empathy} setValue={setEmpathy} color="#00B4D8" bg="#CAF0F8" desc="Warmth, validation, and emotional support tone" />
                <SliderControl label="Protocol Adherence" value={protocol} setValue={setProtocol} color="#F59E0B" bg="#FFFBEB" desc="Strictness in following embedded Master Cases exactly" />
              </div>
            </div>
            
          </div>

          {/* RIGHT COLUMN: STATS & COMPILATION */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 32 }}>
            
            {/* Knowledge DNA Stats */}
            <div className="fade-up" style={{
              background: '#FFFFFF',
              border: '1px solid #E2E8F0',
              borderRadius: '20px',
              padding: '24px',
              boxShadow: '0 4px 12px rgba(3, 4, 94, 0.03)',
            }}>
              <h2 style={{ fontSize: 16, fontWeight: 700, marginBottom: 20, color: '#03045E' }}>Knowledge DNA Integration</h2>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                <StatRow icon={<BrainIcon />} label="Active Master Cases" value={loading ? "..." : (stats?.masterCases || 0)} />
                <StatRow icon={<KnowledgeIcon />} label="Processed Document Chunks" value={loading ? "..." : (stats?.documentsIngested || 0)} />
                <StatRow icon={<WarningIcon />} label="Pending Knowledge Gaps" value={loading ? "..." : (stats?.knowledgeGapsFlagged || 0)} alert={stats?.knowledgeGapsFlagged > 0} />
                <StatRow icon={<GearIcon />} label="Manifest Versions" value={loading ? "..." : (stats?.personaManifests || 0)} />
              </div>
            </div>

            {/* Compilation Engine */}
            <div className="fade-up" style={{
              background: '#FFFFFF',
              border: '1px solid #E2E8F0',
              borderRadius: '20px',
              padding: '32px',
              textAlign: 'center',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              boxShadow: '0 4px 12px rgba(3, 4, 94, 0.03)',
            }}>
              <div style={{
                width: 64, height: 64, borderRadius: '50%', 
                background: compiling ? '#CAF0F8' : '#F8FAFC', 
                border: `2px solid ${compiling ? '#0077B6' : '#E2E8F0'}`,
                display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 16,
                boxShadow: compiling ? '0 0 24px rgba(0,119,182,0.2)' : 'none',
                transition: 'all 0.3s'
              }}>
                {compiling ? <span style={{ animation: 'pulse 1s infinite ease-in-out', display: 'inline-block' }}>🔄</span> : <PersonaIcon size={28} />}
              </div>
              <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 8, color: '#03045E' }}>Manifest Compiler</h2>
              <p style={{ color: '#475569', fontSize: 13, marginBottom: 24, lineHeight: 1.5 }}>
                Fuses your Behavioral Matrix with the latest Logic Vault decisions to generate a new Persona Manifest.
              </p>
              
              <button 
                onClick={handleCompile}
                disabled={compiling}
                style={{
                  width: '100%', padding: '14px',
                  background: compiling ? '#94A3B8' : 'linear-gradient(135deg, #03045E, #0077B6)',
                  color: '#FFFFFF',
                  border: 'none', borderRadius: '8px', fontWeight: 600, fontSize: 14,
                  cursor: compiling ? 'not-allowed' : 'pointer', transition: 'all 0.2s',
                  position: 'relative', overflow: 'hidden',
                  boxShadow: compiling ? 'none' : '0 4px 16px rgba(3, 4, 94, 0.2)',
                }}
              >
                {compiling ? 'Fusing DNA...' : 'Compile Persona Manifest'}
                
                {compiling && (
                  <div style={{ position: 'absolute', bottom: 0, left: 0, height: 3, background: '#00B4D8', width: '100%', animation: 'pulse 1s infinite ease-in-out' }}/>
                )}
              </button>

              {compileSuccess && (
                <div className="fade-in" style={{ marginTop: 12, fontSize: 12, color: '#0077B6', fontWeight: 600 }}>
                  ✓ Manifest compiled securely.
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

function SliderControl({ label, value, setValue, color, bg, desc }) {
  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
        <span style={{ fontSize: 14, fontWeight: 600, color: '#03045E' }}>{label}</span>
        <span style={{ fontSize: 14, fontWeight: 700, color, background: bg, padding: '2px 10px', borderRadius: 99 }}>{value}%</span>
      </div>
      <div style={{ fontSize: 12, color: '#475569', marginBottom: 12 }}>{desc}</div>
      <input 
        type="range" 
        min="0" max="100" 
        value={value} 
        onChange={(e) => setValue(e.target.value)}
        style={{
          width: '100%',
          accentColor: color,
          height: 6,
          background: '#E2E8F0',
          borderRadius: 3,
          outline: 'none',
          WebkitAppearance: 'none'
        }}
      />
      <style dangerouslySetInnerHTML={{__html: `
        input[type=range]::-webkit-slider-thumb {
          -webkit-appearance: none;
          height: 18px;
          width: 18px;
          border-radius: 50%;
          background: ${color};
          cursor: pointer;
          margin-top: -6px;
          box-shadow: 0 2px 8px ${color}50;
          border: 3px solid #fff;
        }
        input[type=range]::-webkit-slider-runnable-track {
          width: 100%;
          height: 6px;
          cursor: pointer;
          background: #E2E8F0;
          border-radius: 3px;
        }
      `}} />
    </div>
  )
}

function StatRow({ icon, label, value, alert }) {
  return (
    <div style={{ 
      display: 'flex', alignItems: 'center', justifyContent: 'space-between', 
      padding: '14px 16px', 
      background: alert ? '#FEF2F2' : '#F8FAFC', 
      borderRadius: '8px', 
      border: alert ? '1px solid #FECACA' : '1px solid #E2E8F0',
      transition: 'all 0.15s',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <span style={{ display: 'flex', alignItems: 'center' }}>{icon}</span>
        <span style={{ fontSize: 14, fontWeight: 500, color: alert ? '#DC2626' : '#03045E' }}>{label}</span>
      </div>
      <span style={{ fontSize: 16, fontWeight: 700, color: '#03045E' }}>{value}</span>
    </div>
  )
}
