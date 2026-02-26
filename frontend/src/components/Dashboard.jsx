import React, { useEffect, useState } from 'react';
import { getDashboard, getSalesTrends, getTopProducts, getLowStock } from '../services/api';
import { AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const formatCurrency = (n) => '₹' + Number(n || 0).toLocaleString('en-IN');

export default function Dashboard() {
    const [data, setData] = useState(null);
    const [trends, setTrends] = useState([]);
    const [topProducts, setTopProducts] = useState([]);
    const [lowStock, setLowStock] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        Promise.all([
            getDashboard(),
            getSalesTrends(14),
            getTopProducts(30),
            getLowStock(),
        ]).then(([dashRes, trendRes, topRes, lowRes]) => {
            setData(dashRes.data);
            setTrends(trendRes.data);
            setTopProducts(topRes.data);
            setLowStock(lowRes.data);
            setLoading(false);
        }).catch(() => setLoading(false));
    }, []);

    if (loading) {
        return <div className="loading"><div className="spinner"></div></div>;
    }

    if (!data) {
        return <div className="loading">Failed to load dashboard data</div>;
    }

    return (
        <div>
            <div className="page-header">
                <div>
                    <h2>Dashboard</h2>
                    <p>Overview of your store performance</p>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                        {new Date().toLocaleDateString('en-IN', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
                    </span>
                </div>
            </div>

            {/* Stats */}
            <div className="stats-grid">
                <div className="stat-card primary">
                    <div className="stat-card-header">
                        <div className="stat-card-icon">💰</div>
                        {data.sales_change_pct !== 0 && (
                            <span className={`stat-card-change ${data.sales_change_pct > 0 ? 'positive' : 'negative'}`}>
                                {data.sales_change_pct > 0 ? '↑' : '↓'} {Math.abs(data.sales_change_pct)}%
                            </span>
                        )}
                    </div>
                    <div className="stat-card-value">{formatCurrency(data.today_sales)}</div>
                    <div className="stat-card-label">Today's Sales</div>
                </div>

                <div className="stat-card success">
                    <div className="stat-card-header">
                        <div className="stat-card-icon">📦</div>
                    </div>
                    <div className="stat-card-value">{data.total_products}</div>
                    <div className="stat-card-label">Total Products</div>
                </div>

                <div className="stat-card warning">
                    <div className="stat-card-header">
                        <div className="stat-card-icon">⚠️</div>
                        {data.low_stock_alerts > 0 && <span className="notification-dot"></span>}
                    </div>
                    <div className="stat-card-value">{data.low_stock_alerts}</div>
                    <div className="stat-card-label">Low Stock Alerts</div>
                </div>

                <div className="stat-card accent">
                    <div className="stat-card-header">
                        <div className="stat-card-icon">📊</div>
                    </div>
                    <div className="stat-card-value">{formatCurrency(data.total_inventory_value)}</div>
                    <div className="stat-card-label">Inventory Value</div>
                </div>

                <div className="stat-card info">
                    <div className="stat-card-header">
                        <div className="stat-card-icon">🧾</div>
                    </div>
                    <div className="stat-card-value">{data.today_transactions}</div>
                    <div className="stat-card-label">Transactions Today</div>
                </div>

                <div className="stat-card success">
                    <div className="stat-card-header">
                        <div className="stat-card-icon">📅</div>
                    </div>
                    <div className="stat-card-value">{formatCurrency(data.month_sales)}</div>
                    <div className="stat-card-label">This Month</div>
                </div>
            </div>

            {/* Charts */}
            <div className="grid-2">
                <div className="card">
                    <div className="card-header">
                        <h3>📈 Sales Trend (14 Days)</h3>
                    </div>
                    <div className="chart-container">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={trends}>
                                <defs>
                                    <linearGradient id="salesGrad" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#6C5CE7" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="#6C5CE7" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                                <XAxis
                                    dataKey="date"
                                    tick={{ fill: '#6C6C80', fontSize: 11 }}
                                    tickFormatter={(v) => v.slice(5)}
                                    axisLine={false}
                                    tickLine={false}
                                />
                                <YAxis
                                    tick={{ fill: '#6C6C80', fontSize: 11 }}
                                    axisLine={false}
                                    tickLine={false}
                                    tickFormatter={(v) => `₹${(v / 1000).toFixed(0)}k`}
                                />
                                <Tooltip
                                    contentStyle={{
                                        background: '#1E1E32',
                                        border: '1px solid rgba(255,255,255,0.1)',
                                        borderRadius: 8,
                                        fontSize: 12,
                                    }}
                                    formatter={(v) => [formatCurrency(v), 'Sales']}
                                    labelFormatter={(v) => v}
                                />
                                <Area type="monotone" dataKey="sales" stroke="#6C5CE7" fill="url(#salesGrad)" strokeWidth={2} />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                <div className="card">
                    <div className="card-header">
                        <h3>🏆 Top Products (30 Days Revenue)</h3>
                    </div>
                    <div className="chart-container">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={topProducts.slice(0, 8)} layout="vertical" margin={{ left: 80 }}>
                                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                                <XAxis
                                    type="number"
                                    tick={{ fill: '#6C6C80', fontSize: 11 }}
                                    axisLine={false}
                                    tickLine={false}
                                    tickFormatter={(v) => `₹${(v / 1000).toFixed(0)}k`}
                                />
                                <YAxis
                                    type="category"
                                    dataKey="product_name"
                                    tick={{ fill: '#A0A0B8', fontSize: 11 }}
                                    axisLine={false}
                                    tickLine={false}
                                    width={80}
                                    tickFormatter={(v) => v.length > 14 ? v.slice(0, 14) + '…' : v}
                                />
                                <Tooltip
                                    contentStyle={{
                                        background: '#1E1E32',
                                        border: '1px solid rgba(255,255,255,0.1)',
                                        borderRadius: 8,
                                        fontSize: 12,
                                    }}
                                    formatter={(v) => [formatCurrency(v), 'Revenue']}
                                />
                                <Bar dataKey="total_revenue" fill="#FF6B35" radius={[0, 4, 4, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>

            {/* Low Stock Alerts */}
            {lowStock.length > 0 && (
                <div className="card" style={{ marginBottom: 24 }}>
                    <div className="card-header">
                        <h3>🚨 Low Stock Alerts</h3>
                        <span className="badge critical">{lowStock.length} items</span>
                    </div>
                    <div className="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>Product</th>
                                    <th>Category</th>
                                    <th>Current Stock</th>
                                    <th>Reorder Point</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                {lowStock.slice(0, 10).map((item, i) => (
                                    <tr key={i}>
                                        <td style={{ fontWeight: 500 }}>{item.product_name}</td>
                                        <td>{item.category}</td>
                                        <td>
                                            <span style={{ color: item.current_quantity <= item.reorder_point * 0.5 ? 'var(--danger)' : 'var(--warning-dark)', fontWeight: 600 }}>
                                                {item.current_quantity} {item.unit}
                                            </span>
                                        </td>
                                        <td>{item.reorder_point} {item.unit}</td>
                                        <td>
                                            <span className={`badge ${item.current_quantity <= item.reorder_point * 0.5 ? 'critical' : 'low'}`}>
                                                {item.current_quantity <= item.reorder_point * 0.5 ? '🔴 Critical' : '🟡 Low'}
                                            </span>
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
