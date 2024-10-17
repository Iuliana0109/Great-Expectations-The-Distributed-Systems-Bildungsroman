import asyncio
import websockets
import requests
from flask import Blueprint, request, jsonify
from app import db
from models import Competition, Submission, Like, Comment
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_socketio import emit, join_room
import datetime
import json

competition_routes = Blueprint('competition_routes', __name__)

def validate_user(headers):
    try:
        response = requests.post(
            "http://user_management_service:5000/users/validate",
            headers=headers
        )
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Error validating user: {e}")
        return False

@competition_routes.route('/competitions', methods=['POST'])
@jwt_required()
def create_competition():
    headers = {"Authorization": request.headers.get("Authorization")}
    if not validate_user(headers):
        return jsonify({"error": "User validation failed"}), 401

    # Retrieve the user ID from the JWT token
    user_id = get_jwt_identity()

    # Attempt to load JSON data from the request
    data = None
    try:
        data = request.get_json()
    except Exception:
        # Fallback to manually loading JSON if get_json() fails
        try:
            data = json.loads(request.data.decode('utf-8'))
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid JSON payload"}), 400

    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Create new competition with the provided data
    try:
        new_competition = Competition(
            title=data['title'],
            description=data['description'],
            admin_id=user_id,
            start_date=datetime.datetime.strptime(data['start_date'], '%Y-%m-%d').date(),
            end_date=datetime.datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        )

        # Save the new competition to the database
        db.session.add(new_competition)
        db.session.commit()

        return jsonify({
            "competition_id": new_competition.id,
            "message": "Competition created successfully"
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@competition_routes.route('/competitions', methods=['GET'])
def get_active_competitions():
    competitions = Competition.query.all()
    result = [{
        "competition_id": comp.id,
        "title": comp.title,
        "description": comp.description,
        "start_date": comp.start_date.isoformat() if comp.start_date else None,
        "end_date": comp.end_date.isoformat() if comp.end_date else None
    } for comp in competitions]
    return jsonify(result), 200

@competition_routes.route('/competitions/<id>', methods=['GET'])
def get_competition_details(id):
    competition = Competition.query.get(id)
    if competition:
        submissions = Submission.query.filter_by(competition_id=id).all()
        submission_details = [{
            "submission_id": sub.id,
            "title": sub.title,
            "content": sub.content,
            "created_at": sub.created_at,
            "user_id": sub.user_id,
            "likes_count": Like.query.filter_by(submission_id=sub.id).count(),
            "comments_count": Comment.query.filter_by(submission_id=sub.id).count()
        } for sub in submissions]

        return jsonify({
            "competition_id": competition.id,
            "title": competition.title,
            "description": competition.description,
            "start_date": competition.start_date.isoformat() if competition.start_date else None,
            "end_date": competition.end_date.isoformat() if competition.end_date else None,
            "created_at": competition.created_at,
            "submissions": submission_details
        }), 200
    return jsonify({"error": "Competition not found"}), 404


@competition_routes.route('/competitions/<id>/submit', methods=['POST'])
@jwt_required()
def submit_entry(id):
    user_id = get_jwt_identity()
    try:
        data = request.get_json()
    except:
        data = json.loads(request.data.decode('utf-8'))

    new_submission = Submission(title=data['title'], content=data['content'], competition_id=id, user_id=user_id)
    try:
        db.session.add(new_submission)
        db.session.commit()

        # Notify subscribers via WebSocket server
        async def notify_websocket():
            async with websockets.connect("ws://websocket:6789") as websocket:
                await websocket.send(json.dumps({
                    "action": "new_submission",
                    "competition_id": id,
                    "submission": {
                        "submission_id": new_submission.id,
                        "title": new_submission.title,
                        "content": new_submission.content,
                        "user_id": user_id,
                        "timestamp": str(datetime.datetime.utcnow())
                    }
                }))

        asyncio.run(notify_websocket())

        return jsonify({"submission_id": new_submission.id, "message": "Submission successful"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@competition_routes.route('/competitions/<id>/like/<submission_id>', methods=['POST'])
@jwt_required()
def like_submission(id, submission_id):
    user_id = get_jwt_identity()
    new_like = Like(user_id=user_id, submission_id=submission_id)
    try:
        db.session.add(new_like)
        db.session.commit()

        return jsonify({"message": "Like added"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@competition_routes.route('/competitions/<id>/comment/<submission_id>', methods=['POST'])
@jwt_required()
def comment_on_submission(id, submission_id):
    user_id = get_jwt_identity()
    try:
        data = request.get_json()
    except:
        data = json.loads(request.data.decode('utf-8'))
    new_comment = Comment(content=data['content'], user_id=user_id, submission_id=submission_id)
    try:
        db.session.add(new_comment)
        db.session.commit()

        return jsonify({"comment_id": new_comment.id, "message": "Comment added"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@competition_routes.route('/competitions/<id>', methods=['DELETE'])
@jwt_required()
def delete_competition(id):
    competition = Competition.query.get(id)
    if not competition:
        return jsonify({"error": "Competition not found"}), 404

    try:
        db.session.delete(competition)
        db.session.commit()
        return jsonify({"message": "Competition deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@competition_routes.route('/submissions/<submission_id>', methods=['DELETE'])
@jwt_required()
def delete_submission(submission_id):
    submission = Submission.query.get(submission_id)
    if not submission:
        return jsonify({"error": "Submission not found"}), 404

    try:
        db.session.delete(submission)
        db.session.commit()
        return jsonify({"message": "Submission deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@competition_routes.route('/submissions/<id>', methods=['GET'])
def get_submission(id):
    submission = Submission.query.get(id)
    if submission:
        like_count = Like.query.filter_by(submission_id=id).count()
        comment_count = Comment.query.filter_by(submission_id=id).count()
        return jsonify({
            "submission_id": submission.id,
            "title": submission.title,
            "content": submission.content,
            "created_at": submission.created_at,
            "competition_id": submission.competition_id,
            "user_id": submission.user_id,
            "likes": like_count,
            "comments": comment_count
        }), 200
    return jsonify({"error": "Submission not found"}), 404