# Distributed Literary Competition Platform

## Overview

The Literary Competition Platform is an interactive and engaging application designed for book lovers and aspiring writers. It offers a dynamic environment where users can unleash their creativity, participate in literary competitions, and connect with a vibrant community of literature enthusiasts.

![Alt text](plan.jpg)

## Application Suitability

The Literary Competition Platform is highly suitable for a distributed systems approach because it contains multiple components that can be managed and developed independently. Microservices ensure the separation of responsibilities, leading to easier scaling, better fault tolerance, and maintainability.

### Why Microservices?

**Modularity:** User management and Competition related features are different in nature and are best maintained as separate services. <br>
**Scalability:** Since competitions can involve a high number of participants, the ability to scale specific parts (e.g. the Competition Service) independently is crucial. <br>
**Fault tolerance:** If one service fails (e.g. notifications), the other service (e.g. user authentication) can continue to work without disrupting or crashing the whole app.

### Real-world example:
**Wattpad:** a platform for writers and readers to share stories and read user-generated content. It uses a microservices architecture to handle user accounts, story submissions, recommendations, and social interactions. <br>
**Medium:** a publishing platform that allows users to write and publish articles. It employs microservices to manage user profiles, content creation, recommendations, and social features.

## Running and Deploying the Project with Docker

