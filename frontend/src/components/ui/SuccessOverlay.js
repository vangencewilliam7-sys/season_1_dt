'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'

export default function SuccessOverlay({ onEnterDashboard }) {
  const router = useRouter()
  const [showContent, setShowContent] = useState(false)

  useEffect(() => {
    const timer = setTimeout(() => setShowContent(true), 2200)
    return () => clearTimeout(timer)
  }, [])

  const handleEnter = () => {
    if (onEnterDashboard) {
      onEnterDashboard()
    } else {
      router.push('/dashboard')
    }
  }

  return (
    <div className="fade-up" style={{ 
      flex: 1,
      display: 'flex', 
      flexDirection: 'column', 
      alignItems: 'center', 
      justifyContent: 'center',
      textAlign: 'center',
      padding: '40px 20px',
      background: 'transparent',
      width: '100%'
    }}>
      {/* PHONEPE STYLE SUCCESS ANIMATION */}
      <div style={{ position: 'relative', width: 180, height: 180, marginBottom: 40 }}>
        {/* Outer Ripple Rings */}
        {[...Array(3)].map((_, i) => (
          <div key={i} style={{
            position: 'absolute',
            inset: 0,
            borderRadius: '50%',
            border: '2px solid #10B981',
            opacity: 0,
            animation: `phonepe-ripple 2s infinite ${i * 0.6}s cubic-bezier(0, 0, 0.2, 1)`
          }} />
        ))}
        
        {/* Main Success Circle */}
        <div style={{
          position: 'absolute',
          inset: 18,
          borderRadius: '50%',
          background: '#10B981',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 10px 30px rgba(16, 185, 129, 0.4)',
          animation: 'phonepe-pop 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275) both'
        }}>
          {/* Animated SVG Checkmark */}
          <svg width="70" height="70" viewBox="0 0 100 100" fill="none">
            <path 
              d="M25 50L40 65L75 30" 
              stroke="white" 
              strokeWidth="10" 
              strokeLinecap="round" 
              strokeLinejoin="round"
              style={{
                strokeDasharray: 100,
                strokeDashoffset: 100,
                animation: 'phonepe-check 0.4s ease forwards 0.5s'
              }}
            />
          </svg>
        </div>
      </div>

      <div style={{
        opacity: showContent ? 1 : 0,
        transform: showContent ? 'translateY(0)' : 'translateY(20px)',
        transition: 'all 1s cubic-bezier(0.19, 1, 0.22, 1)',
        visibility: showContent ? 'visible' : 'hidden'
      }}>
        <h1 style={{ fontSize: 32, fontWeight: 800, color: '#03045E', marginBottom: 12 }}>
          Your Twin is Ready
        </h1>
        <p style={{ color: '#64748B', fontSize: 16, marginBottom: 36, maxWidth: 420, marginInline: 'auto', lineHeight: 1.5 }}>
          Onboarding complete! Your Digital Twin has been successfully initialized with your expertise and persona.
        </p>

        <button 
          onClick={handleEnter}
          style={{
            padding: '16px 48px',
            borderRadius: '16px',
            background: 'linear-gradient(135deg, #03045E 0%, #0077B6 100%)',
            color: '#FFF',
            fontWeight: 800,
            fontSize: 15,
            border: 'none',
            cursor: 'pointer',
            boxShadow: '0 12px 30px rgba(0, 119, 182, 0.3)',
            transition: 'all 0.3s ease',
            letterSpacing: '0.02em'
          }}
          onMouseOver={(e) => e.target.style.transform = 'translateY(-2px) scale(1.02)'}
          onMouseOut={(e) => e.target.style.transform = 'translateY(0) scale(1)'}
        >
          Enter Dashboard
        </button>
      </div>

      <style jsx global>{`
        @keyframes phonepe-pop {
          0% { transform: scale(0); }
          100% { transform: scale(1); }
        }
        @keyframes phonepe-check {
          to { stroke-dashoffset: 0; }
        }
        @keyframes phonepe-ripple {
          0% { transform: scale(0.8); opacity: 0.6; }
          100% { transform: scale(1.6); opacity: 0; }
        }
      `}</style>
    </div>
  )
}
