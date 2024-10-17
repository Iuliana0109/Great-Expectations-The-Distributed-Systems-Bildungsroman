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

## Data Management
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
  "user_id": "string",
  "username": "string",
  "email": "string",
  "created_at": "timestamp"
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
  "token": "string",
  "user_id": "string",
  "expires_at": "timestamp"
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
  "user_id": "string",
  "username": "string",
  "email": "string",
  "profile_picture": "string",
  "bio": "string",
  "created_at": "timestamp"
}
```
- JWT Required: Yes

<br>

4. Get User Submissions

- Endpoint: /users/profile/submissions
- Method: GET
- Headers: ``JWT Token``
- Response (JSON):

```json
[
  {
    "submission_id": "string",
    "competition_id": "string",
    "title": "string",
    "content": "string",
    "created_at": "timestamp"
  }
]
```
- JWT Required: Yes

<br>

5. Get User Subscriptions

- Endpoint: /users/profile/subscriptions
- Method: GET
- Headers: ``JWT Token``
- Response (JSON):

```json
[
  {
    "competition_id": "string",
    "title": "string",
    "description": "string",
    "start_date": "date",
    "end_date": "date"
  }
]
```
- JWT Required: Yes

<br>

6. Subscribe to Competition

- Endpoint: /users/subscribe/{id}
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

### Competition Service Endpoints:
1. Get Active Competitions

- Endpoint: /competitions
- Method: GET
- Response (JSON):

```json
[
  {
    "competition_id": "string",
    "title": "string",
    "description": "string",
    "start_date": "date",
    "end_date": "date"
  }
]
```
- JWT Required: No

<br>

2. Get Competition Details

- Endpoint: /competitions/{id}
- Method: GET
- Response (JSON):

```json
{
  "competition_id": "string",
  "title": "string",
  "description": "string",
  "admin_id": "string",
  "start_date": "date",
  "end_date": "date",
  "created_at": "timestamp"
}
```
- JWT Required: No

<br>

3. Submit Entry to Competition

- Endpoint: /competitions/{id}/submit
- Method: POST
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

4. Like Submission

- Endpoint: /competitions/{id}/like/{submission_id}
- Method: POST
- Response (JSON):

```json
{
  "message": "Like added"
}
```
- JWT Required: Yes

<br>

5. Comment on Submission

- Endpoint: /competitions/{id}/comment/{submission_id}
- Method: POST
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
  "message": "Comment added"
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
