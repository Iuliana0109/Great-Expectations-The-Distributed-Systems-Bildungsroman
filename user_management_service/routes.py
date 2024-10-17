import requests
from flask import Blueprint, request, jsonify
from app import db, bcrypt
from models import User, Subscription
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import datetime

user_routes = Blueprint('user_routes', __name__)

@user_routes.route('/users/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(username=data['username'], email=data['email'], password=hashed_password)
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({
            "user_id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
            "created_at": new_user.created_at
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@user_routes.route('/users/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if user and bcrypt.check_password_hash(user.password, data['password']):
        expires = datetime.timedelta(hours=1)
        access_token = create_access_token(identity=user.id, expires_delta=expires)
        return jsonify({"token": access_token, "user_id": user.id, "expires_at": str(datetime.datetime.utcnow() + expires)}), 200
    return jsonify({"error": "Invalid credentials"}), 401

@user_routes.route('/users/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user:
        return jsonify({
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "created_at": user.created_at
        }), 200
    return jsonify({"error": "User not found"}), 404

@user_routes.route('/users/subscribe/<competition_id>', methods=['POST'])
@jwt_required()
def subscribe(competition_id):
    user_id = get_jwt_identity()
    new_subscription = Subscription(user_id=user_id, competition_id=competition_id)
    try:
        db.session.add(new_subscription)
        db.session.commit()
        return jsonify({"message": "Subscription successful"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@user_routes.route('/users/validate', methods=['POST'])
@jwt_required()
def validate_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user:
        return jsonify({"user_id": user_id, "valid": True}), 200
    return jsonify({"valid": False}), 404

@user_routes.route('/users/subscriptions', methods=['GET'])
@jwt_required()
def get_subscriptions():
    user_id = get_jwt_identity()
    subscriptions = Subscription.query.filter_by(user_id=user_id).all()
    if subscriptions:
        result = [{
            "subscription_id": sub.id,
            "competition_id": sub.competition_id,
            "created_at": sub.created_at
        } for sub in subscriptions]
        return jsonify(result), 200
    return jsonify([]), 200

@user_routes.route('/users/delete', methods=['DELETE'])
@jwt_required()
def delete_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user:
        try:
            db.session.delete(user)
            db.session.commit()
            return jsonify({"message": "User profile deleted successfully"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400
    return jsonify({"error": "User not found"}), 404

@user_routes.route('/test-db', methods=['GET'])
def test_db():
    try:
        # Test database connection
        db.session.execute('SELECT 1')
        return jsonify({"message": "Database connection is successful"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500