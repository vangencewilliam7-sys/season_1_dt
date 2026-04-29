'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { supabase } from '../../../lib/supabase';
import '../auth.css';

export default function SignUpPage() {
  const router = useRouter();
  const [role, setRole] = useState('doctor'); // 'doctor' or 'patient'
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSignUp = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    if (!process.env.NEXT_PUBLIC_SUPABASE_URL) {
      setTimeout(() => {
        setLoading(false);
        router.push(role === 'doctor' ? '/dashboard' : '/chat');
      }, 1000);
      return;
    }

    const { error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: {
          full_name: fullName,
          role: role,
        }
      }
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
          <h1 className="auth-title">Create Profile</h1>
          <p className="auth-subtitle">Register to access the Brain Factory</p>
        </div>

        {error && <div className="auth-error">{error}</div>}

        <form className="auth-form" onSubmit={handleSignUp}>
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
            <label className="input-label" htmlFor="fullName">Full Name</label>
            <input
              id="fullName"
              type="text"
              className="auth-input"
              placeholder="Dr. Sarah Johnson"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              required
            />
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
            disabled={loading || !email || !password || !fullName}
          >
            {loading ? <span className="auth-spinner" /> : 'Create Account'}
          </button>
        </form>

        <div className="auth-footer">
          Already have an account?{' '}
          <Link href="/auth/signin" className="auth-link">
            Sign In
          </Link>
        </div>
      </div>
    </div>
  );
}
