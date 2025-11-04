from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
import re

class SentimentAnalyzer:
    """Sentiment analysis using VADER and TextBlob"""
    
    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()
        
        # Mental health specific keywords
        self.negative_keywords = [
            'sad', 'depressed', 'anxious', 'worried', 'stressed', 
            'lonely', 'hopeless', 'tired', 'exhausted', 'scared',
            'afraid', 'angry', 'frustrated', 'overwhelmed', 'hurt',
            'pain', 'suffering', 'crying', 'miserable', 'terrible'
        ]
        
        self.positive_keywords = [
            'happy', 'good', 'great', 'better', 'wonderful',
            'excited', 'joyful', 'grateful', 'thankful', 'blessed',
            'peaceful', 'calm', 'relaxed', 'content', 'satisfied'
        ]
    
    def analyze_emotion(self, text):
        """
        Analyze emotion in text using combined approach
        Returns: dict with emotion, intensity, and subjectivity
        """
        if not text or not text.strip():
            return {
                'emotion': 'neutral',
                'intensity': 0.0,
                'subjectivity': 0.0
            }
        
        # Clean text
        text = text.lower().strip()
        
        # VADER analysis
        vader_scores = self.vader.polarity_scores(text)
        vader_compound = vader_scores['compound']
        
        # TextBlob analysis
        try:
            blob = TextBlob(text)
            textblob_polarity = blob.sentiment.polarity
            textblob_subjectivity = blob.sentiment.subjectivity
        except:
            textblob_polarity = 0.0
            textblob_subjectivity = 0.5
        
        # Check for mental health specific keywords
        keyword_boost = self._check_keywords(text)
        
        # Combined score with keyword adjustment
        combined_score = (vader_compound + textblob_polarity) / 2
        combined_score += keyword_boost
        
        # Determine emotion state
        emotion_state = self._determine_emotion(combined_score)
        
        return {
            'emotion': emotion_state,
            'intensity': round(combined_score, 2),
            'subjectivity': round(textblob_subjectivity, 2),
            'vader_score': vader_compound,
            'textblob_score': textblob_polarity
        }
    
    def _check_keywords(self, text):
        """Check for mental health specific keywords and adjust score"""
        boost = 0.0
        
        # Check negative keywords
        negative_count = sum(1 for keyword in self.negative_keywords if keyword in text)
        if negative_count > 0:
            boost -= 0.1 * negative_count
        
        # Check positive keywords
        positive_count = sum(1 for keyword in self.positive_keywords if keyword in text)
        if positive_count > 0:
            boost += 0.1 * positive_count
        
        # Cap the boost
        return max(-0.3, min(0.3, boost))
    
    def _determine_emotion(self, score):
        """Determine emotion category from score"""
        if score <= -0.3:
            return 'negative'
        elif score >= 0.3:
            return 'positive'
        else:
            return 'neutral'
    
    def get_emotion_label(self, emotion, intensity):
        """Get detailed emotion label"""
        if emotion == 'negative':
            if intensity <= -0.6:
                return 'very_sad'
            elif intensity <= -0.3:
                return 'sad'
            else:
                return 'slightly_sad'
        elif emotion == 'positive':
            if intensity >= 0.6:
                return 'very_happy'
            elif intensity >= 0.3:
                return 'happy'
            else:
                return 'slightly_happy'
        else:
            return 'neutral'
