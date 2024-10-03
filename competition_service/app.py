from flask import Flask
from models import db
from routes import bp as competition_bp
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object('config.Config')

@app.route('/')
def index():
    return "Welcome to the Competition Service!"

db.init_app(app)
migrate = Migrate(app, db)  # Initialize Flask-Migrate with app and db
jwt = JWTManager(app)

app.register_blueprint(competition_bp)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001)
