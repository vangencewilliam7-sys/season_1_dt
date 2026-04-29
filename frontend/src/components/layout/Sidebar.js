'use client'
import Link from 'next/link'
import { 
  DashboardIcon, 
  KnowledgeIcon, 
  PersonaIcon, 
  ChatIcon, 
  GlassBoxIcon, 
  SkillsIcon 
} from '../ui/SparkleIcons'

const NAV = [
  { href: '/',               label: 'Dashboard',      icon: <DashboardIcon /> },
  { href: '/knowledge-hub',  label: 'Knowledge Hub',  icon: <KnowledgeIcon /> },
  { href: '/persona',        label: 'Persona',        icon: <PersonaIcon /> },
  { href: '/chat',           label: 'Twin Chat',      icon: <ChatIcon /> },
  { href: '/glass-box',      label: 'Glass Box',      icon: <GlassBoxIcon /> },
  { href: '/skills',         label: 'Skills',         icon: <SkillsIcon /> },
]

export default function Sidebar({ active }) {
  return (
    <aside style={{
      width: 240,
      minHeight: '100vh',
      background: '#FFFFFF',
      borderRight: '1px solid #E2E8F0',
      display: 'flex',
      flexDirection: 'column',
      padding: '24px 0',
      flexShrink: 0,
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
          <span style={{ fontSize: 22, filter: 'brightness(10)' }}>⚕</span>
          <div>
            <div style={{ fontSize: 14, fontWeight: 700, color: '#FFFFFF', lineHeight: 1.2 }}>Doctor Twin</div>
            <div style={{ fontSize: 10, color: 'rgba(255,255,255,0.75)', fontWeight: 600, letterSpacing: '0.5px' }}>SEASON 1 · DT</div>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav style={{ flex: 1, padding: '0 12px' }}>
        <div style={{ fontSize: 11, fontWeight: 600, color: '#94A3B8', padding: '0 12px 8px', textTransform: 'uppercase', letterSpacing: '1px' }}>
          Navigation
        </div>
        {NAV.map(item => {
          const isActive = active === item.href
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

      {/* Status dot */}
      <div style={{ padding: '16px 20px', borderTop: '1px solid #E2E8F0' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 12, color: '#64748B' }}>
          <span style={{
            width: 7, height: 7, borderRadius: '50%',
            background: '#00B4D8',
            display: 'inline-block',
          }}/>
          Core DT System Active
        </div>
      </div>
    </aside>
  )
}
