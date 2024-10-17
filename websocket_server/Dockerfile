# websocket_server/Dockerfile
FROM python:3.10-slim

WORKDIR /websocket_server

# Copy code to the container
COPY . .

# Install necessary dependencies
RUN pip install websockets redis asyncio

# Expose the WebSocket server port
EXPOSE 6789

# Command to run the WebSocket server
CMD ["python", "websocket_server.py"]
