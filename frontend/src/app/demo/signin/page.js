'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'

export default function DemoSigninPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  const handleSignin = (e) => {
    e.preventDefault()
    setLoading(true)

    setTimeout(() => {
      setLoading(false)
      router.push('/demo')
    }, 1200)
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #0F172A 100%)',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '40px 24px',
      fontFamily: 'Inter, system-ui, sans-serif',
    }}>

      {/* Brand Header */}
      <div style={{ textAlign: 'center', marginBottom: '40px' }}>
        <div style={{
          display: 'inline-flex', alignItems: 'center', gap: '10px',
          background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)',
          borderRadius: '10px', padding: '8px 16px', marginBottom: '20px',
        }}>
          <span style={{ fontSize: '18px' }}>🏥</span>
          <span style={{ color: '#94A3B8', fontSize: '12px', fontWeight: 600, letterSpacing: '0.1em', textTransform: 'uppercase' }}>
            Mentor Preview Sign In
          </span>
        </div>
        <h1 style={{
          fontSize: '32px', fontWeight: 800, color: '#F8FAFC',
          lineHeight: 1.2, marginBottom: '12px', letterSpacing: '-0.02em',
        }}>
          Welcome Back, Doctor.
        </h1>
        <p style={{ color: '#94A3B8', fontSize: '15px', maxWidth: '400px', lineHeight: 1.6, margin: '0 auto' }}>
          Sign in to access your digital twin dashboard and review consultation logs.
        </p>
      </div>

      {/* Signin Form Card */}
      <div style={{
        background: 'rgba(255,255,255,0.03)',
        border: '1px solid rgba(255,255,255,0.1)',
        borderRadius: '24px',
        padding: '40px',
        width: '100%',
        maxWidth: '460px',
        boxShadow: '0 20px 40px rgba(0,0,0,0.2)',
        backdropFilter: 'blur(12px)',
      }}>
        <form onSubmit={handleSignin} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>

          <div>
            <label htmlFor="email" style={{ display: 'block', color: '#94A3B8', fontSize: '13px', fontWeight: 600, marginBottom: '8px' }}>
              Email Address
            </label>
            <input
              id="email"
              type="email"
              required
              placeholder="dr.venkatesh@hospital.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              style={{
                width: '100%', padding: '14px 16px',
                background: 'rgba(0,0,0,0.2)', border: '1px solid rgba(255,255,255,0.1)',
                borderRadius: '12px', color: '#F8FAFC', fontSize: '15px', outline: 'none',
                transition: 'border-color 0.2s',
              }}
              onFocus={(e) => e.target.style.borderColor = '#3B82F6'}
              onBlur={(e) => e.target.style.borderColor = 'rgba(255,255,255,0.1)'}
            />
          </div>

          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <label htmlFor="password" style={{ color: '#94A3B8', fontSize: '13px', fontWeight: 600 }}>
                Password
              </label>
              <span style={{ color: '#60A5FA', fontSize: '12px', cursor: 'pointer' }}>Forgot?</span>
            </div>
            <input
              id="password"
              type="password"
              required
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={{
                width: '100%', padding: '14px 16px',
                background: 'rgba(0,0,0,0.2)', border: '1px solid rgba(255,255,255,0.1)',
                borderRadius: '12px', color: '#F8FAFC', fontSize: '15px', outline: 'none',
                transition: 'border-color 0.2s',
              }}
              onFocus={(e) => e.target.style.borderColor = '#3B82F6'}
              onBlur={(e) => e.target.style.borderColor = 'rgba(255,255,255,0.1)'}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            style={{
              width: '100%', padding: '16px', marginTop: '10px',
              background: 'linear-gradient(135deg, #0EA5E9, #14B8A6)',
              color: '#FFFFFF', fontSize: '15px', fontWeight: 700,
              border: 'none', borderRadius: '12px', cursor: loading ? 'not-allowed' : 'pointer',
              opacity: loading ? 0.7 : 1, transition: 'all 0.2s',
              boxShadow: '0 4px 12px rgba(14, 165, 233, 0.3)',
            }}
          >
            {loading ? 'Authenticating...' : 'Sign In →'}
          </button>
        </form>

        <div style={{ marginTop: '24px', textAlign: 'center', fontSize: '13px', color: '#64748B' }}>
          New to the Digital Twin platform?{' '}
          <span
            onClick={() => router.push('/demo/signup')}
            style={{ color: '#60A5FA', cursor: 'pointer', fontWeight: 600 }}
          >
            Register here
          </span>
        </div>
      </div>
    </div>
  )
}
