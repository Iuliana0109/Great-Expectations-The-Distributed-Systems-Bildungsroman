# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from flask_bcrypt import Bcrypt
# from flask_jwt_extended import JWTManager
# from dotenv import load_dotenv
# import os

# load_dotenv()  # Load environment variables from .env

# db = SQLAlchemy()
# bcrypt = Bcrypt()
# jwt = JWTManager()

# def create_app():
#     app = Flask(__name__)

#     # Load configuration
#     app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
#     app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')

#     # Initialize extensions
#     db.init_app(app)
#     bcrypt.init_app(app)
#     jwt.init_app(app)

#     # Register Blueprints
#     from routes import competition_routes
#     app.register_blueprint(competition_routes)

#     return app

# # Create the app instance at the module level
# app = create_app()

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5001, debug=True)

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os
import threading
import asyncio
import websockets
import json
import redis

load_dotenv()  # Load environment variables from .env

db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()

# Get environment variables
SERVICE_DISCOVERY_URL = os.getenv('SERVICE_DISCOVERY_URL', 'http://service_discovery:9000')

def register_service():
    service_data = {
        "service_name": "competition_service",
        "service_url": "http://competition_service:5001"
    }
    try:
        response = requests.post("http://service_discovery:9000/register", json=service_data)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error registering service: {e}")

# Redis client
redis_client = redis.StrictRedis(host='redis', port=6379, db=0)

def create_app():
    app = Flask(__name__)

    # Load configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # Register Blueprints
    from routes import competition_routes
    app.register_blueprint(competition_routes)

    return app

# Create the app instance at the module level
app = create_app()

# WebSocket server code
connected_clients = {}

async def websocket_handler(websocket, path):
    try:
        async for message in websocket:
            data = json.loads(message)
            action = data.get("action")

            if action == "subscribe":
                competition_id = data.get("competition_id")
                if competition_id:
                    if competition_id not in connected_clients:
                        connected_clients[competition_id] = []
                    connected_clients[competition_id].append(websocket)
                    await websocket.send(json.dumps({"status": "subscribed", "competition_id": competition_id}))
            elif action == "new_submission":
                competition_id = data.get("competition_id")
                if competition_id in connected_clients:
                    # Notify all subscribers of the new submission
                    for client in connected_clients[competition_id]:
                        if client != websocket:
                            await client.send(json.dumps({"message": "New submission received", "data": data}))
    except websockets.ConnectionClosed:
        pass
    finally:
        # Remove disconnected clients from all rooms
        for subscribers in connected_clients.values():
            if websocket in subscribers:
                subscribers.remove(websocket)

def start_websocket_server():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    start_server = websockets.serve(websocket_handler, "0.0.0.0", 6480)
    loop.run_until_complete(start_server)
    loop.run_forever()

# Start WebSocket server in a separate thread
threading.Thread(target=start_websocket_server, daemon=True).start()

if __name__ == "__main__":
    rregister_service()
    app.run(host="0.0.0.0", port=5001, debug=True)
