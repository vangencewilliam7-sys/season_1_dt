'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { getSupabaseClient, hasSupabaseConfig } from '../../../lib/supabase'
import '../auth.css'

export default function SignUpPage() {
  const router = useRouter()
  const [role, setRole] = useState('doctor')
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleSignUp(event) {
    event.preventDefault()
    setLoading(true)
    setError('')

    if (!hasSupabaseConfig) {
      setTimeout(() => {
        setLoading(false)
        router.push(role === 'doctor' ? '/dashboard' : '/chat')
      }, 500)
      return
    }

    const supabase = getSupabaseClient()
    const { error: authError } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: {
          full_name: fullName,
          role,
        },
      },
    })

    if (authError) {
      setError(authError.message)
      setLoading(false)
      return
    }

    router.push(role === 'doctor' ? '/dashboard' : '/chat')
  }

  return (
    <div className="auth-shell">
      <div className="auth-card fade-up">
        <div className="auth-brand">
          <span className="auth-brand-mark">⚕</span>
          <div className="auth-brand-copy">
            <span className="auth-brand-title">Doctor Twin</span>
            <span className="auth-brand-caption">Season 1 · DT</span>
          </div>
        </div>

        <div className="auth-header">
          <h1 className="auth-title">Create profile</h1>
          <p className="auth-subtitle">
            Register to access the Brain Factory.
          </p>
        </div>

        {error ? <div className="auth-error">{error}</div> : null}

        <form className="auth-form" onSubmit={handleSignUp}>
          <div className="auth-row">
            {['doctor', 'patient'].map((nextRole) => (
              <label
                key={nextRole}
                className={`auth-role ${role === nextRole ? 'active' : ''}`}
              >
                <input
                  type="radio"
                  name="role"
                  value={nextRole}
                  checked={role === nextRole}
                  onChange={() => setRole(nextRole)}
                />
                <span>{nextRole === 'doctor' ? 'Doctor' : 'Patient'}</span>
              </label>
            ))}
          </div>

          <div className="auth-field">
            <label className="auth-label" htmlFor="fullName">Full name</label>
            <input
              id="fullName"
              type="text"
              className="auth-input"
              placeholder="Dr. Sarah Johnson"
              value={fullName}
              onChange={(event) => setFullName(event.target.value)}
              required
            />
          </div>

          <div className="auth-field">
            <label className="auth-label" htmlFor="email">Email address</label>
            <input
              id="email"
              type="email"
              className="auth-input"
              placeholder="doctor@hospital.com"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />
          </div>

          <div className="auth-field">
            <label className="auth-label" htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              className="auth-input"
              placeholder="••••••••"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </div>

          <button
            type="submit"
            className="auth-button"
            disabled={loading || !fullName || !email || !password}
          >
            {loading ? <span className="auth-spinner" /> : 'Create Account'}
          </button>
        </form>

        {!hasSupabaseConfig ? (
          <p className="auth-note">
            Supabase browser auth is not configured in `.env.local`, so this route falls back to local navigation for development.
          </p>
        ) : null}

        <div className="auth-footer">
          Already have an account?{' '}
          <Link href="/auth/signin" className="auth-link">Sign in</Link>
        </div>
      </div>
    </div>
  )
}
