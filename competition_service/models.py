from app import db
import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class Competition(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    title = db.Column(String(255), nullable=False)
    description = db.Column(Text, nullable=False)
    admin_id = db.Column(String(36), nullable=False)
    start_date = db.Column(Date, nullable=False)
    end_date = db.Column(Date, nullable=False)
    created_at = db.Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Competition {self.title}>"


class Submission(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    title = db.Column(String(255), nullable=False)
    content = db.Column(Text, nullable=False)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    competition_id = db.Column(Integer, ForeignKey('competition.id'), nullable=False)
    user_id = db.Column(String(36), nullable=False)

    def __repr__(self):
        return f"<Submission {self.title}>"

class Like(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    user_id = db.Column(String(36), nullable=False)
    submission_id = db.Column(Integer, ForeignKey('submission.id'), nullable=False)
    created_at = db.Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Like by {self.user_id} on {self.submission_id}>"


class Comment(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    content = db.Column(Text, nullable=False)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    user_id = db.Column(String(36), nullable=False)
    submission_id = db.Column(Integer, ForeignKey('submission.id'), nullable=False)
    parent_comment_id = db.Column(Integer, ForeignKey('comment.id'), nullable=True)

    def __repr__(self):
        return f"<Comment by {self.user_id} on {self.submission_id}>"