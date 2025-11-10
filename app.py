import os
import nltk
from functools import wraps

# Set NLTK data path
os.environ['NLTK_DATA'] = '/tmp/nltk_data'

# Download required NLTK models on startup
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    print("Downloading NLTK punkt...")
    nltk.download('punkt')

try:
    nltk.data.find('sentiment/vader_lexicon')
except LookupError:
    print("Downloading NLTK vader_lexicon...")
    nltk.download('vader_lexicon')

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import secrets

from sentiment_analyzer import SentimentAnalyzer
from dialogue_manager import DialogueManager
from resource_recommender import ResourceRecommender
from models import db, User, Conversation, Message, ConversationLog, UserSession, get_ist_time  # ✅ Added get_ist_time

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mindmend.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CORS(app)

# Initialize database
db.init_app(app)

# Initialize components
sentiment_analyzer = SentimentAnalyzer()
dialogue_manager = DialogueManager()
resource_recommender = ResourceRecommender()

with app.app_context():
    db.create_all()
    
    # Create default admin 
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@mindmend.com',
            is_admin=True
        )
        admin.set_password('anj@123')  
        db.session.add(admin)
        db.session.commit()
       

# ============= DECORATORS =============

def login_required(f):
    """Require user to be logged in"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Require user to be admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

# ============= AUTHENTICATION ROUTES =============

@app.route('/')
def index():
    """Redirect to login or chat based on session"""
    if 'user_id' in session:
        return redirect(url_for('chat_page'))
    return redirect(url_for('login'))

@app.route('/login')
def login():
    """Login page"""
    if 'user_id' in session:
        return redirect(url_for('chat_page'))
    return render_template('login.html')

@app.route('/signup')
def signup():
    """Signup page"""
    if 'user_id' in session:
        return redirect(url_for('chat_page'))
    return render_template('signup.html')

@app.route('/api/auth/signup', methods=['POST'])
def api_signup():
    """Handle user registration"""
    try:
        data = request.json
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        # Validation
        if not username or not email or not password:
            return jsonify({'error': 'All fields are required'}), 400
        
        if len(username) < 3:
            return jsonify({'error': 'Username must be at least 3 characters'}), 400
        
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        print(f"✅ New user registered: {username}")
        
        return jsonify({
            'message': 'Account created successfully!',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Signup error: {str(e)}")
        return jsonify({'error': 'Registration failed. Please try again.'}), 500

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    """Handle user login"""
    try:
        data = request.json
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        # Find user
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid username or password'}), 401
        
        # Update last login - ✅ Changed to IST
        user.last_login = get_ist_time()
        db.session.commit()
        
        # Set session
        session['user_id'] = user.id
        session['username'] = user.username
        session['is_admin'] = user.is_admin
        
      
        
        return jsonify({
            'message': 'Login successful!',
            'user': user.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': 'Login failed. Please try again.'}), 500

@app.route('/api/auth/logout', methods=['POST'])
def api_logout():
    """Handle user logout"""
    username = session.get('username', 'Unknown')
    session.clear()
    print(f"✅ User logged out: {username}")
    return jsonify({'message': 'Logged out successfully'})

# ============= CHAT ROUTES =============

@app.route('/chat')
@login_required
def chat_page():
    """Main chat interface"""
    user = User.query.get(session['user_id'])
    return render_template('chat.html', user=user)

@app.route('/api/chat', methods=['POST'])
@login_required
def chat():
    """Handle chat messages"""
    try:
        data = request.json
        user_input = data.get('message', '').strip()
        conversation_id = data.get('conversation_id')
        
        if not user_input:
            return jsonify({'error': 'Empty message'}), 400
        
        user_id = session['user_id']
        
        if conversation_id:
            conversation = Conversation.query.get(conversation_id)
            if not conversation or conversation.user_id != user_id:
                return jsonify({'error': 'Invalid conversation'}), 403
        else:
            # Create new conversation
            title = user_input[:50] + '...' if len(user_input) > 50 else user_input
            conversation = Conversation(user_id=user_id, title=title)
            db.session.add(conversation)
            db.session.commit()
        
        # Analyze sentiment
        sentiment_data = sentiment_analyzer.analyze_emotion(user_input)
        
        # Check for crisis
        if dialogue_manager.detect_crisis(user_input):
            crisis_response = dialogue_manager.crisis_response()
            
            # Save messages
            save_message(conversation.id, 'user', user_input, sentiment_data['emotion'])
            save_message(conversation.id, 'bot', crisis_response['message'], 'crisis')
            
            # Legacy logging
            log_conversation(str(user_id), user_input, 'crisis', crisis_response['message'])
            
            return jsonify({
                'message': crisis_response['message'],
                'sentiment': 'negative',
                'is_crisis': True,
                'emergency_resources': crisis_response['emergency_resources'],
                'conversation_id': conversation.id,
                'show_resources': False
            })
        
        # Get bot response
        bot_response = dialogue_manager.manage_conversation(
            str(user_id),
            user_input,
            sentiment_data
        )
        
        # Save user message
        save_message(conversation.id, 'user', user_input, sentiment_data['emotion'])
        
        # Handle resource response
        if isinstance(bot_response, dict) and bot_response.get('trigger_resources'):
            resources = resource_recommender.recommend_resources(
                bot_response['emotion'],
                data.get('mood_preference')
            )
            
            # Save bot message
            save_message(conversation.id, 'bot', bot_response['text'], sentiment_data['emotion'])
            
            # Legacy logging
            log_conversation(str(user_id), user_input[:100], sentiment_data['emotion'], bot_response['text'][:200])
            
            return jsonify({
                'message': bot_response['text'],
                'resources': resources,
                'sentiment': sentiment_data['emotion'],
                'intensity': sentiment_data['intensity'],
                'show_resources': True,
                'conversation_id': conversation.id
            })
        
        # Simple text response
        response_text = bot_response if isinstance(bot_response, str) else bot_response.get('text', str(bot_response))
        
        # Save bot message
        save_message(conversation.id, 'bot', response_text, sentiment_data['emotion'])
        
        # Legacy logging
        log_conversation(str(user_id), user_input[:100], sentiment_data['emotion'], response_text[:200])
        
        return jsonify({
            'message': response_text,
            'sentiment': sentiment_data['emotion'],
            'intensity': sentiment_data['intensity'],
            'show_resources': False,
            'conversation_id': conversation.id
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'message': 'Sorry, I encountered an error. Please try again.',
            'sentiment': 'neutral',
            'show_resources': False
        }), 500

@app.route('/api/conversations', methods=['GET'])
@login_required
def get_conversations():
    """Get user's conversation history"""
    user_id = session['user_id']
    conversations = Conversation.query.filter_by(user_id=user_id)\
        .order_by(Conversation.updated_at.desc()).all()
    
    return jsonify({
        'conversations': [conv.to_dict() for conv in conversations]
    })

