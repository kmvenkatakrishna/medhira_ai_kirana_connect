import axios from 'axios';

const API_BASE = 'http://localhost:8000/api/v1';
const STORE_ID = 1; // Demo store

const api = axios.create({
    baseURL: API_BASE,
    timeout: 15000,
});

// Dashboard
export const getDashboard = () => api.get(`/stores/${STORE_ID}/analytics/dashboard`);

// Inventory
export const getInventory = (params = {}) => api.get(`/stores/${STORE_ID}/inventory`, { params });
export const getInventorySummary = () => api.get(`/stores/${STORE_ID}/inventory/summary`);
export const getLowStock = () => api.get(`/stores/${STORE_ID}/inventory/low-stock`);
export const updateInventory = (productId, data) => api.put(`/stores/${STORE_ID}/inventory/${productId}`, data);
export const recordPurchase = (data) => api.post(`/stores/${STORE_ID}/inventory/purchase`, data);
export const recordSale = (data) => api.post(`/stores/${STORE_ID}/inventory/sale`, data);

// Products
export const getProducts = (params = {}) => api.get('/products', { params });
export const getCategories = () => api.get('/products/categories');

// Analytics
export const getSalesTrends = (days = 30) => api.get(`/stores/${STORE_ID}/analytics/sales-trends`, { params: { days } });
export const getTopProducts = (days = 30) => api.get(`/stores/${STORE_ID}/analytics/top-products`, { params: { days } });
export const getCategoryBreakdown = (days = 30) => api.get(`/stores/${STORE_ID}/analytics/category-breakdown`, { params: { days } });
export const getDailyReport = () => api.get(`/stores/${STORE_ID}/reports/daily`);

// Predictions
export const getPredictions = () => api.get(`/stores/${STORE_ID}/predictions`);
export const generatePredictions = () => api.post(`/stores/${STORE_ID}/predictions/generate`);
export const getPredictionSummary = () => api.get(`/stores/${STORE_ID}/predictions/summary`);

// Orders
export const getOrders = (status) => api.get(`/stores/${STORE_ID}/orders`, { params: status ? { status } : {} });
export const generateOrderSuggestions = () => api.post(`/stores/${STORE_ID}/orders/generate`);
export const createOrder = (data) => api.post(`/stores/${STORE_ID}/orders`, data);
export const updateOrderStatus = (orderId, status) => api.put(`/stores/${STORE_ID}/orders/${orderId}/status`, null, { params: { status } });
export const getDistributors = () => api.get(`/stores/${STORE_ID}/orders/distributors`);

// Store
export const getStore = () => api.get(`/stores/${STORE_ID}`);

export default api;
