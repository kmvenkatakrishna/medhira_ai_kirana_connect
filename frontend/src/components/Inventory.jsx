import React, { useEffect, useState } from 'react';
import { getInventory, getCategories, getInventorySummary, recordPurchase, recordSale, getProducts } from '../services/api';

const formatCurrency = (n) => '₹' + Number(n || 0).toLocaleString('en-IN');

export default function Inventory() {
    const [items, setItems] = useState([]);
    const [categories, setCategories] = useState([]);
    const [summary, setSummary] = useState(null);
    const [selectedCategory, setSelectedCategory] = useState('');
    const [search, setSearch] = useState('');
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [modalType, setModalType] = useState('purchase');
    const [products, setProducts] = useState([]);
    const [formItems, setFormItems] = useState([{ product_id: '', quantity: '', unit_price: '' }]);
    const [submitting, setSubmitting] = useState(false);

    const fetchData = () => {
        setLoading(true);
        const params = {};
        if (selectedCategory) params.category = selectedCategory;
        if (search) params.search = search;

        Promise.all([
            getInventory(params),
            getCategories(),
            getInventorySummary(),
        ]).then(([invRes, catRes, sumRes]) => {
            setItems(invRes.data);
            setCategories(catRes.data);
            setSummary(sumRes.data);
            setLoading(false);
        });
    };

    useEffect(() => { fetchData(); }, [selectedCategory, search]);

    const openModal = (type) => {
        setModalType(type);
        setFormItems([{ product_id: '', quantity: '', unit_price: '' }]);
        getProducts().then(r => setProducts(r.data));
        setShowModal(true);
    };

    const addFormItem = () => setFormItems([...formItems, { product_id: '', quantity: '', unit_price: '' }]);

    const updateFormItem = (idx, field, value) => {
        const updated = [...formItems];
        updated[idx][field] = value;
        if (field === 'product_id' && value) {
            const p = products.find(prod => prod.id === parseInt(value));
            if (p) updated[idx].unit_price = p.typical_price;
        }
        setFormItems(updated);
    };

    const handleSubmit = async () => {
        const validItems = formItems.filter(i => i.product_id && i.quantity && i.unit_price);
        if (!validItems.length) return;

        setSubmitting(true);
        const data = {
            items: validItems.map(i => ({
                product_id: parseInt(i.product_id),
                quantity: parseFloat(i.quantity),
                unit_price: parseFloat(i.unit_price),
            })),
            source: 'manual',
        };

        try {
            if (modalType === 'purchase') await recordPurchase(data);
            else await recordSale(data);
            setShowModal(false);
            fetchData();
        } catch (e) {
            alert('Error: ' + (e.response?.data?.detail || e.message));
        }
        setSubmitting(false);
    };

    return (
        <div>
            <div className="page-header">
                <div>
                    <h2>Inventory Management</h2>
                    <p>Track and manage your store inventory</p>
                </div>
                <div style={{ display: 'flex', gap: 8 }}>
                    <button className="btn btn-primary" onClick={() => openModal('purchase')}>➕ Add Purchase</button>
                    <button className="btn btn-success" onClick={() => openModal('sale')}>💰 Record Sale</button>
                </div>
            </div>

            {/* Summary cards */}
            {summary && (
                <div className="stats-grid">
                    <div className="stat-card primary">
                        <div className="stat-card-value">{summary.total_items}</div>
                        <div className="stat-card-label">Total Products</div>
                    </div>
                    <div className="stat-card accent">
                        <div className="stat-card-value">{formatCurrency(summary.total_value)}</div>
                        <div className="stat-card-label">Total Value</div>
                    </div>
                    <div className="stat-card success">
                        <div className="stat-card-value">{summary.healthy_count}</div>
                        <div className="stat-card-label">Healthy Stock</div>
                    </div>
                    <div className="stat-card danger">
                        <div className="stat-card-value">{summary.low_stock_count}</div>
                        <div className="stat-card-label">Low / Critical</div>
                    </div>
                </div>
            )}

            {/* Filters */}
            <div className="card" style={{ marginBottom: 20 }}>
                <div style={{ display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap' }}>
                    <div className="search-input" style={{ flex: 1, minWidth: 200 }}>
                        <span className="search-icon">🔍</span>
                        <input
                            type="search"
                            id="inventory-search"
                            placeholder="Search products..."
                            value={search}
                            onChange={e => setSearch(e.target.value)}
                        />
                    </div>
                    <div className="filter-bar" style={{ marginBottom: 0 }}>
                        <button
                            className={`filter-chip ${!selectedCategory ? 'active' : ''}`}
                            onClick={() => setSelectedCategory('')}
                        >All</button>
                        {categories.map(cat => (
                            <button
                                key={cat}
                                className={`filter-chip ${selectedCategory === cat ? 'active' : ''}`}
                                onClick={() => setSelectedCategory(cat)}
                            >{cat}</button>
                        ))}
                    </div>
                </div>
            </div>

            {/* Inventory table */}
            <div className="card">
                {loading ? (
                    <div className="loading"><div className="spinner"></div></div>
                ) : items.length === 0 ? (
                    <div className="empty-state">
                        <div className="icon">📦</div>
                        <h3>No items found</h3>
                        <p>Try adjusting your search or filters</p>
                    </div>
                ) : (
                    <div className="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>Product</th>
                                    <th>Category</th>
                                    <th>Brand</th>
                                    <th>Stock</th>
                                    <th>Reorder At</th>
                                    <th>Value</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                {items.map(item => (
                                    <tr key={item.id}>
                                        <td style={{ fontWeight: 500 }}>
                                            {item.is_perishable && '🟢 '}{item.product_name}
                                        </td>
                                        <td>{item.category}</td>
                                        <td style={{ color: 'var(--text-secondary)' }}>{item.brand}</td>
                                        <td>
                                            <span style={{ fontWeight: 600 }}>{item.current_quantity}</span>
                                            <span style={{ color: 'var(--text-muted)', marginLeft: 4 }}>{item.unit}</span>
                                            <div className="progress-bar" style={{ width: 80, marginTop: 4 }}>
                                                <div
                                                    className={`progress-fill ${item.status}`}
                                                    style={{ width: `${Math.min(100, (item.current_quantity / item.optimal_quantity) * 100)}%` }}
                                                />
                                            </div>
                                        </td>
                                        <td>{item.reorder_point} {item.unit}</td>
                                        <td style={{ fontWeight: 500 }}>{formatCurrency(item.current_quantity * item.typical_price)}</td>
                                        <td><span className={`badge ${item.status}`}>{item.status}</span></td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            {/* Purchase/Sale Modal */}
            {showModal && (
                <div className="modal-overlay" onClick={() => setShowModal(false)}>
                    <div className="modal" onClick={e => e.stopPropagation()} style={{ maxWidth: 600 }}>
                        <div className="modal-header">
                            <h3>{modalType === 'purchase' ? '📥 Record Purchase' : '💰 Record Sale'}</h3>
                            <button className="modal-close" onClick={() => setShowModal(false)}>✕</button>
                        </div>

                        {formItems.map((fi, idx) => (
                            <div key={idx} style={{ display: 'flex', gap: 10, marginBottom: 12, alignItems: 'end' }}>
                                <div style={{ flex: 2 }}>
                                    <label style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 4, display: 'block' }}>Product</label>
                                    <select
                                        value={fi.product_id}
                                        onChange={e => updateFormItem(idx, 'product_id', e.target.value)}
                                    >
                                        <option value="">Select product</option>
                                        {products.map(p => (
                                            <option key={p.id} value={p.id}>{p.name} ({p.unit})</option>
                                        ))}
                                    </select>
                                </div>
                                <div style={{ flex: 1 }}>
                                    <label style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 4, display: 'block' }}>Qty</label>
                                    <input
                                        type="number"
                                        value={fi.quantity}
                                        onChange={e => updateFormItem(idx, 'quantity', e.target.value)}
                                        placeholder="Qty"
                                        min="1"
                                    />
                                </div>
                                <div style={{ flex: 1 }}>
                                    <label style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 4, display: 'block' }}>Price (₹)</label>
                                    <input
                                        type="number"
                                        value={fi.unit_price}
                                        onChange={e => updateFormItem(idx, 'unit_price', e.target.value)}
                                        placeholder="Price"
                                        min="0"
                                    />
                                </div>
                            </div>
                        ))}

                        <button className="btn btn-ghost" onClick={addFormItem} style={{ marginBottom: 16 }}>+ Add Item</button>

                        <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end' }}>
                            <button className="btn btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
                            <button
                                className={`btn ${modalType === 'purchase' ? 'btn-primary' : 'btn-success'}`}
                                onClick={handleSubmit}
                                disabled={submitting}
                            >
                                {submitting ? 'Saving...' : modalType === 'purchase' ? 'Record Purchase' : 'Record Sale'}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
