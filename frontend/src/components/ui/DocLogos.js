'use client'

// Word Logo SVG — Microsoft blue W mark
export function WordLogo({ size = 24 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect width="32" height="32" rx="4" fill="#2B579A"/>
      <path d="M7 8H17L19 8V24H7V8Z" fill="#1A3F6F"/>
      <rect x="11" y="6" width="16" height="20" rx="1" fill="#DEECF9"/>
      <path d="M6 8L18 6V26L6 24V8Z" fill="#2B579A"/>
      <text x="8" y="19.5" fontFamily="Arial, sans-serif" fontWeight="bold" fontSize="11" fill="white">W</text>
    </svg>
  )
}

// PDF Logo SVG — Adobe red PDF mark
export function PdfLogo({ size = 24 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect width="32" height="32" rx="4" fill="#E2231A"/>
      <rect x="5" y="4" width="22" height="24" rx="2" fill="#B71C1C"/>
      <rect x="7" y="6" width="18" height="20" rx="1" fill="#FFCDD2"/>
      <text x="8" y="20" fontFamily="Arial, sans-serif" fontWeight="bold" fontSize="8.5" fill="#B71C1C">PDF</text>
    </svg>
  )
}

// Lock icon for the "locked document" visual
export function LockIcon({ size = 14, color = 'currentColor' }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
      <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
    </svg>
  )
}

// Unlock icon for when document is expanded
export function UnlockIcon({ size = 14, color = 'currentColor' }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
      <path d="M7 11V7a5 5 0 0 1 9.9-1"/>
    </svg>
  )
}
