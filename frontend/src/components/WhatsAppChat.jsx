import React, { useState, useRef, useEffect } from 'react';

const DEMO_FLOWS = {
    onboarding: [
        { type: 'bot', text: 'Welcome to Kirana-Connect! 👋\n\nI\'m your AI assistant for inventory management. I help Kirana store owners manage stock, predict demand, and automate orders.' },
        { type: 'bot', text: 'Let\'s get started! What\'s your store name?' },
        { type: 'user', text: 'Kumar General Store' },
        { type: 'bot', text: 'Great! Where is your store located? (City/Area)' },
        { type: 'user', text: 'Connaught Place, New Delhi' },
        { type: 'bot', text: 'Perfect! ✅ Your store is registered.\n\nHow would you like to add purchases?', buttons: ['📸 Photo of bill', '🎤 Voice note', '⌨️ Type manually'] },
        { type: 'user', text: '📸 Photo of bill' },
        { type: 'bot', text: 'Perfect! Whenever you make a purchase, just send me a photo of the bill. I\'ll handle the rest! 📸\n\nTry it now — send a photo of a recent purchase bill.' },
    ],
    purchase: [
        { type: 'user', text: '📸 [Photo of purchase bill sent]' },
        { type: 'bot', text: 'Got it! Processing your bill... ⏳' },
        { type: 'bot', text: 'I found these items:\n\n✅ Amul Milk (500ml) — 100 packets — ₹2,500\n✅ Britannia Bread — 50 loaves — ₹1,750\n✅ Eggs (12 pack) — 20 trays — ₹1,440\n✅ Parle-G Biscuit — 30 packets — ₹1,800\n\nTotal: ₹7,490\n\nIs this correct?', buttons: ['✅ Yes, add to inventory', '✏️ No, let me edit'] },
        { type: 'user', text: '✅ Yes, add to inventory' },
        { type: 'bot', text: 'Inventory updated! ✅\n\nYour current stock:\n🥛 Milk: 250 packets\n🍞 Bread: 80 loaves\n🥚 Eggs: 45 trays\n🍪 Parle-G: 120 packets' },
    ],
    forecast: [
        { type: 'user', text: 'What should I order for next week?' },
        { type: 'bot', text: 'Analyzing your data... 📊' },
        { type: 'bot', text: 'Based on:\n🎉 Holi festival on Mar 14\n🌡️ Hot weather forecast (35°C+)\n📈 Recent sales trends (↑12%)\n\nHere\'s what I recommend:' },
        { type: 'bot', text: '🚨 High Priority (Low Stock):\n🥛 Milk: Order 200 packets (₹5,000)\n   Current: 50 | 7-day need: 180\n\n⚠️ Bread: Order 100 loaves (₹3,500)\n   Current: 20 | 7-day need: 90\n\n📦 Medium Priority:\n🍫 Chocolates: Order 150 pcs (₹6,000)\n   Festival demand expected ↑40%\n🥤 Cold Drinks: Order 200 bottles (₹7,600)\n   Hot weather surge expected\n\nTotal order value: ₹22,100', buttons: ['📦 Place Order', '✏️ Modify Order', '📋 View Details'] },
        { type: 'user', text: '📦 Place Order' },
        { type: 'bot', text: 'Order sent to Ram Distributors! 📦\n\nOrder #KC2026-0128\nExpected delivery: Tomorrow 10 AM\nTotal: ₹22,100\n\nI\'ll notify you when it\'s dispatched. 🚚' },
    ],
    daily: [
        { type: 'bot', text: 'Good Morning, Rajesh ji! ☀️\n\nHere\'s your daily summary:' },
        { type: 'bot', text: '📊 Yesterday\'s Performance:\n💰 Sales: ₹12,500 (15 transactions)\n🏆 Top seller: Amul Milk (80 sold)\n📦 Purchases: ₹8,200\n💵 Profit: ₹4,300 (34.4%)\n\n📦 Inventory Status:\n✅ 85% items in good stock\n⚠️ 3 items need reordering\n🔴 1 item critical (Bread)\n\n📈 Today\'s Prediction:\nExpected sales: ₹13,200\nPeak hours: 6-8 PM\n\nTip: Stock up on cold drinks — tomorrow\'s forecast shows 38°C! 🌡️', buttons: ['📋 View Full Report', '📦 Place Order', '📊 Check Stock'] },
    ],
    stock: [
        { type: 'user', text: 'Check stock of milk' },
        { type: 'bot', text: '🥛 Amul Milk (500ml)\n\n📦 Current Stock: 150 packets\n📊 Daily Sales Avg: 25 packets/day\n⏰ Days Until Restock: ~6 days\n💰 Stock Value: ₹3,750\n\n📈 Trend: Sales ↑8% this week\n🔮 Predicted demand (7 days): 190 packets\n\nStatus: ✅ Good stock level', buttons: ['📦 Order More', '📊 View History', '🔙 Main Menu'] },
    ],
};

