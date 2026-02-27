const API_BASE_URL = 'http://localhost:8000/api/v1'; // Change for production
const STORE_ID = 'test-store-123';

// Main Initialization
document.addEventListener('DOMContentLoaded', () => {
    // Check which page we are on
    if (document.getElementById('val-total-products')) {
        loadDashboardData();
    }
});

// -- API Calls -- //
async function fetchDashboardData() {
    try {
        const res = await fetch(`${API_BASE_URL}/stores/${STORE_ID}/analytics/dashboard`);
        return await res.json();
    } catch (e) {
        console.error('Failed to fetch dashboard', e);
        return null; // Fallback to mock data if backend not running
    }
}

async function fetchPredictionsData() {
    try {
        const res = await fetch(`${API_BASE_URL}/stores/${STORE_ID}/analytics/predictions`);
        return await res.json();
    } catch (e) {
        console.error('Failed to fetch predictions', e);
        return null;
    }
}

// Global hook for chat.html
window.sendMessageToAPI = async function(messageText) {
    try {
        const res = await fetch(`${API_BASE_URL}/whatsapp/message`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                store_id: STORE_ID,
                sender: 'user',
                text: messageText
            })
        });
        const data = await res.json();
        return data.reply;
    } catch (e) {
        console.error('Msg error', e);
        return `Backend seems offline! Simulated response to: "${messageText}"\nPlease run uvicorn backend.main:app --reload`;
    }
};

// -- UI rendering -- //
async function loadDashboardData() {
    let data = await fetchDashboardData();
    let predictions = await fetchPredictionsData();
    
    // Fallback Mock Data if backend not running (for simple prototype viewing)
    if (!data) {
        data = {
            metrics: {
                total_products: 145,
                low_stock_count: 12,
                out_of_stock_count: 3,
                total_inventory_value: 45000
            },
            low_stock_alerts: [
                {name: 'Amul Butter 100g', quantity: 2, min_threshold: 5},
                {name: 'Parle G 50g', quantity: 1, min_threshold: 10},
                {name: 'Tata Salt 1kg', quantity: 0, min_threshold: 5}
            ]
        };
    }
    
    if (!predictions) {
        predictions = {
            predictions: [
                {name: 'Aashirvaad Atta 5kg', current_stock: 5, estimated_stockout_days: 2, suggested_order_qty: 20},
                {name: 'Maggi Noodles 140g', current_stock: 12, estimated_stockout_days: 1, suggested_order_qty: 50},
                {name: 'Sunrise Mustard Oil 1L', current_stock: 8, estimated_stockout_days: 4, suggested_order_qty: 15}
            ]
        };
    }
    
    // Update metric cards
    document.getElementById('val-total-products').textContent = data.metrics.total_products;
    document.getElementById('val-low-stock').textContent = data.metrics.low_stock_count;
    document.getElementById('val-out-of-stock').textContent = data.metrics.out_of_stock_count;
    document.getElementById('val-total-value').textContent = '₹' + data.metrics.total_inventory_value.toLocaleString('en-IN');
    
    // Render Alerts
    const alertsContainer = document.getElementById('low-stock-list');
    if (alertsContainer) {
        alertsContainer.innerHTML = '';
        data.low_stock_alerts.forEach(item => {
            const li = document.createElement('li');
            li.className = 'alert-item';
            
            li.innerHTML = `
                <div>
                    <div class="alert-title">${item.name}</div>
                    <div class="alert-sub">Stock: <strong style="color:var(--danger)">${item.quantity}</strong> (Min: ${item.min_threshold})</div>
                </div>
                <button class="action-btn" onclick="orderItem('${item.name}')">Order Now</button>
            `;
            alertsContainer.appendChild(li);
        });
    }
    
    // Render Predictions
    const dtBody = document.querySelector('#predictions-table tbody');
    if (dtBody) {
        dtBody.innerHTML = '';
        predictions.predictions.forEach(p => {
            const stockoutColor = p.estimated_stockout_days <= 2 ? 'color: var(--danger)' : '';
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><strong>${p.name}</strong></td>
                <td>${p.current_stock}</td>
                <td style="${stockoutColor}; font-weight: 600;">${p.estimated_stockout_days} days</td>
                <td>${p.suggested_order_qty} units</td>
                <td><button class="action-btn" onclick="orderItem('${p.name}', ${p.suggested_order_qty})">Auto-Order</button></td>
            `;
            dtBody.appendChild(tr);
        });
    }
}

window.orderItem = function(name, qty=10) {
    alert(`Mock Order Placed: Restocking ${qty} units of ${name} from preferred distributor.`);
};
