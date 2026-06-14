import { useState, useEffect } from 'react'
import axios from 'axios'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function Inventory() {
  const [inventory, setInventory] = useState<any>(null)
  const [lowStockItems, setLowStockItems] = useState<any[]>([])
  const [showAddForm, setShowAddForm] = useState(false)
  const [formData, setFormData] = useState({
    lens_power: '',
    lens_type: 'single_vision',
    lens_index: '1.5',
    coating: 'none',
    quantity: ''
  })

  useEffect(() => {
    fetchInventory()
  }, [])

  const fetchInventory = async () => {
    try {
      const [invRes, lowRes] = await Promise.all([
        axios.get(`${API_BASE}/api/inventory/dashboard/summary`),
        axios.get(`${API_BASE}/api/inventory/low-stock`)
      ])
      
      setInventory(invRes.data)
      setLowStockItems(lowRes.data)
    } catch (error) {
      console.error('Error fetching inventory:', error)
    }
  }

  const handleAddStock = async () => {
    try {
      await axios.post(`${API_BASE}/api/inventory/lens`, formData)
      alert('Stock added successfully')
      setFormData({ lens_power: '', lens_type: 'single_vision', lens_index: '1.5', coating: 'none', quantity: '' })
      setShowAddForm(false)
      fetchInventory()
    } catch (error) {
      alert('Error adding stock')
    }
  }

  return (
    <div style={{ padding: '32px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
        <h1>Lens Inventory</h1>
        <button
          onClick={() => setShowAddForm(!showAddForm)}
          style={{ backgroundColor: '#2563eb', color: 'white', padding: '8px 16px', borderRadius: '6px', cursor: 'pointer' }}
        >
          + Add Stock
        </button>
      </div>

      {/* Summary Cards */}
      {inventory && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginBottom: '32px' }}>
          <div style={{ backgroundColor: '#dbeafe', padding: '24px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
            <p style={{ fontSize: '14px', color: '#1e40af', marginBottom: '8px' }}>Total Items</p>
            <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#1e40af' }}>{inventory.total_items}</p>
          </div>
          <div style={{ backgroundColor: '#dbeafe', padding: '24px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
            <p style={{ fontSize: '14px', color: '#1e40af', marginBottom: '8px' }}>Total Quantity</p>
            <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#1e40af' }}>{inventory.total_quantity}</p>
          </div>
          <div style={{ backgroundColor: '#fee2e2', padding: '24px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
            <p style={{ fontSize: '14px', color: '#7f1d1d', marginBottom: '8px' }}>Low Stock Items</p>
            <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#7f1d1d' }}>{inventory.low_stock_items}</p>
          </div>
        </div>
      )}

      {/* Add Stock Form */}
      {showAddForm && (
        <div style={{ backgroundColor: 'white', padding: '24px', borderRadius: '8px', marginBottom: '32px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <h2>Add Stock</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
            <input type="text" placeholder="Lens Power (e.g., +1.5)" value={formData.lens_power} onChange={(e) => setFormData({ ...formData, lens_power: e.target.value })} />
            <select value={formData.lens_type} onChange={(e) => setFormData({ ...formData, lens_type: e.target.value })}>
              <option value="single_vision">Single Vision</option>
              <option value="bifocal">Bifocal</option>
              <option value="progressive">Progressive</option>
            </select>
            <select value={formData.lens_index} onChange={(e) => setFormData({ ...formData, lens_index: e.target.value })}>
              <option value="1.5">1.5</option>
              <option value="1.56">1.56</option>
              <option value="1.61">1.61</option>
              <option value="1.67">1.67</option>
            </select>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px' }}>
            <select value={formData.coating} onChange={(e) => setFormData({ ...formData, coating: e.target.value })}>
              <option value="none">No Coating</option>
              <option value="anti_reflective">Anti-Reflective</option>
              <option value="blue_light">Blue Light</option>
            </select>
            <input type="number" placeholder="Quantity" value={formData.quantity} onChange={(e) => setFormData({ ...formData, quantity: e.target.value })} />
          </div>
          <button onClick={handleAddStock} style={{ backgroundColor: '#10b981', color: 'white', padding: '8px 24px', borderRadius: '6px', cursor: 'pointer', marginTop: '16px' }}>
            Add Stock
          </button>
        </div>
      )}

      {/* Low Stock Alert */}
      {lowStockItems.length > 0 && (
        <div style={{ backgroundColor: '#fee2e2', border: '1px solid #fca5a5', padding: '24px', borderRadius: '8px', marginBottom: '32px', color: '#7f1d1d' }}>
          <h3 style={{ marginBottom: '16px' }}>⚠️ Low Stock Alert</h3>
          {lowStockItems.map((item, i) => (
            <p key={i}>Power {item.power}: Only {item.quantity} units remaining</p>
          ))}
        </div>
      )}
    </div>
  )
}