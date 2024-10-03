const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');

const app = express();
const PORT = 3000;

// Service Discovery
const services = {
  userManagement: 'http://user-management:5000',
  competition: 'http://competition-service:5001',
};

// Proxy for User Management Service
app.use('/users', createProxyMiddleware({ target: services.userManagement, changeOrigin: true }));

// Proxy for Competition Service
app.use('/competitions', createProxyMiddleware({ target: services.competition, changeOrigin: true }));

app.listen(PORT, () => {
  console.log(`Gateway running on http://localhost:${PORT}`);
});
