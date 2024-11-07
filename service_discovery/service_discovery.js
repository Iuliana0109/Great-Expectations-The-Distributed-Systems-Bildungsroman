const express = require('express');
   const app = express();

   // In-memory service registry
   let services = {};

   // Register a new service
   app.post('/register', (req, res) => {
    const { service_name, service_url } = req.body;
    if (service_name && service_url) {
        services[service_name] = service_url;
        console.log(`Service registered: ${service_name} at ${service_url}`);
        res.status(201).send({ message: 'Service registered successfully' });
    } else {
        res.status(400).send({ error: 'Invalid service registration request' });
    }
});

   // Deregister a service
   app.post('/deregister', (req, res) => {
       const { serviceName } = req.body;
       if (!serviceName || !services[serviceName]) {
           return res.status(400).json({ error: 'Service name is invalid or not registered' });
       }
       delete services[serviceName];
       console.log(`Service deregistered: ${serviceName}`);
       res.status(200).json({ message: 'Service deregistered successfully' });
   });

   // Get all registered services
   app.get('/services', (req, res) => {
       res.status(200).json(services);
   });

   // Status endpoint for the service discovery
   app.get('/status', (req, res) => {
       res.status(200).json({ status: 'Service Discovery is running' });
   });

   // Start the Service Discovery server
   const PORT = process.env.SERVICE_DISCOVERY_PORT || 9000;
   app.listen(PORT, () => {
       console.log(`Service Discovery running on port ${PORT}`);
   });



















































































































































































































































































services = {
    "user_management_service": "http://localhost:5000",
    "competition_service": "http://localhost:5001"
}
