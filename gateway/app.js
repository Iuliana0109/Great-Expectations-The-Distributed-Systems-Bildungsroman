const express = require('express');
const axios = require('axios');
const morgan = require('morgan');
const cors = require('cors');
const redis = require('redis');
const opossum = require('opossum'); // circuitt breaker
require('dotenv').config();

const app = express();

// Environment Variables
const USER_SERVICE_URL = process.env.USER_SERVICE_URL || 'http://user_management_service:5000';
const COMPETITION_SERVICE_URL = process.env.COMPETITION_SERVICE_URL || 'http://competition_service:5001';
const REDIS_URL = process.env.REDIS_URL || 'redis://redis:6379';

// Redis Client Setup
const redisClient = redis.createClient({ url: REDIS_URL });
redisClient.connect().catch(console.error);

// Middleware
app.use(cors());
app.use(morgan('dev'));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Circuit Breaker Options
const circuitBreakerOptions = {
    timeout: 2000,
    errorThresholdPercentage: 20,
    resetTimeout: 15000,
};

// Create Circuit Breakers for each service
const userServiceBreaker = new opossum(async (reqConfig) => {
    const response = await axios(reqConfig);
    return response.data;
}, circuitBreakerOptions);

const competitionServiceBreaker = new opossum(async (reqConfig) => {
    const response = await axios(reqConfig);
    return response.data;
}, circuitBreakerOptions);

// Utility function to route through the circuit breaker
async function routeThroughCircuitBreaker(breaker, req, serviceUrl) {
    const reqConfig = {
        method: req.method,
        url: `${serviceUrl}${req.url}`,
        data: req.body,
        headers: {
            'Content-Type': req.headers['content-type'] || 'application/json',
            'Authorization': req.headers['authorization'] || '',
        },
    };

    try {
        // Attempt to fire the circuit breaker
        return await breaker.fire(reqConfig);
    } catch (error) {
        console.error(`Failure captured by circuit breaker: ${error.message}`);

        // Track the reroute
        trackReroute();

        // Throw the error to continue handling it
        throw new Error('Service Unavailable');
    }
}


// Handle Circuit Breaker Events
[userServiceBreaker, competitionServiceBreaker].forEach((breaker, index) => {
    const serviceName = index === 0 ? "User Service" : "Competition Service";

    breaker.on('open', () => {
        console.error(`Circuit breaker for ${serviceName} is now OPEN`);
    });

    breaker.on('halfOpen', () => {
        console.log(`Circuit breaker for ${serviceName} is now HALF-OPEN`);
    });

    breaker.on('close', () => {
        console.log(`Circuit breaker for ${serviceName} is now CLOSED`);
    });

    breaker.on('failure', (error) => {
        console.error(`Circuit breaker for ${serviceName} recorded a FAILURE: ${error.message}`);
    });

    breaker.on('success', () => {
        console.log(`Circuit breaker for ${serviceName} recorded a SUCCESS`);
    });
});

// Routes: Forwarding to User Management Service
app.all('/user/*', async (req, res) => {
    try {
        // Remove '/user' from the forwarded path
        req.url = req.url.replace('/user', '');
        const result = await routeThroughCircuitBreaker(userServiceBreaker, req, USER_SERVICE_URL);
        res.status(200).send(result);
    } catch (error) {
        console.error(`User service error: ${error.message}`);
        res.status(503).send({ error: 'User service is unavailable. Please try again later.' });
    }
});


// Routes: Forwarding to Competition Service
app.all('/competition/*', async (req, res) => {
    try {
        // Remove '/competition' from the forwarded path
        req.url = req.url.replace('/competition', '');
        const result = await routeThroughCircuitBreaker(
            competitionServiceBreaker,
            req,
            COMPETITION_SERVICE_URL
        );
        res.status(200).send(result);
    } catch (error) {
        console.error(`Competition service error: ${error.message}`);
        res.status(503).send({ error: 'Competition service is unavailable. Please try again later.' });
    }
});

// Initialize counters
let competitionFailures = 0;
let competitionSuccesses = 0;

competitionServiceBreaker.on('failure', (error) => {
    competitionFailures++;
    console.error(`Circuit breaker for Competition Service recorded a FAILURE: ${error.message}`);
});

competitionServiceBreaker.on('success', () => {
    competitionSuccesses++;
    console.log(`Circuit breaker for Competition Service recorded a SUCCESS`);
});


app.get('/breaker-status', (req, res) => {
    res.json({
        competitionServiceBreaker: {
            state: competitionServiceBreaker.opened ? 'OPEN' : competitionServiceBreaker.pendingClose ? 'HALF-OPEN' : 'CLOSED',
            failureCount: competitionServiceBreaker.stats.failures,
            successCount: competitionServiceBreaker.stats.successes,
            rerouteCount,
        },
        userServiceBreaker: {
            state: userServiceBreaker.opened ? 'OPEN' : userServiceBreaker.pendingClose ? 'HALF-OPEN' : 'CLOSED',
            failureCount: 0,
            successCount: 0,
        },
    });
});


// Reroute tracking
let rerouteCount = 0;
const rerouteThreshold = 5; // Trip breaker after 5 reroutes
const rerouteWindowMs = 5000; // Time window for counting reroutes (5 seconds)

// Reset reroute count periodically
setInterval(() => {
    rerouteCount = 0; // Reset the counter every 5 seconds
}, rerouteWindowMs);

// Utility to track reroutes
function trackReroute() {
    rerouteCount++;
    console.log(`Reroute occurred. Total reroutes in current window: ${rerouteCount}`);
    if (rerouteCount >= rerouteThreshold) {
        competitionServiceBreaker.open(); // Force trip the circuit breaker
        console.error(`Circuit breaker for Competition Service is tripped due to multiple reroutes`);
    }
}


// Start the Gateway
const PORT = process.env.PORT || 8080;
app.listen(PORT, () => {
    console.log(`Gateway is running on port ${PORT}`);
});
