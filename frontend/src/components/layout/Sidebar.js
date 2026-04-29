'use client'
import Link from 'next/link'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { supabase } from '../../lib/supabase'

const NAV = [
  { href: '/',               label: 'Dashboard',      icon: '◈' },
  { href: '/knowledge-hub',  label: 'Knowledge Hub',  icon: '⬡' },
  { href: '/persona',        label: 'Persona',        icon: '◎' },
  { href: '/chat',           label: 'Twin Chat',      icon: '◇' },
  { href: '/glass-box',      label: 'Glass Box',      icon: '🔍' },
  { href: '/skills',         label: 'Skills',         icon: '◆' },
]

export default function Sidebar({ active }) {
  const router = useRouter()
  const [user, setUser] = useState(null)

  useEffect(() => {
    supabase.auth.getUser().then(({ data }) => {
      setUser(data.user)
    })
  }, [])

  const handleSignOut = async () => {
    await supabase.auth.signOut()
    router.push('/auth/signin')
  }

  return (
    <aside style={{
      width: 220,
      minHeight: '100vh',
      background: 'var(--bg-surface)',
      borderRight: '1px solid var(--border)',
      display: 'flex',
      flexDirection: 'column',
      padding: '24px 0',
      flexShrink: 0,
    }}>
      {/* Logo */}
      <div style={{ padding: '0 20px 28px' }}>
        <div style={{
          display: 'flex', alignItems: 'center', gap: 10,
          padding: '10px 14px',
          background: 'var(--accent-glow)',
          borderRadius: 'var(--radius-md)',
          border: '1px solid var(--accent-primary)30',
        }}>
          <span style={{ fontSize: 22 }}>⚕</span>
          <div>
            <div style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-primary)', lineHeight: 1.2 }}>Doctor Twin</div>
            <div style={{ fontSize: 10, color: 'var(--accent-primary)', fontWeight: 600 }}>SEASON 1 · DT</div>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav style={{ flex: 1, padding: '0 12px' }}>
        {NAV.map(item => {
          const isActive = active === item.href
          return (
            <Link key={item.href} href={item.href} style={{ textDecoration: 'none' }}>
              <div style={{
                display: 'flex', alignItems: 'center', gap: 10,
                padding: '10px 12px',
                borderRadius: 'var(--radius-sm)',
                marginBottom: 4,
                color: isActive ? 'var(--accent-primary)' : 'var(--text-secondary)',
                background: isActive ? 'var(--accent-glow)' : 'transparent',
                border: isActive ? '1px solid var(--accent-primary)30' : '1px solid transparent',
                fontWeight: isActive ? 600 : 400,
                fontSize: 13,
                cursor: 'pointer',
                transition: 'all 0.2s ease',
              }}>
                <span style={{ fontSize: 15 }}>{item.icon}</span>
                {item.label}
              </div>
            </Link>
          )
        })}
      </nav>

      {/* Status & Profile */}
      <div style={{ padding: '16px 20px', borderTop: '1px solid var(--border)', display: 'flex', flexDirection: 'column', gap: 12 }}>
        
        {/* Profile Card */}
        {user && (
          <div style={{
            display: 'flex', alignItems: 'center', justifyContent: 'space-between',
            background: 'var(--bg-elevated)', padding: '10px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border)'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, overflow: 'hidden' }}>
              <div style={{
                width: 28, height: 28, borderRadius: '50%', background: 'var(--accent-primary)', color: '#fff',
                display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 12, fontWeight: 'bold'
              }}>
                {user?.user_metadata?.full_name?.[0]?.toUpperCase() || 'D'}
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
                <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-primary)', whiteSpace: 'nowrap', textOverflow: 'ellipsis', overflow: 'hidden' }}>
                  {user?.user_metadata?.full_name || 'Doctor'}
                </span>
                <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>Logged in</span>
              </div>
            </div>
            <button onClick={handleSignOut} title="Sign Out" style={{
              background: 'transparent', border: 'none', color: 'var(--accent-red)', cursor: 'pointer', fontSize: 14, padding: 4
            }}>
              ⏻
            </button>
          </div>
        )}

        <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 12, color: 'var(--text-secondary)' }}>
          <span style={{
            width: 7, height: 7, borderRadius: '50%',
            background: 'var(--accent-green)',
            animation: 'blink 2s ease infinite',
            display: 'inline-block',
          }}/>
          Backend running
        </div>
      </div>
    </aside>
  )
}