1. **Install Docker and Docker Compose**: Ensure both Docker and Docker Compose are installed on your machine.
   - [Docker Installation Guide](https://docs.docker.com/get-docker/)
   - [Docker Compose Installation Guide](https://docs.docker.com/compose/install/)

2. **Clone the Project Repository**:
   ```bash
   git clone <repository_url>
   cd <repository_folder>
   ```

3. **Run the following command in the terminal**:
    ```bash
      docker-compose up --build
    ```

## Testing the Project

1. **Import Postman Collection**:
   - Import the provided Postman collection (`postman_collection.json`) into Postman to access all API endpoints.

2. **Configure Postman Environment**:
   - Set up the base URL in Postman (e.g., `http://localhost:8080`).

3. **Order of Endpoint Testing**:
   - **Step 1**: Register a new user with the `/user/register` endpoint.
   - **Step 2**: Log in using the `/user/login` endpoint to obtain a JWT token, which is required for authenticated requests.
   - **Step 3**: Test other endpoints, the documentation is [here](#endpoint-documentation).

## Service Boundaries

### User Management Service
The User Management Service is responsible for handling user registration, authentication (with JWT token), and managing user profiles. This service will interact with the Competition Service to verify user actions such as commenting, liking, or submitting content to competitions. Admins (users that create competitions) also use this service for authentication.

### Competition Service
This service will handle creating and managing competitions, submissions, likes, and comments. It will also notify users via WebSocket when someone likes or comments on their submission, replies to their comment, or what place they got in a competition. It hosts WebSocket for real-time notifications and supports gRPC for inter-service communication.

### Gateway 
Acts as the entry point for all incoming traffic and routes requests to the appropriate microservice.

### Service Discovery
Helps locate services using their IP and port, allowing services to scale or restart without disrupting communication.

### Cache
Will include information about currently active competitions, including details such as competition titles, descriptions, start and end dates.

### Databases
Each service has a separate PostgreSQL database.

### Load Balancer
Distributes incoming requests to multiple instances of the microservices based on load. Implements Round-Robin initially, with an upgrade to service-load-based distribution as required.

### Circuit Breaker
Monitors API calls between services. If a service fails 3 times (based on timeout limits), it will temporarily stop forwarding requests to that service, logging the failure for later recovery.

### ELK Stack (Elasticsearch, Logstash, Kibana)

- **Purpose**: Aggregates and visualizes logs from all services. Provides a centralized logging solution, making it easier to monitor, troubleshoot, and analyze system performance.
- **Components**:
  - **Elasticsearch**: Stores and indexes logs.
  - **Logstash**: Collects, processes, and forwards logs to Elasticsearch.
  - **Kibana**: Visualizes logs from Elasticsearch, allowing real-time monitoring.

### Database Redundancy & Replication

- **Purpose**: Implements failover and data replication for high availability.
- **Implementation**: Configures replication for at least one database with a minimum of three replicas (additional replicas if required). This ensures data durability and availability in case of service failure.

### Consistent Hashing for Cache

- **Purpose**: Distributes cached data efficiently across multiple Redis nodes to ensure high availability.
- **Description**: Uses consistent hashing for better cache distribution and scalability, ensuring balanced load across cache nodes and avoiding data loss during scaling.

### Data Warehouse with ETL

- **Purpose**: Consolidates data from all services into a centralized data warehouse for periodic analysis and reporting.
- **Implementation**: An ETL process (Extract, Transform, Load) is created to periodically fetch data from microservices and load it into the warehouse, supporting data analysis and reporting tasks.

### Deployment Diagram:
![Deployment Diagram](Deployment%20Diagram.png)


## Technology Stack
- Python for both services
- JS for the Gateway
- HTTP/REST, WebSocket and gRPC for Competition Service
- Redis for cache
- PostgreSQL for databases
- Docker for deployment and scaling
- Postman for testing

## Endpoint Documentation
### User Management Service Endpoints:
1. Register User

- Endpoint: /users/register
- Method: POST
- Request Body (JSON):

```json
{
    "username": "string",
    "email": "string",
    "password": "string"
}
```
- Response (JSON):

```json
{
    "created_at": "string",
    "email": "string",
    "user_id": "string",
    "username": "string"
}
```
- JWT Required: No

<br>

2. Login

- Endpoint: /users/login
- Method: POST
- Request Body (JSON):

```json
{
  "email": "string",
  "password": "string"
}
```
- Response (JSON):

```json
{
    "expires_at": "string",
    "token": "string",
    "user_id": "string"
}
```
- JWT Required: No (Token is issued upon login)

<br>

3. Get User Profile

- Endpoint: /users/profile
- Method: GET
- Heraders: ``JWT Token``
- Response (JSON):

```json
{
    "created_at": "string",
    "email": "string",
    "user_id": "string",
    "username": "string"
}
```
- JWT Required: Yes

<br>

4. Get User Subscriptions

- Endpoint: /users/profile/subscriptions
- Method: GET
- Headers: ``JWT Token``
- Response (JSON):

```json
[
    {
        "competition_id": "string",
        "created_at": "string",
        "subscription_id": "string"
    }
]
```
- JWT Required: Yes

<br>
<br>

5. Subscribe to Competition

- Endpoint: /users/subscribe/{competition id}
- Method: POST
- Headers: ``JWT Token``
- Response (JSON):

```json
{
  "message": "Subscription successful"
}
```
- JWT Required: Yes

<br>
<br>

6. Delete User
- Endpoint: /users/delete/{user id}
- Method: DELETE
- Headers: ``JWT Token``
- Response (JSON):

```json
{
  "message": "User profile deleted successfully"
}
```

<br><br>

7. Status Endpoint
- Endpoint: /users/status
- Method: GET
- Response (JSON):

```json
{
  "status": "User Management Service is running"
}
```
- JWT Required: No

### Competition Service Endpoints:

1. Create Competition

- Endpoint: /competitions
- Method: POST
- Headers: ``JWT Token``
- Response (JSON):

```json
{
  "competition_id": "string",
  "message": "Competition created successfully"
}
```
- JWT Required: Yes

<br>

2. Get Competitions

- Endpoint: /competitions
- Method: GET
- Headers: ``JWT Token``
- Response (JSON):

```json
[
    {
        "competition_id": "string",
        "description": "string",
        "end_date": "string",
        "start_date": "string",
        "title": "string"
    }
]
```
- JWT Required: yes

<br>

3. Get Competition by ID

- Endpoint: /competitions/{competition id}
- Method: GET
- Response (JSON):

```json
{
    "competition_id": "string",
    "created_at": "string",
    "description": "string",
    "end_date": "string",
    "start_date": "string",
    "submissions": [
        {
            "comments_count": "integer",
            "content": "string",
            "created_at": "string",
            "likes_count": "integer",
            "submission_id": "string",
            "title": "string",
            "user_id": "string"
        }
    ],
    "title": "string"
}
```
- JWT Required: No

<br>

4. Submit Entry to Competition

- Endpoint: /competitions/{competition id}/submit
- Method: POST
- Headers: ``JWT Token``
- Request Body:

```json
{
  "title": "string",
  "content": "string"
}
```

- Response (JSON):

```json
{
  "submission_id": "string",
  "message": "Submission successful"
}
```
- JWT Required: Yes

<br>

5. Get Submission by id

- Endpoint: /submissions/{submission id}
- Method: POST
- Response (JSON):

```json
{
    "comments": "integer",
    "competition_id": "string",
    "content": "string",
    "created_at": "string",
    "likes": "integer",
    "submission_id": "string",
    "title": "string",
    "user_id": "string"
}
```
- JWT Required: No

<br>

6. Like Submission

- Endpoint: /competitions/{id}/like/{submission_id}
- Method: POST
- Headers: ``JWT Token``
- Response (JSON):

```json
{
  "message": "Like added"
}
```
- JWT Required: Yes

<br>

7. Comment on Submission

- Endpoint: /competitions/{id}/comment/{submission_id}
- Method: POST
- Headers: ``JWT Token``
- Request:
```json
{
  "content": "string"
}
```

- Response (JSON):
```json
{
  "comment_id": "string",
  "message": "string"
}
```
- JWT Required: Yes

<br>

8. Delete a Competition

- Endpoint: /competitions/{competition id}
- Method: DELETE
- Headers: ``JWT Token``
- Response (JSON):
```json
{
  "message": "Competition deleted successfully"
}
```
- JWT Required: Yes

<br>

8. Delete Submission by id

- Endpoint: /submissions/{submission id}
- Method: DELETE
- Headers: ``JWT Token``
- Response (JSON):
```json
{
  "message": "Submission deleted successfully"
}
```
- JWT Required: Yes

<br>

### WebSockets
WebSockets are used for all users subscribed to a competition to get notified of all new submissions

**How Does It Work:** <br>
A WebSocket connection is established between the client (browser or app) and the Competition Service when the user logs (already has some submissions) or when the user submits something to a competition. When a submission occurs, the server sends a real-time notification through the open WebSocket connection to notify the user.

1. User A submits an entry via a POST request.
2. The server processes the submission and updates the database.
3. The server sends a WebSocket notification to User B: “New submission”
4. User B instantly receives the notification in their browser or app through the WebSocket.

<br>

## Deployment and Scaling

Docker containers will be used to encapsulate each service. Then, services will be deployed using Docker Compose. <br>
Each service can be scaled horizontally by adjusting the replica count in the Docker Compose file.
