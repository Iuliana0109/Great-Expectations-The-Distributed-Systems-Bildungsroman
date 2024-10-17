from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env

db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()
socketio = SocketIO()

def create_app():
    app = Flask(__name__)

    # Load configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")

    # Register Blueprints
    from routes import competition_routes
    app.register_blueprint(competition_routes)

    return app

if __name__ == "__main__":
    app = create_app()
    socketio.run(app, host="0.0.0.0", port=5001, debug=True)
