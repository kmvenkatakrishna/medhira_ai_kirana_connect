import React, { useState, useEffect } from 'react';
import './index.css';
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import Inventory from './components/Inventory';
import Analytics from './components/Analytics';
import Predictions from './components/Predictions';
import Orders from './components/Orders';
import WhatsAppChat from './components/WhatsAppChat';
import { getLowStock } from './services/api';

function App() {
  const [activePage, setActivePage] = useState('dashboard');
  const [lowStockCount, setLowStockCount] = useState(0);

  useEffect(() => {
    getLowStock().then(res => setLowStockCount(res.data.length)).catch(() => { });
  }, [activePage]);

  const renderPage = () => {
    switch (activePage) {
      case 'dashboard':
        return <Dashboard />;
      case 'inventory':
        return <Inventory />;
      case 'analytics':
        return <Analytics />;
      case 'predictions':
        return <Predictions />;
      case 'orders':
        return <Orders />;
      case 'whatsapp':
        return <WhatsAppChat />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="app-layout">
      <Sidebar
        activePage={activePage}
        onNavigate={setActivePage}
        lowStockCount={lowStockCount}
      />
      <main className="main-content">
        {renderPage()}
      </main>
    </div>
  );
}

export default App;
