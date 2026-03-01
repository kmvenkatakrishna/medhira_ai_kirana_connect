/**
 * KiranaConnect API Client
 * Handles all communication with the FastAPI backend.
 */

const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000'
    : '';  // Same origin in production

const DEFAULT_STORE = 'S001';

class KiranaAPI {
    static BASE_URL = API_BASE;
    static async fetch(endpoint, options = {}) {
        try {
            const res = await fetch(`${API_BASE}${endpoint}`, {
                headers: { 'Content-Type': 'application/json', ...options.headers },
                ...options
            });
            return await res.json();
        } catch (err) {
            console.error(`API Error [${endpoint}]:`, err);
            return null;
        }
    }

    // ── Stores ──
    static getStores() { return this.fetch('/api/v1/stores'); }
    static getStore(id) { return this.fetch(`/api/v1/stores/${id}`); }

    // ── Inventory ──
    static getInventory(storeId = DEFAULT_STORE, category = '') {
        const q = category ? `?category=${category}` : '';
        return this.fetch(`/api/v1/stores/${storeId}/inventory${q}`);
    }
    static getLowStock(storeId = DEFAULT_STORE) {
        return this.fetch(`/api/v1/stores/${storeId}/inventory/low-stock`);
    }
    static getInventoryItem(storeId, productId) {
        return this.fetch(`/api/v1/stores/${storeId}/inventory/${productId}`);
    }

    // ── Predictions ──
    static getPredictions(storeId = DEFAULT_STORE) {
        return this.fetch(`/api/v1/stores/${storeId}/predictions`);
    }
    static getProductPrediction(storeId, productId) {
        return this.fetch(`/api/v1/stores/${storeId}/predictions/${productId}`);
    }

    // ── Orders ──
    static getOrders(storeId = DEFAULT_STORE, status = '') {
        const q = status ? `?status=${status}` : '';
        return this.fetch(`/api/v1/stores/${storeId}/orders${q}`);
    }
    static generateOrder(storeId = DEFAULT_STORE) {
        return this.fetch(`/api/v1/stores/${storeId}/orders/generate`, { method: 'POST' });
    }
    static placeOrder(storeId, orderId) {
        return this.fetch(`/api/v1/stores/${storeId}/orders/${orderId}/place`, { method: 'POST' });
    }

    // ── Analytics ──
    static getDailyReport(storeId = DEFAULT_STORE) {
        return this.fetch(`/api/v1/stores/${storeId}/reports/daily`);
    }
    static getWeeklyReport(storeId = DEFAULT_STORE) {
        return this.fetch(`/api/v1/stores/${storeId}/reports/weekly`);
    }
    static getMonthlyReport(storeId = DEFAULT_STORE) {
        return this.fetch(`/api/v1/stores/${storeId}/reports/monthly`);
    }
    static getSalesTrends(storeId = DEFAULT_STORE, days = 30) {
        return this.fetch(`/api/v1/stores/${storeId}/analytics/sales-trends?days=${days}`);
    }
    static getTopProducts(storeId = DEFAULT_STORE) {
        return this.fetch(`/api/v1/stores/${storeId}/analytics/top-products`);
    }
    static getAnalyticsSummary(storeId = DEFAULT_STORE) {
        return this.fetch(`/api/v1/stores/${storeId}/analytics/summary`);
    }

    // ── Products ──
    static getProducts(category = '', search = '') {
        const params = new URLSearchParams();
        if (category) params.set('category', category);
        if (search) params.set('search', search);
        const q = params.toString() ? `?${params}` : '';
        return this.fetch(`/api/v1/products${q}`);
    }
    static getCategories() { return this.fetch('/api/v1/products/categories'); }

    // ── Chat ──
    static sendMessage(message, storeId = DEFAULT_STORE) {
        return this.fetch('/api/v1/chat', {
            method: 'POST',
            body: JSON.stringify({ message, store_id: storeId })
        });
    }

    // ── Distributors ──
    static getDistributors() { return this.fetch('/api/v1/distributors'); }

    // ── AI Intelligence ──
    static getAIInsights(storeId = DEFAULT_STORE) {
        return this.fetch(`/api/v1/stores/${storeId}/ai/insights`);
    }
    static getAIForecast(storeId = DEFAULT_STORE, topN = 15) {
        return this.fetch(`/api/v1/stores/${storeId}/ai/forecast?top_n=${topN}`);
    }
    static getAIAccuracy(storeId = DEFAULT_STORE) {
        return this.fetch(`/api/v1/stores/${storeId}/ai/accuracy`);
    }
    static getSmartReorder(storeId = DEFAULT_STORE) {
        return this.fetch(`/api/v1/stores/${storeId}/ai/smart-reorder`);
    }
    static getExpiryRisk(storeId = DEFAULT_STORE) {
        return this.fetch(`/api/v1/stores/${storeId}/ai/expiry-risk`);
    }
    static getCrossSell(storeId = DEFAULT_STORE) {
        return this.fetch(`/api/v1/stores/${storeId}/ai/cross-sell`);
    }
}

// Utility: Format currency
function formatCurrency(amount) {
    return '₹' + Number(amount).toLocaleString('en-IN', { maximumFractionDigits: 0 });
}

// Utility: Format number
function formatNumber(num) {
    return Number(num).toLocaleString('en-IN');
}

// Utility: Relative time
function timeAgo(dateStr) {
    const diff = Date.now() - new Date(dateStr).getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 60) return `${mins}m ago`;
    const hrs = Math.floor(mins / 60);
    if (hrs < 24) return `${hrs}h ago`;
    return `${Math.floor(hrs / 24)}d ago`;
}

// Utility: Current time string
function currentTime() {
    return new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
}
