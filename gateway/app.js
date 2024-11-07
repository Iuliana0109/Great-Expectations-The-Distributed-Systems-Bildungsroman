// Import necessary libraries
const express = require('express');
const axios = require('axios');
const morgan = require('morgan');
const cors = require('cors');
const redis = require('redis');
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

async function handleServiceRequest(serviceUrl, req, res) {
    try {
        console.log(`Forwarding request to: ${serviceUrl}${req.url}`);
        const response = await axios({
            method: req.method,
            url: `${serviceUrl}${req.url}`,
            data: req.body,
            headers: {
                'Content-Type': req.headers['content-type'] || 'application/json',
                'Authorization': req.headers['authorization'] || ''
            },
            timeout: 5000
        });
        res.status(response.status).send(response.data);
    } catch (error) {
        console.error(`Error forwarding request: ${error.message}`);
        const status = error.response ? error.response.status : 500;
        const message = error.response?.data?.error || 'Something went wrong. Please try again later.';
        res.status(status).send({ error: message });
    }
}

// Routes: Forwarding to User Management Service
app.all('/user/*', (req, res) => {
    const modifiedUrl = req.url.replace('/user', ''); 
    handleServiceRequest(USER_SERVICE_URL, { ...req, url: modifiedUrl }, res);
});

// Routes: Forwarding to Competition Service
app.all('/competition/*', async (req, res) => {
    const modifiedUrl = req.url.replace('/competition', ''); // Remove '/competition' from the path

    if (req.method === 'GET' && modifiedUrl === '/active') {
        try {
            // Handle caching for GET /competition/active
            const cachedCompetitions = await redisClient.get('activeCompetitions');
            if (cachedCompetitions) {
                console.log('Cache hit for active competitions');
                return res.status(200).send(JSON.parse(cachedCompetitions));
            }

            console.log('Cache miss for active competitions');
            const response = await axios.get(`${COMPETITION_SERVICE_URL}/competitions`);
            const activeCompetitions = response.data;

            await redisClient.setEx('activeCompetitions', 3600, JSON.stringify(activeCompetitions));
            return res.status(response.status).send(activeCompetitions);
        } catch (error) {
            console.error(`Error forwarding request: ${error.message}`);
            const status = error.response ? error.response.status : 500;
            const message = error.response?.data?.error || 'Something went wrong. Please try again later.';
            return res.status(status).send({ error: message });
        }
    } else {
        // Remove the incorrect use of `{ ...req, url: modifiedUrl }` which might be causing issues.
        req.url = modifiedUrl; // Correct the URL path
        handleServiceRequest(COMPETITION_SERVICE_URL, req, res);
    }
});

// Start the Gateway
const PORT = process.env.PORT || 8080;
app.listen(PORT, () => {
    console.log(`Gateway is running on port ${PORT}`);
});