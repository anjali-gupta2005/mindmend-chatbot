from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


def get_ist_time():
   
    utc_now = datetime.utcnow()
    ist_offset = timedelta(hours=5, minutes=30)
    ist_time = utc_now + ist_offset
    return ist_time


class User(db.Model):
    """User account model"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=get_ist_time)  
    last_login = db.Column(db.DateTime)
    
    # Relationships
    conversations = db.relationship('Conversation', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if password matches"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_admin': self.is_admin,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,  
            'last_login': self.last_login.strftime('%Y-%m-%d %H:%M:%S') if self.last_login else None
        }


class Conversation(db.Model):
    """Conversation history for each user"""
    __tablename__ = 'conversations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(200), default='New Conversation')
    created_at = db.Column(db.DateTime, default=get_ist_time, index=True)  
    updated_at = db.Column(db.DateTime, default=get_ist_time, onupdate=get_ist_time)  
    
    # Relationships
    messages = db.relationship('Message', backref='conversation', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        message_count = len(self.messages)
        last_message = self.messages[-1] if self.messages else None
        
        return {
            'id': self.id,
            'title': self.title,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,  
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None,  
            'message_count': message_count,
            'preview': last_message.content[:50] + '...' if last_message and len(last_message.content) > 50 else (last_message.content if last_message else '')
        }


class Message(db.Model):
    """Individual messages in conversations"""
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False, index=True)
    sender = db.Column(db.String(10), nullable=False) 
    content = db.Column(db.Text, nullable=False)
    sentiment = db.Column(db.String(20))
    timestamp = db.Column(db.DateTime, default=get_ist_time, index=True)  
    
    def to_dict(self):
        return {
            'id': self.id,
            'sender': self.sender,
            'content': self.content,
            'sentiment': self.sentiment,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S') if self.timestamp else None  
        }


class ConversationLog(db.Model):
    """conversation log """
    __tablename__ = 'conversation_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), index=True)
    message = db.Column(db.Text)
    sentiment = db.Column(db.String(50))
    bot_response = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=get_ist_time, index=True)  
    
    def __repr__(self):
        return f'<ConversationLog {self.id}: {self.sentiment}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'sentiment': self.sentiment,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None  
        }


class UserSession(db.Model):
    """User session tracking"""
    __tablename__ = 'user_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), unique=True, nullable=False)
    session_start = db.Column(db.DateTime, default=get_ist_time)  
    last_activity = db.Column(db.DateTime, default=get_ist_time)  
    message_count = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<UserSession {self.user_id}>'
