import React, { useEffect, useState } from 'react';
import { getPredictions, generatePredictions, getPredictionSummary } from '../services/api';

const formatCurrency = (n) => '₹' + Number(n || 0).toLocaleString('en-IN');

const factorIcons = {
    seasonal: '🌤️',
    trend: '📈',
    weather_impact: '🌧️',
    festival_effect: '🎉',
    weekend_boost: '📅',
};

export default function Predictions() {
    const [predictions, setPredictions] = useState([]);
    const [summary, setSummary] = useState(null);
    const [loading, setLoading] = useState(true);
    const [generating, setGenerating] = useState(false);
    const [view, setView] = useState('summary');

    const fetchData = () => {
        setLoading(true);
        Promise.all([
            getPredictions(),
            getPredictionSummary(),
        ]).then(([predRes, sumRes]) => {
            setPredictions(predRes.data);
            setSummary(sumRes.data);
            setLoading(false);
        });
    };

    useEffect(() => { fetchData(); }, []);

    const handleGenerate = async () => {
        setGenerating(true);
        await generatePredictions();
        fetchData();
        setGenerating(false);
    };

    if (loading) return <div className="loading"><div className="spinner"></div></div>;

    // Group predictions by product
    const grouped = {};
    predictions.forEach(p => {
        if (!grouped[p.product_name]) {
            grouped[p.product_name] = { category: p.category, items: [] };
        }
        grouped[p.product_name].items.push(p);
    });

    return (
        <div>
            <div className="page-header">
                <div>
                    <h2>🔮 AI Demand Predictions</h2>
                    <p>ML-powered demand forecasting for your inventory</p>
                </div>
                <button className="btn btn-primary" onClick={handleGenerate} disabled={generating}>
                    {generating ? '⏳ Generating...' : '🔄 Regenerate Predictions'}
                </button>
            </div>

            {/* Summary stats */}
            {summary && (
                <div className="stats-grid">
                    <div className="stat-card primary">
                        <div className="stat-card-value">{summary.total_products_analyzed}</div>
                        <div className="stat-card-label">Products Analyzed</div>
                    </div>
                    <div className="stat-card danger">
                        <div className="stat-card-header">
                            <div className="stat-card-icon">⚠️</div>
                        </div>
                        <div className="stat-card-value">{summary.at_risk_products}</div>
                        <div className="stat-card-label">At Risk (Deficit)</div>
                    </div>
                </div>
            )}

            <div className="tabs" style={{ marginBottom: 20 }}>
                <button className={`tab ${view === 'summary' ? 'active' : ''}`} onClick={() => setView('summary')}>Risk Summary</button>
                <button className={`tab ${view === 'details' ? 'active' : ''}`} onClick={() => setView('details')}>All Forecasts</button>
            </div>

            {view === 'summary' && summary && (
                <div className="card">
                    <div className="card-header">
                        <h3>🚨 High-Risk Items (7-Day Stockout Risk)</h3>
                    </div>
                    {summary.high_risk_items.length === 0 ? (
                        <div className="empty-state">
                            <div className="icon">✅</div>
                            <h3>All Clear!</h3>
                            <p>No products are at risk of stockout in the next 7 days</p>
                        </div>
                    ) : (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                            {summary.high_risk_items.map((item, i) => (
                                <div key={i} className="prediction-card">
                                    <div className="prediction-icon" style={{ background: 'var(--danger-bg)', color: 'var(--danger)' }}>
                                        📉
                                    </div>
                                    <div className="prediction-details">
                                        <h4>{item.product_name}</h4>
                                        <p>
                                            Current: <strong>{item.current_stock}</strong> |
                                            7-day demand: <strong>{item.total_predicted}</strong> |
                                            Deficit: <span className="text-danger" style={{ fontWeight: 700 }}>{item.surplus_deficit}</span>
                                        </p>
                                    </div>
                                    <div>
                                        <span className={`badge ${item.surplus_deficit < -20 ? 'critical' : 'low'}`}>
                                            {item.surplus_deficit < -20 ? 'Critical' : 'Moderate'} Risk
                                        </span>
                                        <div className="prediction-confidence" style={{ marginTop: 4 }}>
                                            Confidence: {(item.avg_confidence * 100).toFixed(0)}%
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}

            {view === 'details' && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                    {Object.entries(grouped).map(([name, data]) => (
                        <div key={name} className="card">
                            <div className="card-header">
                                <div>
                                    <h3>{name}</h3>
                                    <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>{data.category}</span>
                                </div>
                            </div>
                            <div className="table-container">
                                <table>
                                    <thead>
                                        <tr>
                                            <th>Date</th>
                                            <th>Predicted Qty</th>
                                            <th>Confidence</th>
                                            <th>Key Factors</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {data.items.map((item, i) => (
                                            <tr key={i}>
                                                <td>{item.forecast_date}</td>
                                                <td style={{ fontWeight: 600 }}>{item.predicted_quantity}</td>
                                                <td>
                                                    <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                                                        <div className="progress-bar" style={{ width: 60 }}>
                                                            <div className="progress-fill good" style={{ width: `${item.confidence * 100}%` }} />
                                                        </div>
                                                        <span style={{ fontSize: 11 }}>{(item.confidence * 100).toFixed(0)}%</span>
                                                    </div>
                                                </td>
                                                <td style={{ fontSize: 12 }}>
                                                    {Object.entries(item.factors || {}).filter(([, v]) => typeof v === 'number' && Math.abs(v) > 0.05).map(([k, v]) => (
                                                        <span key={k} style={{ marginRight: 8, color: v > 0 ? 'var(--success)' : 'var(--danger)', fontWeight: 500 }}>
                                                            {factorIcons[k] || '•'} {k.replace('_', ' ')}: {v > 0 ? '+' : ''}{(v * 100).toFixed(0)}%
                                                        </span>
                                                    ))}
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
