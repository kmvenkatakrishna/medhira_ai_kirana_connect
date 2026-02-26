import React, { useEffect, useState } from 'react';
import { getSalesTrends, getTopProducts, getCategoryBreakdown, getDailyReport } from '../services/api';
import {
    AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
    XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts';

const formatCurrency = (n) => '₹' + Number(n || 0).toLocaleString('en-IN');

const COLORS = ['#6C5CE7', '#FF6B35', '#00B894', '#FDCB6E', '#74B9FF', '#FF6B6B', '#A29BFE', '#55EFC4', '#F39C12', '#E55A2B'];

export default function Analytics() {
    const [trends, setTrends] = useState([]);
    const [topProducts, setTopProducts] = useState([]);
    const [categories, setCategories] = useState([]);
    const [report, setReport] = useState(null);
    const [days, setDays] = useState(30);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        setLoading(true);
        Promise.all([
            getSalesTrends(days),
            getTopProducts(days),
            getCategoryBreakdown(days),
            getDailyReport(),
        ]).then(([trendRes, topRes, catRes, reportRes]) => {
            setTrends(trendRes.data);
            setTopProducts(topRes.data);
            setCategories(catRes.data);
            setReport(reportRes.data);
            setLoading(false);
        });
    }, [days]);

    if (loading) return <div className="loading"><div className="spinner"></div></div>;

    return (
        <div>
            <div className="page-header">
                <div>
                    <h2>Analytics & Reports</h2>
                    <p>Insights and performance metrics for your store</p>
                </div>
                <div className="tabs">
                    {[7, 14, 30].map(d => (
                        <button key={d} className={`tab ${days === d ? 'active' : ''}`} onClick={() => setDays(d)}>
                            {d}D
                        </button>
                    ))}
                </div>
            </div>

            {/* Daily report summary */}
            {report && (
                <div className="stats-grid">
                    <div className="stat-card primary">
                        <div className="stat-card-value">{formatCurrency(report.total_sales)}</div>
                        <div className="stat-card-label">Yesterday Sales</div>
                    </div>
                    <div className="stat-card accent">
                        <div className="stat-card-value">{formatCurrency(report.total_purchases)}</div>
                        <div className="stat-card-label">Yesterday Purchases</div>
                    </div>
                    <div className="stat-card success">
                        <div className="stat-card-value">{formatCurrency(report.profit_estimate)}</div>
                        <div className="stat-card-label">Estimated Profit</div>
                    </div>
                    <div className="stat-card info">
                        <div className="stat-card-value">{report.margin_pct}%</div>
                        <div className="stat-card-label">Profit Margin</div>
                    </div>
                </div>
            )}

            {/* Sales trend */}
            <div className="card" style={{ marginBottom: 24 }}>
                <div className="card-header">
                    <h3>📈 Sales Trend ({days} Days)</h3>
                </div>
                <div className="chart-container" style={{ height: 320 }}>
                    <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={trends}>
                            <defs>
                                <linearGradient id="trendGrad" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#6C5CE7" stopOpacity={0.3} />
                                    <stop offset="95%" stopColor="#6C5CE7" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                            <XAxis dataKey="date" tick={{ fill: '#6C6C80', fontSize: 10 }} axisLine={false} tickLine={false} tickFormatter={v => v.slice(5)} />
                            <YAxis tick={{ fill: '#6C6C80', fontSize: 10 }} axisLine={false} tickLine={false} tickFormatter={v => `₹${(v / 1000).toFixed(0)}k`} />
                            <Tooltip contentStyle={{ background: '#1E1E32', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, fontSize: 12 }} formatter={v => [formatCurrency(v), 'Sales']} />
                            <Area type="monotone" dataKey="sales" stroke="#6C5CE7" fill="url(#trendGrad)" strokeWidth={2} dot={false} />
                        </AreaChart>
                    </ResponsiveContainer>
                </div>
            </div>

            <div className="grid-2">
                {/* Top products */}
                <div className="card">
                    <div className="card-header">
                        <h3>🏆 Top Products by Revenue</h3>
                    </div>
                    <div className="chart-container" style={{ height: 320 }}>
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={topProducts.slice(0, 8)} margin={{ left: 10 }}>
                                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                                <XAxis dataKey="product_name" tick={{ fill: '#6C6C80', fontSize: 9 }} axisLine={false} tickLine={false} tickFormatter={v => v.length > 10 ? v.slice(0, 10) + '…' : v} angle={-30} />
                                <YAxis tick={{ fill: '#6C6C80', fontSize: 10 }} axisLine={false} tickLine={false} tickFormatter={v => `₹${(v / 1000).toFixed(0)}k`} />
                                <Tooltip contentStyle={{ background: '#1E1E32', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, fontSize: 12 }} formatter={v => [formatCurrency(v), 'Revenue']} />
                                <Bar dataKey="total_revenue" radius={[4, 4, 0, 0]}>
                                    {topProducts.slice(0, 8).map((_, i) => (
                                        <Cell key={i} fill={COLORS[i % COLORS.length]} />
                                    ))}
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Category breakdown */}
                <div className="card">
                    <div className="card-header">
                        <h3>🎯 Revenue by Category</h3>
                    </div>
                    <div className="chart-container" style={{ height: 320 }}>
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie
                                    data={categories}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={70}
                                    outerRadius={110}
                                    paddingAngle={3}
                                    dataKey="revenue"
                                    nameKey="category"
                                    label={({ category, percentage }) => `${category} (${percentage}%)`}
                                >
                                    {categories.map((_, i) => (
                                        <Cell key={i} fill={COLORS[i % COLORS.length]} />
                                    ))}
                                </Pie>
                                <Tooltip
                                    contentStyle={{ background: '#1E1E32', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, fontSize: 12 }}
                                    formatter={v => formatCurrency(v)}
                                />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>

            {/* Top products table */}
            <div className="card">
                <div className="card-header">
                    <h3>📋 Product Performance Details</h3>
                </div>
                <div className="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>Product</th>
                                <th>Category</th>
                                <th>Units Sold</th>
                                <th>Revenue</th>
                            </tr>
                        </thead>
                        <tbody>
                            {topProducts.map((p, i) => (
                                <tr key={i}>
                                    <td style={{ color: 'var(--text-muted)', fontWeight: 600 }}>{i + 1}</td>
                                    <td style={{ fontWeight: 500 }}>{p.product_name}</td>
                                    <td><span className="badge good">{p.category}</span></td>
                                    <td>{p.total_quantity}</td>
                                    <td style={{ fontWeight: 600 }}>{formatCurrency(p.total_revenue)}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
