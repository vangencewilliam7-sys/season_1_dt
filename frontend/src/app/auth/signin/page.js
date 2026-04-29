'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { supabase } from '../../../lib/supabase';
import '../auth.css';

export default function SignInPage() {
  const router = useRouter();
  const [role, setRole] = useState('doctor'); // 'doctor' or 'patient'
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSignIn = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    // Make sure supabase URL/Key are defined or graceful fallback for dev
    if (!process.env.NEXT_PUBLIC_SUPABASE_URL) {
      setTimeout(() => {
        setLoading(false);
        router.push(role === 'doctor' ? '/dashboard' : '/chat');
      }, 1000);
      return;
    }

    const { error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });

    if (error) {
      setError(error.message);
      setLoading(false);
    } else {
      router.push(role === 'doctor' ? '/dashboard' : '/chat');
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card glass fade-up">
        <div className="auth-header">
          <h1 className="auth-title">Welcome Back</h1>
          <p className="auth-subtitle">Sign in to your Digital Twin dashboard</p>
        </div>

        {error && <div className="auth-error">{error}</div>}

        <form className="auth-form" onSubmit={handleSignIn}>
          <div className="input-group" style={{ flexDirection: 'row', gap: '1rem', marginBottom: '0.5rem' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', color: 'var(--text-primary)' }}>
              <input 
                type="radio" 
                name="role" 
                value="doctor" 
                checked={role === 'doctor'} 
                onChange={() => setRole('doctor')} 
                style={{ accentColor: 'var(--accent-primary)' }}
              />
              Doctor
            </label>
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', color: 'var(--text-primary)' }}>
              <input 
                type="radio" 
                name="role" 
                value="patient" 
                checked={role === 'patient'} 
                onChange={() => setRole('patient')} 
                style={{ accentColor: 'var(--accent-teal)' }}
              />
              Patient
            </label>
          </div>

          <div className="input-group">
            <label className="input-label" htmlFor="email">Email Address</label>
            <input
              id="email"
              type="email"
              className="auth-input"
              placeholder="doctor@hospital.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="input-group">
            <label className="input-label" htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              className="auth-input"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
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

        <div className="auth-footer">
          Don't have an account?{' '}
          <Link href="/auth/signup" className="auth-link">
            Create Profile
          </Link>
        </div>
      </div>
    </div>
  );
}
