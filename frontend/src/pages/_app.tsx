import '../styles/globals.css'
import type { AppProps } from 'next/app'
import Link from 'next/link'
import { useRouter } from 'next/router'

export default function App({ Component, pageProps }: AppProps) {
  const router = useRouter()
  const showSidebar = router.pathname !== '/'

  return (
    <div style={{ display: 'flex', height: showSidebar ? '100vh' : 'auto' }}>
      {showSidebar && <Sidebar />}
      <main style={{ flex: 1, overflowY: 'auto', backgroundColor: '#f3f4f6' }}>
        <Component {...pageProps} />
      </main>
    </div>
  )
}

function Sidebar() {
  const router = useRouter()

  return (
    <aside style={{ width: '256px', backgroundColor: '#111827', color: 'white', padding: '24px', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}>
      <h1 style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '32px' }}>👓 Eyewear</h1>
      
      <nav style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <NavLink href="/dashboard" label="Dashboard" active={router.pathname === '/dashboard'} />
        <NavLink href="/orders" label="Orders" active={router.pathname.startsWith('/orders')} />
        <NavLink href="/inventory" label="Inventory" active={router.pathname === '/inventory'} />
      </nav>
    </aside>
  )
}

function NavLink({ href, label, active }: { href: string; label: string; active: boolean }) {
  return (
    <Link 
      href={href}
      style={{
        display: 'block',
        padding: '8px 16px',
        borderRadius: '6px',
        backgroundColor: active ? '#2563eb' : 'transparent',
        color: 'white',
        textDecoration: 'none',
        transition: 'background-color 0.2s'
      }}
      onMouseEnter={(e) => {
        if (!active) e.currentTarget.style.backgroundColor = '#1f2937'
      }}
      onMouseLeave={(e) => {
        if (!active) e.currentTarget.style.backgroundColor = 'transparent'
      }}
    >
      {label}
    </Link>
  )
}