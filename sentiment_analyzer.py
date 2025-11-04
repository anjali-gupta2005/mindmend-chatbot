from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import numpy as np
import re


class SentimentAnalyzer:
    """Sentiment analysis using VADER, TextBlob, and Scikit-learn"""
    
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
        
        # ===== ADD: Scikit-learn for advanced analysis =====
        # Training data for emotion classification
        self.training_texts = [
            # Positive
            "I'm so happy and excited!", "This is wonderful!", "I love this!",
            "I'm feeling great!", "Everything is amazing!",
            # Negative
            "I'm feeling down", "Everything is terrible", "I'm so sad",
            "I don't know what to do", "I feel empty",
            # Anxious
            "I'm very anxious", "I feel nervous", "I can't stop worrying",
            "I'm panicking", "Everything feels overwhelming"
        ]
        
        self.training_labels = [
            1, 1, 1, 1, 1,  # Positive = 1
            0, 0, 0, 0, 0,  # Negative = 0
            2, 2, 2, 2, 2   # Anxious = 2
        ]
        
        # Train scikit-learn classifier
        self.vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
        self.X_train = self.vectorizer.fit_transform(self.training_texts)
        self.classifier = MultinomialNB()
        self.classifier.fit(self.X_train, self.training_labels)
        
        # Emotion mapping for scikit-learn
        self.emotion_map = {0: 'negative', 1: 'positive', 2: 'anxious'}
        # ===== END: Scikit-learn setup =====
    
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
        
        # ===== ADD: Scikit-learn prediction =====
        try:
            text_vectorized = self.vectorizer.transform([text])
            sklearn_pred = self.classifier.predict(text_vectorized)[0]
            sklearn_emotion = self.emotion_map.get(sklearn_pred, 'neutral')
            sklearn_confidence = self.classifier.predict_proba(text_vectorized)[0].max()
        except:
            sklearn_emotion = 'neutral'
            sklearn_confidence = 0.5
        
        # Combine scikit-learn with other methods
        # If scikit-learn is very confident, use it
        if sklearn_confidence > 0.7:
            if sklearn_emotion == 'anxious':
                emotion_state = 'anxious'
            else:
                emotion_state = self._determine_emotion(combined_score)
        else:
            emotion_state = self._determine_emotion(combined_score)
        # ===== END: Scikit-learn prediction =====
        
        # Determine emotion state
        # emotion_state = self._determine_emotion(combined_score)  # Original line still works
        
        return {
            'emotion': emotion_state,
            'intensity': round(combined_score, 2),
            'subjectivity': round(textblob_subjectivity, 2),
            'vader_score': vader_compound,
            'textblob_score': textblob_polarity,
            'sklearn_emotion': sklearn_emotion,  # ADD: Include ML prediction
            'sklearn_confidence': round(sklearn_confidence, 2)  # ADD: Include confidence
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
