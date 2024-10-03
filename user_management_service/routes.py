from flask import Blueprint, request, jsonify
from models import db, User
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

bp = Blueprint('user', __name__)

# Register a new user
@bp.route('/users/register', methods=['POST'])
def register_user():
    try:
        data = request.json
        if not data.get('username') or not data.get('email') or not data.get('password'):
            return jsonify({'message': 'Missing required fields'}), 400

        # Check if the user already exists
        if User.query.filter((User.username == data['username']) | (User.email == data['email'])).first():
            return jsonify({'message': 'User already exists'}), 400
        
        new_user = User(username=data['username'], email=data['email'], password=data['password'])
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'user_id': new_user.id, 'username': new_user.username, 'email': new_user.email}), 201
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'message': 'An error occurred during registration'}), 500

# Test database connection
@bp.route('/test-db', methods=['GET'])
def test_db():
    try:
        users = User.query.all()
        return jsonify([user.username for user in users]), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

# Login user
@bp.route('/users/login', methods=['POST'])
def login_user():
    try:
        data = request.json
        if not data.get('email') or not data.get('password'):
            return jsonify({'message': 'Missing required fields'}), 400
        
        user = User.query.filter_by(email=data['email']).first()
        if user and user.password == data['password']:
            token = create_access_token(identity=user.id)
            return jsonify({'token': token, 'user_id': user.id}), 200
        
        return jsonify({'message': 'Invalid credentials'}), 401
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'message': 'An error occurred during login'}), 500

# Get user profile
@bp.route('/users/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404

        return jsonify({
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'created_at': user.created_at
        }), 200
    except Exception as e:
        return jsonify({'message': 'An error occurred while retrieving the profile'}), 500


# Delete user
@bp.route('/users/delete', methods=['DELETE'])
@jwt_required()
def delete_user():
    try:
        user_id = get_jwt_identity()  # Get user ID from JWT
        user = User.query.get(user_id)

        if user:
            db.session.delete(user)
            db.session.commit()
            return jsonify({'message': f'User {user.username} has been deleted'}), 200
        else:
            return jsonify({'message': 'User not found'}), 404

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'message': 'An error occurred while trying to delete the user'}), 500