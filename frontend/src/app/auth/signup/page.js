'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { getSupabaseClient, hasSupabaseConfig } from '../../../lib/supabase'
import '../auth.css'

export default function SignUpPage() {
  const router = useRouter()
  const [sector, setSector] = useState('Healthcare')
  const [role, setRole] = useState('Doctor')
  const [firstName, setFirstName] = useState('')
  const [lastName, setLastName] = useState('')
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
        router.push('/dashboard')
      }, 500)
      return
    }

    const supabase = getSupabaseClient()
    const { error: authError } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: {
          first_name: firstName,
          last_name: lastName,
          sector,
          role,
        },
      },
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
          <h1 className="auth-title">Create profile</h1>
        </div>

        {error ? <div className="auth-error">{error}</div> : null}

        <form className="auth-form" onSubmit={handleSignUp}>
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
            <label className="auth-label" htmlFor="role">Role</label>
            <select
              id="role"
              className="auth-input"
              value={role}
              onChange={(e) => setRole(e.target.value)}
              required
            >
              <option value="Doctor">Doctor</option>
              <option value="Project Manager">Project Manager</option>
              <option value="Tutor">Tutor</option>
            </select>
          </div>

          <div style={{ display: 'flex', gap: 12 }}>
            <div className="auth-field" style={{ flex: 1 }}>
              <label className="auth-label" htmlFor="firstName">First name</label>
              <input
                id="firstName"
                type="text"
                className="auth-input"
                placeholder="Jane"
                value={firstName}
                onChange={(event) => setFirstName(event.target.value)}
                required
              />
            </div>
            <div className="auth-field" style={{ flex: 1 }}>
              <label className="auth-label" htmlFor="lastName">Last name</label>
              <input
                id="lastName"
                type="text"
                className="auth-input"
                placeholder="Doe"
                value={lastName}
                onChange={(event) => setLastName(event.target.value)}
                required
              />
            </div>
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
            disabled={loading || !firstName || !lastName || !email || !password}
          >
            {loading ? <span className="auth-spinner" /> : 'Create Account'}
          </button>
        </form>

        {!hasSupabaseConfig ? (
          <p className="auth-note">
            Supabase browser auth is not configured, falling back to local navigation.
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
