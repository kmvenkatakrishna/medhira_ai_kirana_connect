import React, { useEffect, useState } from 'react';
import { getOrders, generateOrderSuggestions, getDistributors, createOrder, updateOrderStatus } from '../services/api';

const formatCurrency = (n) => '₹' + Number(n || 0).toLocaleString('en-IN');

const STATUS_STEPS = ['suggested', 'placed', 'confirmed', 'dispatched', 'delivered'];

function OrderTimeline({ status }) {
    const currentIdx = STATUS_STEPS.indexOf(status);
    return (
        <div className="order-timeline">
            {STATUS_STEPS.map((step, i) => (
                <React.Fragment key={step}>
                    <div className={`timeline-step ${i < currentIdx ? 'completed' : i === currentIdx ? 'active' : ''}`}>
                        <div className="dot">{i < currentIdx ? '✓' : i + 1}</div>
                        <div className="label">{step.charAt(0).toUpperCase() + step.slice(1)}</div>
                    </div>
                    {i < STATUS_STEPS.length - 1 && (
                        <div className={`timeline-line ${i < currentIdx ? 'completed' : ''}`} />
                    )}
                </React.Fragment>
            ))}
        </div>
    );
}

export default function Orders() {
    const [orders, setOrders] = useState([]);
    const [suggestions, setSuggestions] = useState(null);
    const [distributors, setDistributors] = useState([]);
    const [loading, setLoading] = useState(true);
    const [tab, setTab] = useState('orders');
    const [expandedOrder, setExpandedOrder] = useState(null);

    const fetchOrders = () => {
        setLoading(true);
        Promise.all([
            getOrders(),
            getDistributors(),
        ]).then(([ordRes, distRes]) => {
            setOrders(ordRes.data);
            setDistributors(distRes.data);
            setLoading(false);
        });
    };

    useEffect(() => { fetchOrders(); }, []);

    const handleGenerateSuggestions = async () => {
        setLoading(true);
        const res = await generateOrderSuggestions();
        setSuggestions(res.data);
        setTab('suggestions');
        setLoading(false);
    };

    const handlePlaceOrder = async () => {
        if (!suggestions || !suggestions.suggestions.length || !distributors.length) return;
        const orderData = {
            distributor_id: distributors[0].id,
            items: suggestions.suggestions.map(s => ({
                product_id: s.product_id,
                quantity: s.suggested_quantity,
                unit_price: s.estimated_cost / s.suggested_quantity,
            })),
        };
        await createOrder(orderData);
        setSuggestions(null);
        setTab('orders');
        fetchOrders();
    };

    const handleStatusUpdate = async (orderId, newStatus) => {
        await updateOrderStatus(orderId, newStatus);
        fetchOrders();
    };

    if (loading) return <div className="loading"><div className="spinner"></div></div>;

    return (
        <div>
            <div className="page-header">
                <div>
                    <h2>Order Management</h2>
                    <p>Manage orders and distributor relationships</p>
                </div>
                <button className="btn btn-primary" onClick={handleGenerateSuggestions}>
                    🤖 Generate Smart Orders
                </button>
            </div>

            <div className="tabs" style={{ marginBottom: 20 }}>
                <button className={`tab ${tab === 'orders' ? 'active' : ''}`} onClick={() => setTab('orders')}>
                    Orders ({orders.length})
                </button>
                <button className={`tab ${tab === 'suggestions' ? 'active' : ''}`} onClick={() => { setTab('suggestions'); if (!suggestions) handleGenerateSuggestions(); }}>
                    AI Suggestions
                </button>
                <button className={`tab ${tab === 'distributors' ? 'active' : ''}`} onClick={() => setTab('distributors')}>
                    Distributors ({distributors.length})
                </button>
            </div>

            {/* Orders list */}
            {tab === 'orders' && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                    {orders.length === 0 ? (
                        <div className="card">
                            <div className="empty-state">
                                <div className="icon">🛒</div>
                                <h3>No Orders Yet</h3>
                                <p>Generate smart order suggestions to get started</p>
                            </div>
                        </div>
                    ) : orders.map(order => (
                        <div key={order.id} className="card" style={{ cursor: 'pointer' }} onClick={() => setExpandedOrder(expandedOrder === order.id ? null : order.id)}>
                            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                                <div>
                                    <h3 style={{ fontSize: 15, fontWeight: 600 }}>Order #{order.id}</h3>
                                    <p style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
                                        {order.distributor_name} • {order.created_at ? new Date(order.created_at).toLocaleDateString() : 'N/A'}
                                    </p>
                                </div>
                                <div style={{ textAlign: 'right' }}>
                                    <div style={{ fontSize: 18, fontWeight: 700 }}>{formatCurrency(order.total_amount)}</div>
                                    <span className={`badge ${order.status}`}>{order.status}</span>
                                </div>
                            </div>

                            <OrderTimeline status={order.status} />

                            {expandedOrder === order.id && (
                                <div style={{ marginTop: 12 }}>
                                    <div className="table-container">
                                        <table>
                                            <thead>
                                                <tr>
                                                    <th>Product</th>
                                                    <th>Qty</th>
                                                    <th>Price</th>
                                                    <th>Total</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {order.items.map((item, i) => (
                                                    <tr key={i}>
                                                        <td>{item.product_name}</td>
                                                        <td>{item.quantity}</td>
                                                        <td>{formatCurrency(item.unit_price)}</td>
                                                        <td style={{ fontWeight: 600 }}>{formatCurrency(item.total)}</td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                    {order.status !== 'delivered' && order.status !== 'cancelled' && (
                                        <div style={{ display: 'flex', gap: 8, marginTop: 12, justifyContent: 'flex-end' }}>
                                            {order.status === 'suggested' && (
                                                <button className="btn btn-primary btn-sm" onClick={(e) => { e.stopPropagation(); handleStatusUpdate(order.id, 'placed'); }}>
                                                    Place Order
                                                </button>
                                            )}
                                            {order.status === 'placed' && (
                                                <button className="btn btn-success btn-sm" onClick={(e) => { e.stopPropagation(); handleStatusUpdate(order.id, 'confirmed'); }}>
                                                    Confirm
                                                </button>
                                            )}
                                            {order.status === 'confirmed' && (
                                                <button className="btn btn-primary btn-sm" onClick={(e) => { e.stopPropagation(); handleStatusUpdate(order.id, 'dispatched'); }}>
                                                    Mark Dispatched
                                                </button>
                                            )}
                                            {order.status === 'dispatched' && (
                                                <button className="btn btn-success btn-sm" onClick={(e) => { e.stopPropagation(); handleStatusUpdate(order.id, 'delivered'); }}>
                                                    Mark Delivered
                                                </button>
                                            )}
                                            <button className="btn btn-danger btn-sm" onClick={(e) => { e.stopPropagation(); handleStatusUpdate(order.id, 'cancelled'); }}>
                                                Cancel
                                            </button>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}

            {/* Suggestions */}
            {tab === 'suggestions' && suggestions && (
                <div className="card">
                    <div className="card-header">
                        <h3>🤖 Smart Order Suggestions</h3>
                        <div>
                            <span style={{ fontSize: 14, fontWeight: 600, marginRight: 12 }}>
                                Total: {formatCurrency(suggestions.total_estimated_cost)}
                            </span>
                            {suggestions.suggestions.length > 0 && (
                                <button className="btn btn-success btn-sm" onClick={handlePlaceOrder}>
                                    📦 Place All Orders
                                </button>
                            )}
                        </div>
                    </div>
                    {suggestions.suggestions.length === 0 ? (
                        <div className="empty-state">
                            <div className="icon">✅</div>
                            <h3>All Stock Levels Healthy!</h3>
                            <p>No reorder suggestions at this time</p>
                        </div>
                    ) : (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                            {suggestions.suggestions.map((s, i) => (
                                <div key={i} className="prediction-card">
                                    <div className="prediction-icon" style={{
                                        background: s.priority === 'high' ? 'var(--danger-bg)' : 'var(--warning-bg)',
                                        color: s.priority === 'high' ? 'var(--danger)' : 'var(--warning-dark)',
                                    }}>
                                        {s.priority === 'high' ? '🚨' : '📦'}
                                    </div>
                                    <div className="prediction-details">
                                        <h4>{s.product_name}</h4>
                                        <p>
                                            Stock: {s.current_stock} | Reorder at: {s.reorder_point} |
                                            <strong> Order: {s.suggested_quantity}</strong>
                                        </p>
                                    </div>
                                    <div style={{ textAlign: 'right' }}>
                                        <div className="prediction-value">{formatCurrency(s.estimated_cost)}</div>
                                        <span className={`badge ${s.priority}`}>{s.priority}</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}

            {/* Distributors */}
            {tab === 'distributors' && (
                <div className="card">
                    <div className="card-header"><h3>🤝 Distributors</h3></div>
                    <div className="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>Phone</th>
                                    <th>Email</th>
                                    <th>City</th>
                                    <th>Rating</th>
                                    <th>Categories</th>
                                </tr>
                            </thead>
                            <tbody>
                                {distributors.map(d => (
                                    <tr key={d.id}>
                                        <td style={{ fontWeight: 500 }}>{d.name}</td>
                                        <td>{d.phone}</td>
                                        <td style={{ color: 'var(--text-secondary)' }}>{d.email}</td>
                                        <td>{d.city}</td>
                                        <td>
                                            <span style={{ color: 'var(--warning-dark)', fontWeight: 600 }}>
                                                ⭐ {d.rating}
                                            </span>
                                        </td>
                                        <td>
                                            {JSON.parse(d.categories || '[]').map(c => (
                                                <span key={c} className="badge good" style={{ marginRight: 4 }}>{c}</span>
                                            ))}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    );
}