export default function WhatsAppChat() {
    const [messages, setMessages] = useState([]);
    const [inputValue, setInputValue] = useState('');
    const [currentFlow, setCurrentFlow] = useState(null);
    const [flowIndex, setFlowIndex] = useState(0);
    const [isTyping, setIsTyping] = useState(false);
    const messagesEndRef = useRef(null);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const startFlow = (flowName) => {
        setCurrentFlow(flowName);
        setFlowIndex(0);
        setMessages([]);
        playFlow(DEMO_FLOWS[flowName], 0, []);
    };

    const playFlow = (flow, idx, currentMsgs) => {
        if (idx >= flow.length) {
            setCurrentFlow(null);
            return;
        }

        const msg = flow[idx];
        if (msg.type === 'bot') {
            setIsTyping(true);
            setTimeout(() => {
                setIsTyping(false);
                const newMsgs = [...currentMsgs, { ...msg, time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }];
                setMessages(newMsgs);
                setFlowIndex(idx + 1);
                // Auto-play next message if it's also a bot
                if (idx + 1 < flow.length && flow[idx + 1].type === 'bot') {
                    playFlow(flow, idx + 1, newMsgs);
                }
            }, 800 + Math.random() * 600);
        } else {
            setTimeout(() => {
                const newMsgs = [...currentMsgs, { ...msg, time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }];
                setMessages(newMsgs);
                setFlowIndex(idx + 1);
                // Auto-play next bot message
                if (idx + 1 < flow.length) {
                    playFlow(flow, idx + 1, newMsgs);
                }
            }, 500);
        }
    };

    const handleButtonClick = (btnText) => {
        if (currentFlow && DEMO_FLOWS[currentFlow]) {
            const flow = DEMO_FLOWS[currentFlow];
            if (flowIndex < flow.length) {
                playFlow(flow, flowIndex, messages);
            }
        }
    };

    const handleSend = () => {
        if (!inputValue.trim()) return;
        const userMsg = { type: 'user', text: inputValue, time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) };
        setMessages([...messages, userMsg]);
        setInputValue('');

        // Simple keyword matching for demo
        const lower = inputValue.toLowerCase();
        setTimeout(() => {
            setIsTyping(true);
            setTimeout(() => {
                setIsTyping(false);
                let response;
                if (lower.includes('stock') || lower.includes('check')) {
                    startFlow('stock');
                } else if (lower.includes('order') || lower.includes('forecast') || lower.includes('predict')) {
                    startFlow('forecast');
                } else if (lower.includes('report') || lower.includes('summary') || lower.includes('daily')) {
                    startFlow('daily');
                } else if (lower.includes('purchase') || lower.includes('buy') || lower.includes('bill')) {
                    startFlow('purchase');
                } else {
                    response = {
                        type: 'bot', text: 'I can help you with:\n\n📦 Check stock\n📊 Get forecast\n📋 Daily report\n📸 Add purchase\n\nJust type or tap a button below!',
                        buttons: ['📦 Check Stock', '📊 Get Forecast', '📋 Daily Report'],
                        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                    };
                    setMessages(prev => [...prev, response]);
                }
            }, 800);
        }, 300);
    };

    return (
        <div>
            <div className="page-header">
                <div>
                    <h2>💬 WhatsApp Chat Simulator</h2>
                    <p>Experience the Kirana-Connect conversational AI</p>
                </div>
            </div>

            <div style={{ display: 'flex', gap: 24 }}>
                {/* Flow selector */}
                <div style={{ width: 240, flexShrink: 0 }}>
                    <div className="card" style={{ marginBottom: 16 }}>
                        <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 12 }}>Demo Flows</h3>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                            {[
                                { id: 'onboarding', icon: '👋', label: 'Onboarding' },
                                { id: 'purchase', icon: '📸', label: 'Add Purchase (OCR)' },
                                { id: 'forecast', icon: '🔮', label: 'Get Forecast' },
                                { id: 'daily', icon: '📊', label: 'Daily Summary' },
                                { id: 'stock', icon: '📦', label: 'Check Stock' },
                            ].map(flow => (
                                <button
                                    key={flow.id}
                                    className={`sidebar-nav-item ${currentFlow === flow.id ? 'active' : ''}`}
                                    onClick={() => startFlow(flow.id)}
                                >
                                    <span className="nav-icon">{flow.icon}</span>
                                    <span>{flow.label}</span>
                                </button>
                            ))}
                        </div>
                    </div>

                    <div className="card">
                        <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 8 }}>About</h3>
                        <p style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                            This simulator demonstrates how Kirana store owners interact with our AI agent via WhatsApp.
                            Select a demo flow or type your own messages!
                        </p>
                        <div style={{ marginTop: 12, display: 'flex', flexDirection: 'column', gap: 4, fontSize: 11, color: 'var(--text-muted)' }}>
                            <div>✅ OCR receipt processing</div>
                            <div>✅ Voice note transcription</div>
                            <div>✅ AI demand forecasting</div>
                            <div>✅ Natural language queries</div>
                            <div>✅ Multilingual (EN/HI)</div>
                        </div>
                    </div>
                </div>

                {/* Chat window */}
                <div className="whatsapp-container" style={{ flex: 1, maxWidth: 440 }}>
                    <div className="whatsapp-header">
                        <div className="avatar">🏪</div>
                        <div className="chat-info">
                            <h3>Kirana-Connect AI</h3>
                            <p>{isTyping ? 'typing...' : 'online'}</p>
                        </div>
                        <div style={{ marginLeft: 'auto', display: 'flex', gap: 16, color: 'rgba(255,255,255,0.7)', fontSize: 18 }}>
                            <span>📞</span>
                            <span>📹</span>
                            <span>⋮</span>
                        </div>
                    </div>

                    <div className="whatsapp-messages">
                        {messages.length === 0 && (
                            <div style={{ textAlign: 'center', padding: '40px 20px' }}>
                                <div style={{ fontSize: 48, marginBottom: 12 }}>🏪</div>
                                <h3 style={{ fontSize: 16, color: 'var(--text-primary)', marginBottom: 8 }}>Kirana-Connect AI Agent</h3>
                                <p style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.6 }}>
                                    Select a demo flow from the left panel or type a message to start chatting!
                                </p>
                            </div>
                        )}

                        {messages.map((msg, i) => (
                            <div key={i} className={`chat-message ${msg.type}`}>
                                <div style={{ whiteSpace: 'pre-line' }}>{msg.text}</div>
                                {msg.buttons && (
                                    <div className="chat-buttons">
                                        {msg.buttons.map((btn, j) => (
                                            <button key={j} className="chat-btn" onClick={() => handleButtonClick(btn)}>{btn}</button>
                                        ))}
                                    </div>
                                )}
                                <div className="time">{msg.time}</div>
                            </div>
                        ))}

                        {isTyping && (
                            <div className="chat-message bot" style={{ padding: '10px 16px' }}>
                                <div style={{ display: 'flex', gap: 4 }}>
                                    <span className="pulse">⬤</span>
                                    <span className="pulse" style={{ animationDelay: '0.2s' }}>⬤</span>
                                    <span className="pulse" style={{ animationDelay: '0.4s' }}>⬤</span>
                                </div>
                            </div>
                        )}

                        <div ref={messagesEndRef} />
                    </div>

                    <div className="whatsapp-input-area">
                        <span style={{ fontSize: 20, cursor: 'pointer' }}>😊</span>
                        <span style={{ fontSize: 20, cursor: 'pointer' }}>📎</span>
                        <input
                            type="text"
                            id="whatsapp-input"
                            placeholder="Type a message..."
                            value={inputValue}
                            onChange={e => setInputValue(e.target.value)}
                            onKeyDown={e => e.key === 'Enter' && handleSend()}
                        />
                        <button className="whatsapp-send-btn" onClick={handleSend}>▶</button>
                    </div>
                </div>
            </div>
        </div>
    );
}
