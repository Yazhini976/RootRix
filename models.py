from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="participant")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    submissions = db.relationship("Submission", backref="user", lazy=True)


class Challenge(db.Model):
    __tablename__ = "challenges"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    resource_type = db.Column(db.String(20), nullable=True)  # 'link' or 'file'
    resource_path = db.Column(db.String(500), nullable=True)
    correct_flag = db.Column(db.String(500), nullable=False)
    points = db.Column(db.Integer, nullable=False, default=100)
    is_published = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    submissions = db.relationship("Submission", backref="challenge", lazy=True)

    def solved_count(self):
        return Submission.query.filter_by(challenge_id=self.id, is_correct=True).count()

    def to_dict(self, include_flag=False):
        data = {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "description": self.description,
            "resource_type": self.resource_type,
            "resource_path": self.resource_path,
            "points": self.points,
            "is_published": self.is_published,
            "solved_count": self.solved_count(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if include_flag:
            data["correct_flag"] = self.correct_flag
        return data


class Submission(db.Model):
    __tablename__ = "submissions"
    __table_args__ = (db.UniqueConstraint("user_id", "challenge_id", name="uq_user_challenge"),)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey("challenges.id"), nullable=False)
    submitted_flag = db.Column(db.String(500), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False, default=False)
    earned_points = db.Column(db.Integer, nullable=False, default=0)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.user.username if self.user else None,
            "challenge_id": self.challenge_id,
            "challenge_title": self.challenge.title if self.challenge else None,
            "submitted_flag": self.submitted_flag,
            "is_correct": self.is_correct,
            "earned_points": self.earned_points,
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
        }