@app.route('/api/conversations/<int:conversation_id>', methods=['GET'])
@login_required
def get_conversation(conversation_id):
    """Get specific conversation with messages"""
    conversation = Conversation.query.get_or_404(conversation_id)
    
    # Check ownership (allow admin to view any conversation)
    current_user = User.query.get(session['user_id'])
    if conversation.user_id != session['user_id'] and not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    messages = Message.query.filter_by(conversation_id=conversation_id)\
        .order_by(Message.timestamp.asc()).all()
    
    return jsonify({
        'conversation': conversation.to_dict(),
        'messages': [msg.to_dict() for msg in messages]
    })

@app.route('/api/conversations/<int:conversation_id>', methods=['DELETE'])
@login_required
def delete_conversation(conversation_id):
    """Delete a conversation"""
    conversation = Conversation.query.get_or_404(conversation_id)
    
    # Check ownership (allow admin to delete any conversation)
    current_user = User.query.get(session['user_id'])
    if conversation.user_id != session['user_id'] and not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(conversation)
    db.session.commit()
    
    print(f"✅ Conversation deleted: {conversation_id}")
    
    return jsonify({'message': 'Conversation deleted'})

@app.route('/api/reset', methods=['POST'])
@login_required
def reset_session():
    """Reset conversation session (legacy support)"""
    user_id = session.get('user_id')
    if user_id:
        dialogue_manager.reset_session(str(user_id))
    return jsonify({'message': 'Session reset successfully'})

# ============= ADMIN ROUTES =============

@app.route('/admin')
@admin_required
def admin_panel():
    """Admin dashboard"""
    return render_template('admin.html')

@app.route('/api/admin/users', methods=['GET'])
@admin_required
def get_all_users():
    """Get all users (admin only)"""
    users = User.query.all()
    return jsonify({
        'users': [user.to_dict() for user in users],
        'total': len(users)
    })

@app.route('/api/admin/conversations', methods=['GET'])
@admin_required
def get_all_conversations():
    """Get all conversations (admin only)"""
    conversations = Conversation.query.join(User).all()
    
    data = []
    for conv in conversations:
        conv_dict = conv.to_dict()
        conv_dict['username'] = conv.user.username
        conv_dict['user_email'] = conv.user.email
        data.append(conv_dict)
    
    return jsonify({
        'conversations': data,
        'total': len(data)
    })

@app.route('/api/admin/stats', methods=['GET'])
@admin_required
def get_admin_stats():
    """Get system statistics (admin only)"""
    total_users = User.query.count()
    total_conversations = Conversation.query.count()
    total_messages = Message.query.count()
    
    # Recent activity
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_conversations = Conversation.query.order_by(Conversation.updated_at.desc()).limit(10).all()
    
    return jsonify({
        'stats': {
            'total_users': total_users,
            'total_conversations': total_conversations,
            'total_messages': total_messages,
        },
        'recent_users': [u.to_dict() for u in recent_users],
        'recent_conversations': [c.to_dict() for c in recent_conversations]
    })

# ============= UTILITY FUNCTIONS =============

def save_message(conversation_id, sender, content, sentiment=None):
    """Save message to database"""
    try:
        message = Message(
            conversation_id=conversation_id,
            sender=sender,
            content=content,
            sentiment=sentiment
        )
        db.session.add(message)
        
        
        conversation = Conversation.query.get(conversation_id)
        if conversation:
            conversation.updated_at = get_ist_time()
        
        db.session.commit()
    except Exception as e:
       
        db.session.rollback()

def log_conversation(user_id, message, sentiment, bot_response):
    """Log conversation """
    try:
        log = ConversationLog(
            user_id=user_id,
            message=message,
            sentiment=sentiment,
            bot_response=bot_response[:200] if bot_response else ''
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
       
        db.session.rollback()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
