'use client'
import Sidebar from '../../components/layout/Sidebar'
import { DashboardService } from '../../lib/api/services/DashboardService'
import { PersonaService } from '../../lib/api/services/PersonaService'
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
  
  const [dynamicTraits, setDynamicTraits] = useState([])
  const [linguisticDna, setLinguisticDna] = useState([])
  const [manifestText, setManifestText] = useState("Loading manifest...")

  const updateTrait = (id, newValue) => {
    setDynamicTraits(prev => prev.map(t => t.id === id ? { ...t, value: newValue } : t))
  }
  
  const [compiling, setCompiling] = useState(false)
  const [compileSuccess, setCompileSuccess] = useState(false)

  useEffect(() => {
    // Fetch stats
    DashboardService.getStats('demo')
      .then(data => setStats(data))
      .catch(err => console.error("Failed to fetch stats:", err))

    // Fetch persona profile
    PersonaService.getProfile()
      .then(data => {
        if (data) {
          setDynamicTraits(data.traits || [])
          setLinguisticDna(data.linguisticDna || [])
          setManifestText(data.manifest || 'No manifest compiled.')
        }
      })
      .catch(err => console.error("Failed to fetch persona profile:", err))
      .finally(() => setLoading(false))
  }, [])

  const handleCompile = () => {
    setCompiling(true)
    setCompileSuccess(false)
    setTimeout(() => {
      setCompiling(false)
      setCompileSuccess(true)
      setTimeout(() => setCompileSuccess(false), 5000)
    }, 2500)
  }

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: '#F4F7FB', fontFamily: 'var(--font-sans), Inter, system-ui, sans-serif' }}>
      <Sidebar active="/persona" />

      <main style={{ flex: 1, padding: '40px', overflowY: 'auto', minWidth: 0 }}>
        <div className="fade-up" style={{ marginBottom: 40, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
          <div>
            <h1 style={{ fontSize: 28, fontWeight: 700, marginBottom: 8, color: '#03045E' }}>Expert Persona Architecture</h1>
            <p style={{ color: '#475569', fontSize: 15, maxWidth: '600px' }}>
              Review the exact prompt instructions, cognitive traits, and linguistic DNA extracted from your interviews. 
            </p>
          </div>
          <div style={{ background: '#E0E7FF', color: '#3730A3', padding: '8px 16px', borderRadius: '8px', fontSize: 13, fontWeight: 700, border: '1px solid #C7D2FE' }}>
            ACTIVE PROFILE: DR. SARAH JENKINS (TWIN)
          </div>
        </div>

        {/* FULL WIDTH MASSIVE PROMPT TERMINAL */}
        <div className="fade-up" style={{
          background: '#020617', // Deeper black for a more premium server look
          borderRadius: '12px',
          padding: '0',
          marginBottom: 32,
          boxShadow: '0 24px 48px rgba(0,0,0,0.25)',
          border: '1px solid #1E293B',
          overflow: 'hidden'
        }}>
          {/* Terminal Header - Server Slate Style */}
          <div style={{ background: '#0F172A', padding: '16px 24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #1E293B' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <div style={{ width: 8, height: 8, background: '#38BDF8', boxShadow: '0 0 12px #38BDF8', animation: 'pulse 2s infinite' }} />
              <div style={{ fontSize: 12, color: '#94A3B8', fontFamily: 'monospace', letterSpacing: '2px', textTransform: 'uppercase' }}>
                Manifest_ID: <span style={{ color: '#E2E8F0', fontWeight: 600 }}>#7A9F-2B</span>
              </div>
            </div>
            
            <div style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
              <div style={{ fontSize: 12, color: '#64748B', fontFamily: 'monospace' }}>Type: XML</div>
              <div style={{ fontSize: 11, color: '#10B981', background: 'rgba(16,185,129,0.1)', padding: '4px 10px', borderRadius: '4px', border: '1px solid rgba(16,185,129,0.2)', fontFamily: 'monospace', letterSpacing: '1px' }}>
                STATUS: ACTIVE
              </div>
            </div>
          </div>
          
          {/* Terminal Body */}
          <div style={{ padding: '32px', overflowX: 'auto' }}>
            <pre style={{ margin: 0, color: '#E2E8F0', fontFamily: '"Fira Code", monospace', fontSize: 14, lineHeight: 1.8 }}>
              {manifestText}
            </pre>
          </div>
        </div>

        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', 
          gap: 32 
        }}>
          
          {/* LEFT COLUMN: BEHAVIOR & LINGUISTICS */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 32 }}>
            
            {/* Linguistic DNA Explained */}
            <div className="fade-up" style={{
              background: '#FFFFFF',
              border: '1px solid #E2E8F0',
              borderRadius: '20px',
              padding: '32px',
              boxShadow: '0 4px 12px rgba(3, 4, 94, 0.03)',
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
                <h2 style={{ fontSize: 18, fontWeight: 700, color: '#03045E' }}>Extracted Linguistic DNA</h2>
                <div style={{ fontSize: 11, color: '#0077B6', background: '#CAF0F8', padding: '4px 10px', borderRadius: '99px', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px' }}>Tacit Extraction</div>
              </div>
              <p style={{ fontSize: 14, color: '#475569', marginBottom: 24, lineHeight: 1.6 }}>
                These are the specific conversational habits and linguistic rules extracted from your interview answers. They ensure the AI speaks exactly like you do.
              </p>
              
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                {linguisticDna.length > 0 ? linguisticDna.map((dna, idx) => (
                  <div key={idx} style={{ background: '#F8FAFC', border: '1px solid #E2E8F0', padding: '16px', borderRadius: '12px' }}>
                    <div style={{ fontSize: 13, fontWeight: 700, color: '#03045E', marginBottom: 6 }}>{dna.title}</div>
                    <div style={{ fontSize: 12, color: '#64748B', lineHeight: 1.5 }}>{dna.desc}</div>
                  </div>
                )) : (
                  <div style={{ padding: '20px', color: '#64748B', fontSize: 13, background: '#F8FAFC', borderRadius: '12px', border: '1px dashed #E2E8F0', gridColumn: 'span 2', textAlign: 'center' }}>
                    No linguistic DNA profiles found.
                  </div>
                )}
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
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
                <h2 style={{ fontSize: 18, fontWeight: 700, color: '#03045E' }}>Dynamic Behavioral Matrix</h2>
                <div style={{ fontSize: 11, color: '#0077B6', background: '#CAF0F8', padding: '4px 10px', borderRadius: '99px', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px' }}>Auto-extracted</div>
              </div>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
                {dynamicTraits.length > 0 ? dynamicTraits.map(trait => (
                  <SliderControl 
                    key={trait.id}
                    label={trait.label} 
                    value={trait.value} 
                    setValue={(val) => updateTrait(trait.id, val)} 
                    color={trait.color} 
                    bg={trait.bg} 
                    desc={trait.desc} 
                  />
                )) : (
                  <div style={{ padding: '20px', color: '#64748B', fontSize: 13, background: '#F8FAFC', borderRadius: '12px', border: '1px dashed #E2E8F0', textAlign: 'center' }}>
                    No dynamic behavioral traits configured.
                  </div>
                )}
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
              padding: '32px',
              boxShadow: '0 4px 12px rgba(3, 4, 94, 0.03)',
            }}>
              <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 24, color: '#03045E' }}>Knowledge DNA Integration</h2>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
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
              padding: '40px 32px',
              textAlign: 'center',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              boxShadow: '0 4px 12px rgba(3, 4, 94, 0.03)',
            }}>
              <div style={{
                width: 72, height: 72, borderRadius: '50%', 
                background: compiling ? '#CAF0F8' : '#F8FAFC', 
                border: `2px solid ${compiling ? '#0077B6' : '#E2E8F0'}`,
                display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 24,
                boxShadow: compiling ? '0 0 24px rgba(0,119,182,0.2)' : 'none',
                transition: 'all 0.3s'
              }}>
                {compiling ? <span style={{ animation: 'pulse 1s infinite ease-in-out', display: 'inline-block', fontSize: 24 }}>🔄</span> : <PersonaIcon size={32} />}
              </div>
              <h2 style={{ fontSize: 20, fontWeight: 700, marginBottom: 12, color: '#03045E' }}>Manifest Compiler</h2>
              <p style={{ color: '#475569', fontSize: 14, marginBottom: 32, lineHeight: 1.6, maxWidth: 300 }}>
                Fuses your Behavioral Matrix with the latest Logic Vault decisions to generate a new Persona Manifest.
              </p>
              
              <button 
                onClick={handleCompile}
                disabled={compiling}
                style={{
                  width: '100%', padding: '16px',
                  background: compiling ? '#94A3B8' : 'linear-gradient(135deg, #03045E, #0077B6)',
                  color: '#FFFFFF',
                  border: 'none', borderRadius: '12px', fontWeight: 600, fontSize: 15,
                  cursor: compiling ? 'not-allowed' : 'pointer', transition: 'all 0.2s',
                  position: 'relative', overflow: 'hidden',
                  boxShadow: compiling ? 'none' : '0 8px 24px rgba(3, 4, 94, 0.25)',
                }}
              >
                {compiling ? 'Fusing DNA...' : 'Compile Persona Manifest'}
                
                {compiling && (
                  <div style={{ position: 'absolute', bottom: 0, left: 0, height: 4, background: '#00B4D8', width: '100%', animation: 'pulse 1s infinite ease-in-out' }}/>
                )}
              </button>

              {compileSuccess && (
                <div className="fade-in" style={{ marginTop: 16, fontSize: 13, color: '#0077B6', fontWeight: 600 }}>
                  ✓ Manifest v1.0.5 compiled securely.
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
      padding: '16px 20px', 
      background: alert ? '#FEF2F2' : '#F8FAFC', 
      borderRadius: '12px', 
      border: alert ? '1px solid #FECACA' : '1px solid #E2E8F0',
      transition: 'all 0.15s',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
        <span style={{ display: 'flex', alignItems: 'center' }}>{icon}</span>
        <span style={{ fontSize: 14, fontWeight: 600, color: alert ? '#DC2626' : '#03045E' }}>{label}</span>
      </div>
      <span style={{ fontSize: 18, fontWeight: 700, color: '#03045E' }}>{value}</span>
    </div>
  )
}
