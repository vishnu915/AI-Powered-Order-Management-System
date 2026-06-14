import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import axios from 'axios'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function OrderDetail() {
  const router = useRouter()
  const { id } = router.query
  const [order, setOrder] = useState<any>(null)
  const [sla, setSla] = useState<any>(null)
  const [newStatus, setNewStatus] = useState('')
  const [notes, setNotes] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!id) return
    fetchOrderData()
  }, [id])

  const fetchOrderData = async () => {
    try {
      const [orderRes, slaRes] = await Promise.all([
        axios.get(`${API_BASE}/api/orders/${id}`),
        axios.get(`${API_BASE}/api/orders/${id}/sla-status`)
      ])
      
      setOrder(orderRes.data)
      setSla(slaRes.data)
      setNewStatus(orderRes.data.status)
    } catch (error) {
      console.error('Error fetching order:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleStatusUpdate = async () => {
    try {
      await axios.put(`${API_BASE}/api/orders/${id}`, { status: newStatus, notes })
      alert('Order updated successfully')
      fetchOrderData()
      setNotes('')
    } catch (error) {
      alert('Error updating order')
    }
  }

  if (loading) return <div style={{ padding: '32px' }}>Loading...</div>

  return (
    <div style={{ padding: '32px' }}>
      <button onClick={() => router.back()} style={{ color: '#2563eb', marginBottom: '24px', cursor: 'pointer', background: 'none', border: 'none' }}>
        ← Back
      </button>

      <div style={{ backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', padding: '32px', marginBottom: '32px' }}>
        <h1>{order?.order_id}</h1>

        {/* SLA Status */}
        <div style={{
          padding: '24px',
          borderRadius: '8px',
          marginBottom: '32px',
          backgroundColor: sla?.is_breached ? '#fee2e2' : '#d1fae5',
          color: sla?.is_breached ? '#7f1d1d' : '#065f46'
        }}>
          <p style={{ fontWeight: 'bold', marginBottom: '8px' }}>
            {sla?.is_breached ? '❌ BREACHED' : '✅ ON TRACK'}
          </p>
          <p>Hours Remaining: <strong>{Math.round(sla?.hours_remaining)}</strong> / {sla?.sla_hours}</p>
          <p>Breach Probability: <strong>{(sla?.breach_probability * 100).toFixed(1)}%</strong></p>
          <p>Predicted TAT: <strong>{sla?.predicted_tat_hours?.toFixed(1)} hours</strong></p>
        </div>

        {/* Order Details */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '32px', marginBottom: '32px' }}>
          <div>
            <h3>Customer Info</h3>
            <p><strong>Name:</strong> {order?.customer_name}</p>
            <p><strong>Email:</strong> {order?.customer_email}</p>
            <p><strong>Phone:</strong> {order?.customer_phone}</p>
          </div>

          <div>
            <h3>Lens Details</h3>
            <p><strong>Type:</strong> {order?.lens_type}</p>
            <p><strong>Index:</strong> {order?.lens_index}</p>
            <p><strong>Coating:</strong> {order?.coating}</p>
            <p><strong>Power (L):</strong> {order?.left_eye_power}</p>
            <p><strong>Power (R):</strong> {order?.right_eye_power}</p>
          </div>
        </div>

        {/* Status Update */}
        <div style={{ backgroundColor: '#f9fafb', padding: '24px', borderRadius: '8px' }}>
          <h3>Update Status</h3>
          
          <select
            value={newStatus}
            onChange={(e) => setNewStatus(e.target.value)}
            style={{ width: '100%', padding: '8px 12px', border: '1px solid #d1d5db', borderRadius: '6px', marginBottom: '16px' }}
          >
            <option value="pending">Pending</option>
            <option value="confirmed">Confirmed</option>
            <option value="qc_pass">QC Pass</option>
            <option value="qc_fail">QC Fail</option>
            <option value="delivered">Delivered</option>
          </select>

          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Add reason for status change"
            style={{ width: '100%', padding: '8px 12px', border: '1px solid #d1d5db', borderRadius: '6px', marginBottom: '16px', minHeight: '100px', fontFamily: 'inherit' }}
          />

          <button
            onClick={handleStatusUpdate}
            style={{ backgroundColor: '#2563eb', color: 'white', padding: '8px 24px', borderRadius: '6px', cursor: 'pointer' }}
          >
            Update Order
          </button>
        </div>
      </div>
    </div>
  )
}