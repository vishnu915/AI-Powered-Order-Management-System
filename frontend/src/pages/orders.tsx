import { useState, useEffect } from 'react'
import axios from 'axios'
import Link from 'next/link'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function Orders() {
  const [orders, setOrders] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchOrders()
  }, [])

  const fetchOrders = async () => {
    try {
      const res = await axios.get(`${API_BASE}/api/orders`)
      setOrders(res.data)
    } catch (error) {
      console.error('Error fetching orders:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <div style={{ padding: '32px' }}>Loading...</div>

  return (
    <div style={{ padding: '32px' }}>
      <h1>All Orders</h1>

      <table style={{ width: '100%', borderCollapse: 'collapse', backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
        <thead>
          <tr style={{ backgroundColor: '#f9fafb', borderBottom: '1px solid #e5e7eb' }}>
            <th style={{ padding: '12px 16px', textAlign: 'left', fontWeight: '600' }}>Order ID</th>
            <th style={{ padding: '12px 16px', textAlign: 'left', fontWeight: '600' }}>Customer</th>
            <th style={{ padding: '12px 16px', textAlign: 'left', fontWeight: '600' }}>Email</th>
            <th style={{ padding: '12px 16px', textAlign: 'left', fontWeight: '600' }}>Status</th>
            <th style={{ padding: '12px 16px', textAlign: 'left', fontWeight: '600' }}>Action</th>
          </tr>
        </thead>
        <tbody>
          {orders.map((order) => (
            <tr key={order.id} style={{ borderBottom: '1px solid #e5e7eb' }}>
              <td style={{ padding: '12px 16px', fontWeight: '500' }}>{order.order_id}</td>
              <td style={{ padding: '12px 16px' }}>{order.customer_name}</td>
              <td style={{ padding: '12px 16px' }}>{order.customer_email}</td>
              <td style={{ padding: '12px 16px' }}>
                <span style={{ backgroundColor: '#bfdbfe', color: '#1e40af', padding: '4px 8px', borderRadius: '4px', fontSize: '12px' }}>
                  {order.status}
                </span>
              </td>
              <td style={{ padding: '12px 16px' }}>
                <Link href={`/orders/${order.id}`} style={{ color: '#2563eb', textDecoration: 'none' }}>
                  View
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}