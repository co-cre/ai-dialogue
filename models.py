from app import db
from datetime import datetime

class Dialogue(db.Model):
    __tablename__ = 'dialogue'

    id = db.Column(db.Integer, primary_key=True)
    theme = db.Column(db.String(200), nullable=False)
    persona_a_name = db.Column(db.String(100), nullable=False)
    persona_b_name = db.Column(db.String(100), nullable=False)
    persona_a_description = db.Column(db.Text, nullable=False)
    persona_b_description = db.Column(db.Text, nullable=False)
    started_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    messages = db.relationship('Message', backref='dialogue', lazy=True, cascade='all, delete-orphan')

class Message(db.Model):
    __tablename__ = 'message'

    id = db.Column(db.Integer, primary_key=True)
    dialogue_id = db.Column(db.Integer, db.ForeignKey('dialogue.id', ondelete='CASCADE'), nullable=False)
    speaker = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)