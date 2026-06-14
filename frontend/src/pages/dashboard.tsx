import { useState, useEffect } from 'react'
import axios from 'axios'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function Dashboard() {
  const [stats, setStats] = useState<any>(null)
  const [orders, setOrders] = useState<any[]>([])
  const [filters, setFilters] = useState({ status: '', lens_type: '', location: '' })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 30000)
    return () => clearInterval(interval)
  }, [filters])

  const fetchData = async () => {
    try {
      const [statsRes, ordersRes] = await Promise.all([
        axios.get(`${API_BASE}/api/dashboard/stats`),
        axios.get(`${API_BASE}/api/dashboard/orders`, { params: filters })
      ])
      
      setStats(statsRes.data)
      setOrders(ordersRes.data)
    } catch (error) {
      console.error('Error fetching data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div style={{ padding: '32px', fontSize: '20px' }}>Loading...</div>
  }

  return (
    <div style={{ padding: '32px' }}>
      <h1>Order Management Dashboard</h1>

      {/* KPI Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '16px', marginBottom: '32px' }}>
        <KPICard title="Total Orders" value={stats?.total_orders} />
        <KPICard title="Pending" value={stats?.pending_orders} />
        <KPICard title="Delivered" value={stats?.delivered_orders} />
        <KPICard title="Breach Rate" value={`${stats?.breach_rate}%`} color="danger" />
      </div>

      {/* Filters */}
      <div style={{ backgroundColor: 'white', padding: '24px', borderRadius: '8px', marginBottom: '32px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
        <h2>Filters</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
          <select
            value={filters.status}
            onChange={(e) => setFilters({ ...filters, status: e.target.value })}
            style={{ padding: '8px 12px', border: '1px solid #d1d5db', borderRadius: '6px' }}
          >
            <option value="">All Status</option>
            <option value="pending">Pending</option>
            <option value="confirmed">Confirmed</option>
            <option value="qc_pass">QC Pass</option>
            <option value="delivered">Delivered</option>
          </select>

          <select
            value={filters.lens_type}
            onChange={(e) => setFilters({ ...filters, lens_type: e.target.value })}
            style={{ padding: '8px 12px', border: '1px solid #d1d5db', borderRadius: '6px' }}
          >
            <option value="">All Lens Types</option>
            <option value="single_vision">Single Vision</option>
            <option value="bifocal">Bifocal</option>
            <option value="progressive">Progressive</option>
          </select>

          <select
            value={filters.location}
            onChange={(e) => setFilters({ ...filters, location: e.target.value })}
            style={{ padding: '8px 12px', border: '1px solid #d1d5db', borderRadius: '6px' }}
          >
            <option value="">All Locations</option>
            <option value="NYC">NYC</option>
            <option value="LA">LA</option>
            <option value="Chicago">Chicago</option>
          </select>
        </div>
      </div>

      {/* Orders Table */}
      <table style={{ width: '100%', borderCollapse: 'collapse', backgroundColor: 'white', borderRadius: '8px', overflow: 'hidden', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
        <thead>
          <tr style={{ backgroundColor: '#f9fafb', borderBottom: '1px solid #e5e7eb' }}>
            <th style={{ padding: '12px 16px', textAlign: 'left', fontWeight: '600' }}>Order ID</th>
            <th style={{ padding: '12px 16px', textAlign: 'left', fontWeight: '600' }}>Customer</th>
            <th style={{ padding: '12px 16px', textAlign: 'left', fontWeight: '600' }}>Lens Type</th>
            <th style={{ padding: '12px 16px', textAlign: 'left', fontWeight: '600' }}>Status</th>
            <th style={{ padding: '12px 16px', textAlign: 'left', fontWeight: '600' }}>Hours Left</th>
            <th style={{ padding: '12px 16px', textAlign: 'left', fontWeight: '600' }}>Breach</th>
          </tr>
        </thead>
        <tbody>
          {orders.map((order) => (
            <tr key={order.id} style={{ borderBottom: '1px solid #e5e7eb' }}>
              <td style={{ padding: '12px 16px', fontWeight: '500' }}>{order.order_id}</td>
              <td style={{ padding: '12px 16px' }}>{order.customer}</td>
              <td style={{ padding: '12px 16px' }}>{order.lens_type}</td>
              <td style={{ padding: '12px 16px' }}>
                <span style={{
                  display: 'inline-block',
                  padding: '4px 8px',
                  borderRadius: '4px',
                  fontSize: '12px',
                  fontWeight: '600',
                  backgroundColor: getStatusBgColor(order.status),
                  color: getStatusTextColor(order.status)
                }}>
                  {order.status}
                </span>
              </td>
              <td style={{ padding: '12px 16px' }}>{Math.round(order.hours_remaining)}</td>
              <td style={{ padding: '12px 16px', color: order.is_breached ? '#dc2626' : '#059669', fontWeight: 'bold' }}>
                {order.is_breached ? '⚠️ BREACHED' : '✓'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function KPICard({ title, value, color = 'info' }: any) {
  const bgColors: any = {
    info: '#dbeafe',
    danger: '#fee2e2'
  }
  const textColors: any = {
    info: '#1e40af',
    danger: '#7f1d1d'
  }

  return (
    <div style={{
      backgroundColor: bgColors[color],
      padding: '24px',
      borderRadius: '8px',
      boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
      color: textColors[color]
    }}>
      <p style={{ fontSize: '14px', marginBottom: '8px' }}>{title}</p>
      <p style={{ fontSize: '32px', fontWeight: 'bold' }}>{value}</p>
    </div>
  )
}

function getStatusBgColor(status: string) {
  const colors: any = {
    pending: '#fef3c7',
    confirmed: '#bfdbfe',
    qc_pass: '#bbf7d0',
    qc_fail: '#fecaca',
    delivered: '#bbf7d0'
  }
  return colors[status] || '#e5e7eb'
}

function getStatusTextColor(status: string) {
  const colors: any = {
    pending: '#92400e',
    confirmed: '#1e40af',
    qc_pass: '#065f46',
    qc_fail: '#7f1d1d',
    delivered: '#065f46'
  }
  return colors[status] || '#374151'
}