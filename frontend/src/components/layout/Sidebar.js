'use client'
import Link from 'next/link'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { getSupabaseClient, hasSupabaseConfig } from '../../lib/supabase'
import { 
  DashboardIcon, 
  KnowledgeIcon, 
  PersonaIcon, 
  ChatIcon, 
  GlassBoxIcon, 
  SkillsIcon 
} from '../ui/SparkleIcons'

const NAV = [
  { href: '/dashboard',      label: 'Dashboard',      icon: <DashboardIcon /> },
  { href: '/knowledge-hub',  label: 'Knowledge Hub',  icon: <KnowledgeIcon /> },
  { href: '/persona',        label: 'Persona',        icon: <PersonaIcon /> },
  { href: '/chat',           label: 'Twin Chat',      icon: <ChatIcon /> },
  { href: '/glass-box',      label: 'Glass Box',      icon: <GlassBoxIcon /> },
  { href: '/skills',         label: 'Skills',         icon: <SkillsIcon /> },
]

export default function Sidebar({ active }) {
  const router = useRouter()
  const [userName, setUserName] = useState('')

  useEffect(() => {
    if (!hasSupabaseConfig) {
      return
    }

    const supabase = getSupabaseClient()
    supabase.auth.getUser().then(({ data }) => {
      const fullName = data?.user?.user_metadata?.full_name
      setUserName(fullName || '')
    })
  }, [])

  async function handleSignOut() {
    if (hasSupabaseConfig) {
      const supabase = getSupabaseClient()
      await supabase.auth.signOut()
      setUserName('')
    }

    router.push('/auth/signin')
  }

  return (
    <aside style={{
      width: 240,
      height: '100vh',
      position: 'sticky',
      top: 0,
      background: '#FFFFFF',
      borderRight: '1px solid #E2E8F0',
      display: 'flex',
      flexDirection: 'column',
      padding: '24px 0',
      flexShrink: 0,
      overflowY: 'auto'
    }}>
      {/* Logo */}
      <div style={{ padding: '0 20px 32px' }}>
        <div style={{
          display: 'flex', alignItems: 'center', gap: 12,
          padding: '14px 16px',
          background: 'linear-gradient(135deg, #03045E 0%, #0077B6 100%)',
          borderRadius: '12px',
          boxShadow: '0 4px 16px rgba(3,4,94,0.15)',
        }}>
          <span style={{ fontSize: 22, filter: 'brightness(10)' }}>✨</span>
          <div>
            <div style={{ fontSize: 14, fontWeight: 700, color: '#FFFFFF', lineHeight: 1.2 }}>Expert Twin</div>

          </div>
        </div>
      </div>

      {/* Nav */}
      <nav style={{ flex: 1, padding: '0 12px' }}>
        <div style={{ fontSize: 11, fontWeight: 600, color: '#94A3B8', padding: '0 12px 8px', textTransform: 'uppercase', letterSpacing: '1px' }}>
          Navigation
        </div>
        {NAV.map(item => {
          const isActive =
            active === item.href || (item.href === '/' && active === '/dashboard')
          return (
            <Link key={item.href} href={item.href} style={{ textDecoration: 'none' }}>
              <div style={{
                display: 'flex', alignItems: 'center', gap: 12,
                padding: '12px 14px',
                borderRadius: '8px',
                marginBottom: 4,
                color: isActive ? '#0077B6' : '#475569',
                background: isActive ? '#CAF0F8' : 'transparent',
                fontWeight: isActive ? 600 : 500,
                fontSize: 14,
                cursor: 'pointer',
                transition: 'all 0.2s ease',
              }}>
                <span style={{ display: 'flex', alignItems: 'center', opacity: isActive ? 1 : 0.6 }}>
                  {item.icon}
                </span>
                {item.label}
              </div>
            </Link>
          )
        })}
      </nav>

      {/* Footer session strip */}
      <div style={{ padding: '16px 20px', borderTop: '1px solid #E2E8F0' }}>
        {userName ? (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            background: '#F8FAFC',
            padding: '8px 12px',
            borderRadius: '10px',
            border: '1px solid #E2E8F0'
          }}>
            <div style={{ fontSize: 12.5, color: '#03045E', fontWeight: 700, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: 110 }}>
              {userName}
            </div>
            <button
              onClick={handleSignOut}
              style={{
                border: 'none',
                background: '#FEE2E2',
                padding: '5px 10px',
                borderRadius: '6px',
                fontSize: 11.5,
                color: '#EF4444',
                fontWeight: 700,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: 5,
                transition: 'all 0.2s',
              }}
              title="Sign out"
            >
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                <polyline points="16 17 21 12 16 7"></polyline>
                <line x1="21" y1="12" x2="9" y2="12"></line>
              </svg>
              Exit
            </button>
          </div>
        ) : (
          <button
            onClick={handleSignOut}
            style={{
              width: '100%',
              border: '1px solid #E2E8F0',
              background: '#F8FAFC',
              padding: '10px 16px',
              borderRadius: '10px',
              fontSize: 13,
              color: '#475569',
              fontWeight: 700,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 8,
              transition: 'all 0.2s',
              boxShadow: '0 2px 4px rgba(0,0,0,0.02)'
            }}
            title="Sign out session"
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#64748B" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
              <polyline points="16 17 21 12 16 7"></polyline>
              <line x1="21" y1="12" x2="9" y2="12"></line>
            </svg>
            Sign out
          </button>
        )}
      </div>
    </aside>
  )
}
