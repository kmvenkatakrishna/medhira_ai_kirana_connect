import React from 'react';

const navItems = [
    {
        section: 'Overview', items: [
            { id: 'dashboard', icon: '📊', label: 'Dashboard' },
            { id: 'analytics', icon: '📈', label: 'Analytics' },
        ]
    },
    {
        section: 'Management', items: [
            { id: 'inventory', icon: '📦', label: 'Inventory' },
            { id: 'orders', icon: '🛒', label: 'Orders' },
            { id: 'predictions', icon: '🔮', label: 'AI Predictions' },
        ]
    },
    {
        section: 'Communication', items: [
            { id: 'whatsapp', icon: '💬', label: 'WhatsApp Chat' },
        ]
    },
];

export default function Sidebar({ activePage, onNavigate, lowStockCount }) {
    return (
        <aside className="sidebar">
            <div className="sidebar-header">
                <div className="sidebar-logo">
                    <div className="sidebar-logo-icon">🏪</div>
                    <div className="sidebar-logo-text">
                        <h1>Kirana-Connect</h1>
                        <p>AI Inventory Agent</p>
                    </div>
                </div>
            </div>

            <nav className="sidebar-nav">
                {navItems.map((section) => (
                    <div key={section.section} className="sidebar-nav-section">
                        <div className="sidebar-nav-section-title">{section.section}</div>
                        {section.items.map((item) => (
                            <button
                                key={item.id}
                                id={`nav-${item.id}`}
                                className={`sidebar-nav-item ${activePage === item.id ? 'active' : ''}`}
                                onClick={() => onNavigate(item.id)}
                            >
                                <span className="nav-icon">{item.icon}</span>
                                <span>{item.label}</span>
                                {item.id === 'inventory' && lowStockCount > 0 && (
                                    <span className="nav-badge">{lowStockCount}</span>
                                )}
                            </button>
                        ))}
                    </div>
                ))}
            </nav>

            <div className="sidebar-footer">
                <div className="sidebar-store-info">
                    <div className="store-avatar">RK</div>
                    <div className="store-details">
                        <h3>Kumar General Store</h3>
                        <p>Connaught Place, Delhi</p>
                    </div>
                </div>
            </div>
        </aside>
    );
}
