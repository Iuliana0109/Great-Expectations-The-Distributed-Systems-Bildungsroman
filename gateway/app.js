const express = require('express');
const morgan = require('morgan');
const cors = require('cors');
const { createProxyMiddleware } = require('http-proxy-middleware');
require('dotenv').config();

const app = express();

// Environment Variables
const USER_SERVICE = process.env.USER_SERVICE_URL || 'http://user_management_service:5000';
const COMPETITION_SERVICE = process.env.COMPETITION_SERVICE_URL || 'http://competition_service:5001';

// Middleware
app.use(cors());
app.use(morgan('dev'));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Proxy Middleware to handle requests to User Management Service
app.use('/user', createProxyMiddleware({
    target: USER_SERVICE,
    changeOrigin: true,
    pathRewrite: {
        '^/user': '', // Remove /user prefix when forwarding
    },
}));

// Proxy Middleware to handle requests to Competition Service
app.use('/competition', createProxyMiddleware({
    target: COMPETITION_SERVICE,
    changeOrigin: true,
    pathRewrite: {
        '^/competition': '', // Remove /competition prefix when forwarding
    },
}));

// Start the Gateway
const PORT = process.env.PORT || 8080;
app.listen(PORT, () => {
    console.log(`Stateless Gateway is running on port ${PORT}`);
});
