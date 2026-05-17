'use client'

export default function OnboardingLayout({ children }) {
  return (
    <div style={{
      minHeight: '100vh',
      background: 'radial-gradient(circle at top right, #E0F2FE, #F8FAFC 40%)',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      padding: '20px',
      fontFamily: 'Inter, system-ui, sans-serif',
      overflow: 'auto'
    }}>
      {/* Header / Brand */}
      <div style={{ marginBottom: 24, textAlign: 'center' }}>
        <div style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: 12,
          padding: '6px 12px',
          background: 'rgba(255, 255, 255, 0.8)',
          borderRadius: '10px',
          border: '1px solid #E2E8F0',
          boxShadow: '0 4px 12px rgba(0,0,0,0.03)'
        }}>
          <span style={{ fontSize: 18 }}>⚕</span>
          <span style={{ fontWeight: 700, color: '#03045E', fontSize: 13 }}>Digital Twin Onboarding</span>
        </div>
      </div>

      <div style={{ width: '100%', maxWidth: 1000 }}>
        {children}
      </div>

      {/* Development Bypass Footer */}
      <div style={{
        marginTop: '20px',
        padding: '10px',
        color: '#94A3B8',
        fontSize: 10,
        fontWeight: 500,
        letterSpacing: '0.05em',
        textTransform: 'uppercase'
      }}>
        UI Preview Mode
      </div>
    </div>
  )
}
