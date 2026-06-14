import Link from 'next/link'

export default function Home() {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #3b82f6 0%, #a855f7 100%)',
      color: 'white',
      textAlign: 'center'
    }}>
      <h1 style={{ fontSize: '48px', fontWeight: 'bold', marginBottom: '16px' }}>👓 Eyewear Order Management</h1>
      <p style={{ fontSize: '20px', marginBottom: '32px' }}>AI-Powered Order Management System</p>
      
      <Link 
        href="/dashboard"
        style={{
          display: 'inline-block',
          backgroundColor: 'white',
          color: '#3b82f6',
          padding: '12px 32px',
          borderRadius: '6px',
          fontWeight: 'bold',
          textDecoration: 'none',
          transition: 'background-color 0.2s'
        }}
        onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f3f4f6'}
        onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'white'}
      >
        Go to Dashboard →
      </Link>
    </div>
  )
}