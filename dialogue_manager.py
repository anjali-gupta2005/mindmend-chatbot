import random
import re
from datetime import datetime
import spacy  # ===== ADD: Spacy for NLP =====


class DialogueManager:
    """Ultra-comprehensive dialogue manager that handles EVERY possible user scenario"""
    
    def __init__(self):
        # ===== ADD: Spacy NLP setup =====
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            print("Warning: Spacy model not found. Run: python -m spacy download en_core_web_sm")
            self.nlp = None
        # ===== END: Spacy setup =====
        
        self.sessions = {}
        
        # Expanded intent patterns covering ALL scenarios
        self.intent_patterns = {
            # Greetings
            'greeting': r'\b(hello|hi|hey|hii|hiii|hy|hyy|hola|namaste|good morning|good afternoon|good evening|greetings|whats up|sup|yo)\b',
            
            # Emotional states - NEGATIVE
            'feeling_sad': r'\b(sad|sadness|feeling sad|feel sad|im sad|i am sad)\b',
            'feeling_depressed': r'\b(depressed|depression|feeling depressed|feel depressed)\b',
            'feeling_anxious': r'\b(anxious|anxiety|worried|worry|nervous|panic|scared|afraid|fear)\b',
            'feeling_stressed': r'\b(stressed|stress|pressure|overwhelmed|overworked|burnout|burnt out)\b',
            'feeling_lonely': r'\b(lonely|alone|isolated|no one|nobody)\b',
            'feeling_angry': r'\b(angry|mad|furious|frustrated|irritated|annoyed)\b',
            'crying': r'\b(crying|cry|tears|weeping|sobbing)\b',
            'hurt': r'\b(hurt|pain|painful|hurting|wounded)\b',
            'feeling_hopeless': r'\b(hopeless|helpless|worthless|useless|pointless)\b',
            'low_mood': r'\b(low mood|feeling down|feeling low|down|low|unmotivated|no energy)\b',
            
            # Emotional states - POSITIVE
            'feeling_happy': r'\b(happy|happiness|feeling happy|feel happy|joyful|joy)\b',
            'feeling_good': r'\b(good|great|amazing|wonderful|fantastic|excellent|awesome|fine|better)\b',
            'feeling_excited': r'\b(excited|excitement|energetic|motivated|pumped)\b',
            'feeling_grateful': r'\b(grateful|thankful|blessed|appreciate)\b',
            
            # Specific problems
            'relationship_problems': r'\b(relationship|boyfriend|girlfriend|partner|spouse|husband|wife|breakup|broke up|break up|divorce|cheating|cheated|fight|fought|argument|love problem)\b',
            'family_problems': r'\b(family|parents|mother|father|mom|dad|sister|brother|sibling|family issue|family problem|family fight)\b',
            'friendship_problems': r'\b(friend|friends|friendship|best friend|friends hurt|friends ignore|friends left|friend problem)\b',
            'bullying': r'\b(bully|bullying|bullied|harass|harassment|teasing|mocking|make fun)\b',
            'work_stress': r'\b(work|job|office|workplace|boss|manager|colleague|coworker|workload|deadline|overtime|project|career)\b',
            'exam_stress': r'\b(exam|test|exams|tests|studying|study|grade|grades|marks|result|results|academic|school|college|university|assignment|homework)\b',
            'money_problems': r'\b(money|financial|finances|debt|broke|bills|salary|pay|loan|expenses|poor)\b',
            'health_problems': r'\b(health|sick|illness|disease|pain|ache|medical|doctor|hospital|unwell)\b',
            'self_esteem': r'\b(ugly|fat|stupid|dumb|worthless|useless|hate myself|self esteem|confidence|insecure|not good enough)\b',
            
            # Reasons/Explanations
            'because': r'\b(because|cause|reason|due to|since|as)\b',
            'someone_hurt': r'\b(hurt me|hurting me|betrayed|betray|let me down|disappointed|ignore|ignored|left me|abandoned)\b',
            'failure': r'\b(fail|failed|failure|mess|messed up|mistake|screwed up|lost)\b',
            'rejection': r'\b(reject|rejected|rejection|turned down|said no|denied)\b',
            'loss': r'\b(lost|loss|death|died|passed away|gone|miss)\b',
            
            # Responses
            'thanks': r'\b(thank|thanks|thx|thankyou|thank you|appreciate|grateful)\b',
            'yes': r'\b(yes|yeah|yep|yup|sure|okay|ok|fine|alright)\b',
            'no': r'\b(no|nope|nah|not really)\b',
            'help': r'\b(help|support|advice|suggest|recommend|what should|what can|guide)\b',
            'goodbye': r'\b(bye|goodbye|see you|gtg|gotta go|have to go|talk later|later)\b',
        }
        
        self.crisis_keywords = [
            'suicide', 'kill myself', 'end my life', 'want to die', 'wanna die',
            'hurt myself', 'harm myself', 'end it all', 'better off dead', 'not worth living'
        ]
        
        # COMPREHENSIVE RESPONSES for EVERY scenario
        self.responses = {
            'greeting_first': [
                "Hello! I'm MindMend, your mental health support companion. I'm here to listen to you without any judgment. How are you feeling today? 😊",
                "Hi there! I'm so glad you're here. I'm MindMend, and I'm here to support you through whatever you're going through. What's on your mind today? 💙",
                "Hey! Welcome to MindMend. This is a safe space for you to share anything. How are you doing right now? 🤗"
            ],
            
            'greeting_response': [
                "Hello again! I'm here for you. How can I support you today? 😊",
                "Hi! Good to hear from you again. What would you like to talk about? 💬",
                "Hey! I'm all ears. What's going on with you? 🌟"
            ],
            
            # SAD responses
            'sad_initial': [
                "I'm really sorry you're feeling sad right now. 😢 Your feelings are completely valid. Can you tell me what's making you feel this way? I'm here to listen.",
                "I hear you, and I'm here for you. Feeling sad is tough, and I want you to know you're not alone. What's been going on that's making you feel sad? 💙",
                "Thank you for sharing that with me. It takes courage to express when you're feeling down. Would you like to tell me what's causing these feelings? I'm listening. 🤗"
            ],
            
            # RELATIONSHIP PROBLEMS
            'sad_because_relationship': [
                "I'm so sorry you're going through relationship problems. 💔 Heartbreak and relationship conflicts are incredibly painful. Your feelings are completely valid. Remember, you deserve to be treated with love, respect, and kindness. Let me share some resources that can help you through this difficult time.",
                "Relationship pain is one of the deepest hurts we can experience. 😢 Whether it's a breakup, betrayal, or ongoing conflicts, these wounds take time to heal. You're not alone in this. I'm here to support you with helpful resources."
            ],
            
            # FAMILY PROBLEMS
            'sad_because_family': [
                "I'm sorry you're dealing with family problems. 👨‍👩‍👧 Family conflicts can be especially difficult. Your feelings are valid, and it's okay to feel hurt or frustrated. Remember, you can take care of yourself. Let me share some coping strategies and resources.",
                "Family problems are incredibly challenging. 😔 Whether it's conflicts with parents or siblings, these situations can feel overwhelming. You deserve peace. I have resources that can help you navigate this."
            ],
            
            # FRIENDSHIP PROBLEMS
            'sad_because_friends': [
                "I'm so sorry your friends hurt you. 💔 Friendship problems can feel devastating. Being ignored or hurt by friends can shake our confidence. Please know that you deserve friends who value and respect you. Let me share some resources to help you cope.",
                "That's really hard. 😢 When our friends let us down, it can make us feel so alone. Remember, you are worthy of genuine, caring friendships. Let me provide you with some helpful resources and coping strategies."
            ],
            
            # BULLYING
            'sad_because_bullying': [
                "I'm so sorry you're being bullied. 😔 Bullying is NOT okay, and it's NOT your fault. No one deserves to be treated that way. Please consider talking to a trusted adult, teacher, or counselor. Let me also share resources that can help you cope and protect yourself.",
                "Bullying is a form of abuse, and I want you to know that you don't deserve this treatment. 💙 You are valuable and worthy of respect. Please reach out to someone you trust. I'm also going to provide you with coping strategies and support resources."
            ],
            
            # EXAM STRESS
            'sad_because_exam': [
                "Exam pressure can be incredibly stressful. 📚 Remember, your worth isn't defined by your grades. You're so much more than a test score! Let me help you with some stress-relief techniques, study tips, and motivational resources.",
                "I hear you. Academic pressure is real. 😟 Many students go through this. Let me help you with some stress-relief techniques, study tips, and calming exercises that can make things feel more manageable."
            ],
            
            # WORK STRESS
            'sad_because_work': [
                "Work stress and office pressure can be exhausting. 😓 It's okay to feel overwhelmed. Your wellbeing matters more than any deadline. Let me share some stress management resources and quick relaxation techniques.",
                "I'm sorry you're dealing with work overload. Burnout is real. 💼 Remember to take breaks and be kind to yourself. Let me share some stress management resources, funny videos, and relaxation exercises."
            ],
            
            # MONEY PROBLEMS
            'sad_because_money': [
                "Financial stress is incredibly challenging. 💰 Please know that your worth isn't determined by your bank account. Many people face financial difficulties. Let me share resources including stress-management techniques and support information.",
                "I'm sorry you're dealing with financial stress. 😔 Money problems can cause enormous anxiety. You're not alone in this. Let me provide coping strategies and helpful resources."
            ],
            
            # HEALTH PROBLEMS
            'sad_because_health': [
                "I'm sorry you're dealing with health issues. 🏥 Physical illness can deeply affect our mental health too. Please make sure you're seeing medical professionals. Let me also share mental health resources to support you through this difficult time.",
                "Health problems are so challenging. 😔 Dealing with illness or pain is exhausting. While I can't provide medical advice, I can offer mental health support resources to help you cope emotionally."
            ],
            
            # SELF-ESTEEM
            'sad_because_self_esteem': [
                "I'm so sorry you're feeling this way about yourself. 💙 Please know that you ARE good enough, worthy, and valuable - exactly as you are. You deserve self-compassion. Let me share resources to help build your self-esteem.",
                "Those feelings of worthlessness are symptoms of low self-esteem, not truth. 🌟 You have inherent value. Let me help you challenge those negative thoughts with coping strategies and professional resources."
            ],
            
            # LONELINESS
            'sad_because_lonely': [
                "I'm so sorry you're feeling lonely. 😔 Loneliness is incredibly painful. You matter, and you deserve connection and companionship. Let me share resources for building social connections and coping with loneliness.",
                "Feeling alone is one of the hardest experiences. 💙 Your feelings are valid, and reaching out shows courage. Let me provide resources and strategies to help you feel less isolated."
            ],
            
            # CRYING responses
            'crying_response': [
                "I'm here with you. It's okay to cry - tears are a natural way to release emotion. 😢 Take your time. When you're ready, I'm here to listen.",
                "Crying is healing. 💙 Let it out. I'm right here with you. Would you like to share what's causing these tears?"
            ],
            
            # STRESS-SPECIFIC responses
            'stress_response': [
                "I hear that you're feeling stressed. 😰 Stress can affect everything - sleep, mood, and health. Can you tell me what's causing this stress? I have stress-relief resources that can help.",
                "Stress is your body's way of saying it's overwhelmed. 😓 What's been stressing you out? Let me provide you with stress-management techniques, breathing exercises, and calming resources."
            ],
            
            # ANXIETY-SPECIFIC responses
            'anxiety_response': [
                "I'm sorry you're experiencing anxiety. 😰 Anxiety can feel like your mind is racing. Can you tell me more about when you feel most anxious? I have anxiety-relief techniques including breathing exercises that can help immediately.",
                "Anxiety is so challenging. 💙 It can make you feel constantly worried. Please know that anxiety is treatable. I have resources specifically for managing anxious thoughts."
            ],
            
            # LOW MOOD-SPECIFIC responses
            'low_mood_response': [
                "I'm sorry you're experiencing low mood. 😔 When we feel down or unmotivated, it can be hard to see things getting better. I have resources including mood-boosting activities and uplifting videos that can help.",
                "A persistent low mood can be draining. 💙 Sometimes we just feel down without knowing why. I have resources to help lift your mood and energy."
            ],
            
            # ANXIETY/STRESS COMBO
            'anxiety_stress_combo': [
                "Anxiety and stress together can feel overwhelming. 😰 But there are ways to break this cycle. Let me provide you with breathing exercises, stress-management techniques, and calming resources that address both.",
                "Dealing with both stress and anxiety is exhausting. 💙 The good news is that many techniques help with both. I have breathing exercises, grounding techniques, and calming videos that work for stress and anxiety."
            ],
            
            # HAPPY responses
            'happy_response': [
                "That's wonderful to hear! 😊 I'm so happy you're feeling good! What's been going well for you? I'd love to celebrate this moment with you! ✨",
                "Yay! I love hearing that you're happy! 🎉 What's bringing you joy today? Tell me all about it!"
            ],
            
            'happy_because_marks': [
                "Congratulations on your good marks! 🎊 You worked hard for this! This is proof of your dedication. I'm so proud of you! 🌟",
                "That's amazing! Good grades are the result of your hard work! 📚✨ You should feel really proud! 💪"
            ],
            
            # VALIDATION phrases
            'validation': [
                "What you're feeling is completely valid and normal. You're not alone in this. 💙",
                "Your emotions matter, and acknowledging them shows strength. 🌟",
                "Thank you for trusting me. What you're going through is significant, and you deserve support. 🫂"
            ],
            
            # ENCOURAGEMENT
            'encouragement': [
                "You're stronger than you think, and you can work through this. 💪",
                "Remember, difficult times don't last forever. You've survived 100% of your worst days. 🌈",
                "You took an important step by reaching out. That shows courage. 🌟"
            ],
            
            # TRANSITION TO RESOURCES
            'transition_resources': [
                "Based on what you've shared, I have helpful resources - calming exercises, motivational videos (including funny ones!), and professional support options. These can really help. 🌈",
                "Let me help you with practical tools! I have breathing exercises, YouTube videos for relaxation and motivation, and helpful articles. 💙"
            ],
            
            # THANKS responses
            'thanks_response': [
                "You're very welcome! 😊 I'm here whenever you need support. Take care of yourself! 💙",
                "I'm glad I could help! 🌟 Feel free to come back anytime. You're doing great! 🤗"
            ],
            
            # GOODBYE
            'goodbye': [
                "Take care! 💙 Remember, I'm here 24/7 whenever you need support. You're not alone. Goodbye for now! 🌈",
                "Goodbye! 👋 Please be kind to yourself. You're strong and capable. Stay well! ✨"
            ]
        }
    
    # ===== ADD: Extract entities with spacy =====
    def extract_entities_with_spacy(self, user_input):
        """Extract important entities (people, organizations, etc.) using spacy"""
        try:
            if self.nlp is None:
                return []
            
            doc = self.nlp(user_input)
            entities = []
            
            for ent in doc.ents:
                entities.append({
                    'text': ent.text,
                    'label': ent.label_  # PERSON, ORG, DATE, GPE, etc.
                })
            
            return entities
        except:
            return []
    
    def extract_noun_chunks_with_spacy(self, user_input):
        """Extract key noun phrases using spacy"""
        try:
            if self.nlp is None:
                return []
            
            doc = self.nlp(user_input)
            noun_chunks = [chunk.text for chunk in doc.noun_chunks]
            return noun_chunks
        except:
            return []
    # ===== END: Spacy extraction =====
    
    def manage_conversation(self, user_id, user_input, sentiment_data):
        """Main conversation management"""
        
        # Initialize session
        if user_id not in self.sessions:
            self.sessions[user_id] = {
                'history': [],
                'current_state': 'initial',
                'emotion_detected': None,
                'problem_identified': None,
                'turn_count': 0,
                'last_interaction': datetime.now()
            }
        
        session = self.sessions[user_id]
        session['history'].append({
            'user': user_input,
            'sentiment': sentiment_data,
            'timestamp': datetime.now()
        })
        session['turn_count'] += 1
        
        text_lower = user_input.lower()
        
        # ===== ADD: Extract spacy entities =====
        entities = self.extract_entities_with_spacy(user_input)
        noun_chunks = self.extract_noun_chunks_with_spacy(user_input)
        # ===== END: Spacy extraction =====
        
        # Detect all matching intents
        intents = self._detect_all_intents(text_lower)
        
        # Generate response
        response = self._generate_smart_response(session, intents, sentiment_data, text_lower)
        
        # ===== ADD: Include spacy info in response =====
        if isinstance(response, dict):
            response['entities'] = entities
            response['noun_chunks'] = noun_chunks
        # ===== END: Add spacy info =====
        
        return response
    
    def _detect_all_intents(self, text):
        """Detect all matching intents"""
        detected = []
        for intent, pattern in self.intent_patterns.items():
            if re.search(pattern, text):
                detected.append(intent)
        return detected if detected else ['general']
    
    def _generate_smart_response(self, session, intents, sentiment_data, text_lower):
        """Generate intelligent contextual responses"""
        
        turn = session['turn_count']
        
        # GREETING
        if 'greeting' in intents:
            if turn == 1:
                return random.choice(self.responses['greeting_first'])
            else:
                return random.choice(self.responses['greeting_response'])
        
        # THANKS
        if 'thanks' in intents:
            return random.choice(self.responses['thanks_response'])
        
        # GOODBYE
        if 'goodbye' in intents:
            return random.choice(self.responses['goodbye'])
        
        # CRYING
        if 'crying' in intents:
            session['emotion_detected'] = 'crying'
            return random.choice(self.responses['crying_response'])
        
        # HAPPY
        if 'feeling_happy' in intents or 'feeling_good' in intents or sentiment_data['emotion'] == 'positive':
            if 'exam' in text_lower or 'marks' in text_lower or 'grade' in text_lower:
                return random.choice(self.responses['happy_because_marks'])
            else:
                return random.choice(self.responses['happy_response'])
        
        # STRESS-SPECIFIC
        if 'feeling_stressed' in intents and 'feeling_anxious' not in intents:
            session['emotion_detected'] = 'stress'
            if 'because' in intents or session['turn_count'] >= 3:
                if 'work_stress' in intents:
                    return self._build_response_with_resources(
                        random.choice(self.responses['sad_because_work']), 'negative'
                    )
                elif 'exam_stress' in intents:
                    return self._build_response_with_resources(
                        random.choice(self.responses['sad_because_exam']), 'negative'
                    )
                else:
                    return self._build_response_with_resources(
                        random.choice(self.responses['stress_response']), 'negative'
                    )
            else:
                return random.choice(self.responses['stress_response'])
        
        # ANXIETY-SPECIFIC
        if 'feeling_anxious' in intents and 'feeling_stressed' not in intents:
            session['emotion_detected'] = 'anxiety'
            if 'because' in intents or session['turn_count'] >= 3:
                return self._build_response_with_resources(
                    random.choice(self.responses['anxiety_response']), 'negative'
                )
            else:
                return random.choice(self.responses['anxiety_response'])
        
        # ANXIETY + STRESS COMBO
        if 'feeling_anxious' in intents and 'feeling_stressed' in intents:
            session['emotion_detected'] = 'anxiety_stress'
            if 'because' in intents or session['turn_count'] >= 3:
                return self._build_response_with_resources(
                    random.choice(self.responses['anxiety_stress_combo']), 'negative'
                )
            else:
                return random.choice(self.responses['anxiety_stress_combo'])
        
        # LOW MOOD
        if 'low_mood' in intents:
            session['emotion_detected'] = 'low_mood'
            if 'because' in intents or session['turn_count'] >= 3:
                return self._build_response_with_resources(
                    random.choice(self.responses['low_mood_response']), 'negative'
                )
            else:
                return random.choice(self.responses['low_mood_response'])
        
        # SAD/NEGATIVE - Handle ALL specific problems (FIXED VERSION)
        if 'feeling_sad' in intents or sentiment_data['emotion'] == 'negative' or 'feeling_depressed' in intents:
            session['emotion_detected'] = 'negative'
            
            # Check if specific problem mentioned
            has_problem = any([
                'friendship_problems' in intents,
                'relationship_problems' in intents,
                'family_problems' in intents,
                'bullying' in intents,
                'exam_stress' in intents,
                'work_stress' in intents,
                'money_problems' in intents,
                'health_problems' in intents,
                'self_esteem' in intents,
                'feeling_lonely' in intents,
                'someone_hurt' in intents
            ])
            
            # Give resources if: specific problem detected OR turn count >= 3 OR "because" mentioned
            if has_problem or 'because' in intents or session['turn_count'] >= 3:
                
                # FRIENDSHIP PROBLEMS
                if 'friendship_problems' in intents or 'someone_hurt' in intents:
                    session['problem_identified'] = 'friends'
                    return self._build_response_with_resources(
                        random.choice(self.responses['sad_because_friends']), 'negative'
                    )
                
                # RELATIONSHIP PROBLEMS
                elif 'relationship_problems' in intents:
                    session['problem_identified'] = 'relationship'
                    return self._build_response_with_resources(
                        random.choice(self.responses['sad_because_relationship']), 'negative'
                    )
                
                # FAMILY PROBLEMS
                elif 'family_problems' in intents:
                    session['problem_identified'] = 'family'
                    return self._build_response_with_resources(
                        random.choice(self.responses['sad_because_family']), 'negative'
                    )
                
                # BULLYING
                elif 'bullying' in intents:
                    session['problem_identified'] = 'bullying'
                    return self._build_response_with_resources(
                        random.choice(self.responses['sad_because_bullying']), 'negative'
                    )
                
                # EXAM STRESS
                elif 'exam_stress' in intents:
                    session['problem_identified'] = 'exam'
                    return self._build_response_with_resources(
                        random.choice(self.responses['sad_because_exam']), 'negative'
                    )
                
                # WORK STRESS
                elif 'work_stress' in intents:
                    session['problem_identified'] = 'work'
                    return self._build_response_with_resources(
                        random.choice(self.responses['sad_because_work']), 'negative'
                    )
                
                # MONEY PROBLEMS
                elif 'money_problems' in intents:
                    session['problem_identified'] = 'money'
                    return self._build_response_with_resources(
                        random.choice(self.responses['sad_because_money']), 'negative'
                    )
                
                # HEALTH PROBLEMS
                elif 'health_problems' in intents:
                    session['problem_identified'] = 'health'
                    return self._build_response_with_resources(
                        random.choice(self.responses['sad_because_health']), 'negative'
                    )
                
                # SELF-ESTEEM
                elif 'self_esteem' in intents:
                    session['problem_identified'] = 'self_esteem'
                    return self._build_response_with_resources(
                        random.choice(self.responses['sad_because_self_esteem']), 'negative'
                    )
                
                # LONELINESS
                elif 'feeling_lonely' in intents:
                    session['problem_identified'] = 'lonely'
                    return self._build_response_with_resources(
                        random.choice(self.responses['sad_because_lonely']), 'negative'
                    )
                
                # GENERAL SAD with explanation (turn 3+)
                else:
                    validation = random.choice(self.responses['validation'])
                    encouragement = random.choice(self.responses['encouragement'])
                    transition = random.choice(self.responses['transition_resources'])
                    return self._build_response_with_resources(
                        f"{validation} {encouragement} {transition}", 'negative'
                    )
            
            # First time saying sad - ask why (turn 1-2)
            else:
                return random.choice(self.responses['sad_initial'])
        
        # DEFAULT
        return "I'm here to listen. Would you like to share more about how you're feeling? I'm here to support you. 💙"
    
    def _build_response_with_resources(self, empathy_text, emotion, specific_type=None):
        """Build response that triggers resources"""
        return {
            'text': empathy_text,
            'trigger_resources': True,
            'emotion': emotion,
            'specific_type': specific_type
        }
    
    def detect_crisis(self, text):
        """Detect crisis keywords"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.crisis_keywords)
    
    def crisis_response(self):
        """Return crisis response"""
        return {
            'message': "I'm very concerned about what you're sharing. Your life matters. Please reach out to a professional immediately. 🆘",
            'emergency_resources': [
                {'service': 'National Suicide Prevention Lifeline (US)', 'number': '988', 'available': '24/7'},
                {'service': 'Crisis Text Line', 'instruction': 'Text HOME to 741741', 'available': '24/7'},
                {'service': 'Emergency Services', 'number': '911', 'instruction': 'Call for immediate help'}
            ],
            'is_crisis': True
        }
    
    def reset_session(self, user_id):
        """Reset session"""
        if user_id in self.sessions:
            del self.sessions[user_id]
