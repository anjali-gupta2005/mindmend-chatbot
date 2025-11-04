import os
import nltk

# Set NLTK data path for Render
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


from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import secrets
import os
from sentiment_analyzer import SentimentAnalyzer
from dialogue_manager import DialogueManager
from resource_recommender import ResourceRecommender
from models import db, ConversationLog, UserSession


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


# Create tables
with app.app_context():
    db.create_all()


@app.route('/')
def index():
    """Render main chat interface"""
    return render_template('index.html')


@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages with resource recommendations"""
    try:
        data = request.json
        user_input = data.get('message', '').strip()
        
        if not user_input:
            return jsonify({'error': 'Empty message'}), 400
        
        # Get or create user session
        if 'user_id' not in session:
            session['user_id'] = secrets.token_hex(8)
        
        user_id = session['user_id']
        
        # Analyze sentiment
        sentiment_data = sentiment_analyzer.analyze_emotion(user_input)
        
        # Check for crisis situation first
        if dialogue_manager.detect_crisis(user_input):
            crisis_response = dialogue_manager.crisis_response()
            log_conversation(user_id, user_input, 'crisis', crisis_response['message'])
            return jsonify({
                'message': crisis_response['message'],
                'sentiment': 'negative',
                'is_crisis': True,
                'emergency_resources': crisis_response['emergency_resources'],
                'show_resources': False
            })
        
        # Manage dialogue and get response
        bot_response = dialogue_manager.manage_conversation(
            user_id,
            user_input,
            sentiment_data
        )
        
        # DEBUG: Print response details
        print(f"DEBUG - Bot response type: {type(bot_response)}")
        print(f"DEBUG - Bot response: {bot_response}")
        
        # Check if resources should be provided
        if isinstance(bot_response, dict) and bot_response.get('trigger_resources'):
            # Get resources based on emotion
            mood_preference = data.get('mood_preference')  # Optional
            resources = resource_recommender.recommend_resources(
                bot_response['emotion'],
                mood_preference
            )
            
            # Log conversation
            log_conversation(
                user_id,
                user_input[:100],
                sentiment_data['emotion'],
                bot_response['text'][:200]
            )
            
            return jsonify({
                'message': bot_response['text'],
                'resources': resources,
                'sentiment': sentiment_data['emotion'],
                'intensity': sentiment_data['intensity'],
                'show_resources': True
            })
        
        # Simple text response (no resources)
        response_text = bot_response if isinstance(bot_response, str) else bot_response.get('text', str(bot_response))
        
        # Log conversation
        log_conversation(
            user_id,
            user_input[:100],
            sentiment_data['emotion'],
            response_text[:200]
        )
        
        return jsonify({
            'message': response_text,
            'sentiment': sentiment_data['emotion'],
            'intensity': sentiment_data['intensity'],
            'show_resources': False
        })
    
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'message': 'Sorry, I encountered an error. Please try again.',
            'sentiment': 'neutral',
            'show_resources': False
        }), 500


@app.route('/api/resources', methods=['POST'])
def get_resources():
    """Get resources based on emotion and preference"""
    try:
        data = request.json
        emotion = data.get('emotion', 'negative')
        mood_preference = data.get('mood_preference')
        
        resources = resource_recommender.recommend_resources(emotion, mood_preference)
        return jsonify(resources)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/reset', methods=['POST'])
def reset_session():
    """Reset conversation session"""
    if 'user_id' in session:
        user_id = session['user_id']
        dialogue_manager.reset_session(user_id)
    session.clear()
    return jsonify({'message': 'Session reset successfully'})


def log_conversation(user_id, message, sentiment, bot_response):
    """Log conversation to database (anonymized)"""
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
        print(f"Logging error: {str(e)}")
        db.session.rollback()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)