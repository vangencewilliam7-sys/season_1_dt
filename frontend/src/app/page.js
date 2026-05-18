'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { getSupabaseClient, hasSupabaseConfig } from '../lib/supabase'
import './auth/auth.css'

export default function RootPage() {
  const router = useRouter()
  const [sector, setSector] = useState('Healthcare')
  const [domain, setDomain] = useState('Doctor')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleSignIn(event) {
    event.preventDefault()
    setLoading(true)
    setError('')

    const dummyAccounts = [
      { email: 'doctor@hospital.com', pass: 'password123', targetSector: 'Healthcare', targetRole: 'Doctor' },
      { email: 'manager@services.com', pass: 'password123', targetSector: 'Services', targetRole: 'Project Manager' },
      { email: 'tutor@academy.com', pass: 'password123', targetSector: 'Education', targetRole: 'Tutor' },
    ]

    const matched = dummyAccounts.find(a => a.email === email && a.pass === password)

    if (matched) {
      setTimeout(() => {
        setLoading(false)
        // Auto-select correct sector/role for the dummy user
        setSector(matched.targetSector)
        setDomain(matched.targetRole)
        router.push('/dashboard')
      }, 800)
      return
    }

    if (!hasSupabaseConfig) {
      setLoading(false)
      setError('Invalid credentials. Please use one of the dummy accounts or configure Supabase.')
      return
    }

    const supabase = getSupabaseClient()
    const { error: authError } = await supabase.auth.signInWithPassword({
      email,
      password,
    })

    if (authError) {
      setError(authError.message)
      setLoading(false)
      return
    }

    router.push('/dashboard')
  }

  return (
    <div className="auth-shell">
      <div className="auth-card fade-up">
        <div className="auth-header">
          <h1 className="auth-title">Welcome back</h1>
        </div>

        {error ? <div className="auth-error">{error}</div> : null}

        <form className="auth-form" onSubmit={handleSignIn}>
          {/* Sector Dropdown */}
          <div className="auth-field">
            <label className="auth-label" htmlFor="sector">Sector</label>
            <select
              id="sector"
              className="auth-input"
              value={sector}
              onChange={(e) => setSector(e.target.value)}
              required
            >
              <option value="Healthcare">Healthcare</option>
              <option value="Services">Services</option>
              <option value="Education">Education</option>
            </select>
          </div>

          {/* Role Dropdown */}
          <div className="auth-field">
            <label className="auth-label" htmlFor="domain">Role</label>
            <select
              id="domain"
              className="auth-input"
              value={domain}
              onChange={(e) => setDomain(e.target.value)}
              required
            >
              <option value="Doctor">Doctor</option>
              <option value="Project Manager">Project Manager</option>
              <option value="Tutor">Tutor</option>
            </select>
          </div>

          <div className="auth-field">
            <label className="auth-label" htmlFor="email">Email address</label>
            <input
              id="email"
              type="email"
              className="auth-input"
              placeholder="user@example.com"
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
            disabled={loading || !email || !password}
          >
            {loading ? <span className="auth-spinner" /> : 'Sign In'}
          </button>
        </form>

        {!hasSupabaseConfig ? (
          <p className="auth-note">
            Supabase browser auth is not configured, falling back to local navigation.
          </p>
        ) : null}

        <div className="auth-footer">
          Don&apos;t have an account?{' '}
          <Link href="/auth/signup" className="auth-link">Create one</Link>
        </div>
      </div>
    </div>
  )
}
