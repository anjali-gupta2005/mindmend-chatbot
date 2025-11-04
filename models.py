from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class ConversationLog(db.Model):
    """Store anonymized conversation logs"""
    __tablename__ = 'conversation_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=False, index=True)
    message = db.Column(db.Text, nullable=False)  # Truncated user message
    sentiment = db.Column(db.String(50))
    bot_response = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<ConversationLog {self.id}: {self.sentiment}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'sentiment': self.sentiment,
            'timestamp': self.timestamp.isoformat()
        }

class UserSession(db.Model):
    """Track user sessions"""
    __tablename__ = 'user_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), unique=True, nullable=False)
    session_start = db.Column(db.DateTime, default=datetime.utcnow)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    message_count = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<UserSession {self.user_id}>'
