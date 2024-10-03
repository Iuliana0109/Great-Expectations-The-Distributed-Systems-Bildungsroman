from flask import Blueprint, request, jsonify
from models import db, Competition
from flask_jwt_extended import jwt_required, get_jwt_identity

bp = Blueprint('competition', __name__)

# Create a new competition
@bp.route('/competitions', methods=['POST'])
@jwt_required()
def create_competition():
    try:
        data = request.json
        if not data.get('title') or not data.get('description') or not data.get('start_date') or not data.get('end_date'):
            return jsonify({'message': 'Missing required fields'}), 400

        new_competition = Competition(
            title=data['title'],
            description=data['description'],
            start_date=data['start_date'],
            end_date=data['end_date']
        )
        db.session.add(new_competition)
        db.session.commit()
        return jsonify({'competition_id': new_competition.id, 'title': new_competition.title}), 201
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'message': 'An error occurred during competition creation'}), 500

# Get all competitions
@bp.route('/competitions', methods=['GET'])
def get_competitions():
    try:
        competitions = Competition.query.all()
        return jsonify([{
            'competition_id': comp.id,
            'title': comp.title,
            'description': comp.description,
            'start_date': comp.start_date,
            'end_date': comp.end_date
        } for comp in competitions]), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'message': 'An error occurred while retrieving competitions'}), 500

# Get competition by ID
@bp.route('/competitions/<int:competition_id>', methods=['GET'])
def get_competition(competition_id):
    try:
        competition = Competition.query.get(competition_id)
        if not competition:
            return jsonify({'message': 'Competition not found'}), 404

        return jsonify({
            'competition_id': competition.id,
            'title': competition.title,
            'description': competition.description,
            'start_date': competition.start_date,
            'end_date': competition.end_date
        }), 200
    except Exception as e:
        return jsonify({'message': 'An error occurred while retrieving the competition'}), 500

# Delete a competition
@bp.route('/competitions/<int:competition_id>', methods=['DELETE'])
@jwt_required()
def delete_competition(competition_id):
    try:
        competition = Competition.query.get(competition_id)
        if competition:
            db.session.delete(competition)
            db.session.commit()
            return jsonify({'message': f'Competition {competition.title} has been deleted'}), 200
        else:
            return jsonify({'message': 'Competition not found'}), 404
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'message': 'An error occurred while trying to delete the competition'}), 500
