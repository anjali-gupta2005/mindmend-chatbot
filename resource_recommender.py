import random
from sklearn.feature_extraction.text import CountVectorizer  # ===== ADD: Scikit-learn =====
from sklearn.metrics.pairwise import cosine_similarity  # ===== ADD: Scikit-learn =====
import numpy as np  # ===== ADD: For ML calculations =====


class ResourceRecommender:
    """Recommends resources based on user emotion with real, working YouTube videos and detailed exercises"""
    
    def __init__(self):
        self.resources = {
            'negative': {
                'videos': [
                    # Meditation & Calming
                    {
                        'title': '5 Minute Meditation for Relaxation & Positive Energy',
                        'url': 'https://www.youtube.com/watch?v=VpHz8Mb13_Y',
                        'type': 'meditation',
                        'duration': '5 min',
                        'description': 'Quick meditation for instant calm and positive energy'
                    },
                    {
                        'title': 'Breathwork for Anxiety - Simple Breathing Exercises',
                        'url': 'https://www.youtube.com/watch?v=ci4Fpc8QFZw',
                        'type': 'calming',
                        'duration': '6 min',
                        'description': 'Fast-acting anti-anxiety breathing techniques'
                    },
                    {
                        'title': 'Guided Meditation For Relaxation & Healing',
                        'url': 'https://www.youtube.com/watch?v=q97MANMpsxI',
                        'type': 'meditation',
                        'duration': '10 min',
                        'description': 'Healing meditation for mental health and positive energy'
                    },
                    {
                        'title': 'Break the Anxiety Cycle - Breathing Exercises',
                        'url': 'https://www.youtube.com/watch?v=3-72jcwNi80',
                        'type': 'calming',
                        'duration': '18 min',
                        'description': 'Learn diaphragmatic, box, and 4-7-8 breathing techniques'
                    },
                    {
                        'title': '11-Minute Guided Meditation for Stress & Anger',
                        'url': 'https://www.soulsensei.in/play/harrish-sai-raman-guided-meditation-to-manage-stress-and-anger',
                        'type': 'meditation',
                        'duration': '11 min',
                        'description': 'Release stress, anxiety, and negative feelings'
                    },
                    {
                        'title': 'Calming Music for Stress Relief - Peaceful Meditation',
                        'url': 'https://www.youtube.com/watch?v=lFcSrYw-ARY',
                        'type': 'relaxation',
                        'duration': '3 hours',
                        'description': 'Soothing background music for deep relaxation'
                    },
                    {
                        'title': 'The Guided Meditation You Need for 2025',
                        'url': 'https://www.youtube.com/watch?v=3r0YscOXAlI',
                        'type': 'meditation',
                        'duration': '20 min',
                        'description': 'Let go of mental burdens and stress from the year'
                    },
                    {
                        'title': '10 Minute Mindfulness Meditation for Anxiety',
                        'url': 'https://www.youtube.com/watch?v=O-6f5wQXSu8',
                        'type': 'meditation',
                        'duration': '10 min',
                        'description': 'Mindfulness practice for managing anxious thoughts'
                    },
                    
                    # Funny & Motivational (NEW)
                    {
                        'title': 'FUNNY Stress Management Techniques - Humor for Mental Health',
                        'url': 'https://www.youtube.com/watch?v=ybnzd4zu8xs',
                        'type': 'funny',
                        'duration': '5 min',
                        'description': 'Hilarious stress relief techniques by TEDx speaker'
                    },
                    {
                        'title': 'Take Care of Yourself - Mental Health Stand Up Comedy',
                        'url': 'https://www.youtube.com/watch?v=k6uK26y12Jo',
                        'type': 'funny',
                        'duration': '1 min',
                        'description': 'Funny take on self-care and mental health'
                    },
                    {
                        'title': 'How To Take Charge of Your Mental Health - Motivational',
                        'url': 'https://www.youtube.com/watch?v=IC9DM7w-pm8',
                        'type': 'motivational',
                        'duration': '5 min',
                        'description': 'Inspiring story of overcoming bipolar disorder'
                    },
                    {
                        'title': 'Conquering Exam Stress - Educational Video',
                        'url': 'https://www.youtube.com/watch?v=-RZ86OB9hw4',
                        'type': 'educational',
                        'duration': '4 min',
                        'description': 'Learn how to manage exam anxiety scientifically'
                    },
                    {
                        'title': 'Funny Motivational Speaker on Resilience',
                        'url': 'https://www.youtube.com/watch?v=IsSQ3-udjUo',
                        'type': 'funny',
                        'duration': '10 min',
                        'description': 'Humorous and uplifting talk about building resilience'
                    },
                    {
                        'title': 'Ross Szabo - Humorous Mental Health Awareness',
                        'url': 'https://www.youtube.com/watch?v=49FVdfdeTmE',
                        'type': 'funny',
                        'duration': '60 min',
                        'description': 'Evidence-based mental health education with humor'
                    }
                ],
                'exercises': [
                    {
                        'name': '4-7-8 Breathing Technique (Calms Anxiety Instantly)',
                        'description': 'Breathe in through your nose for 4 counts, hold your breath for 7 counts, then exhale slowly through your mouth for 8 counts. Repeat 4 times.',
                        'duration': '2-3 minutes',
                        'benefit': 'Activates relaxation response, reduces anxiety within minutes',
                        'steps': [
                            '1. Sit comfortably with your back straight',
                            '2. Place tongue tip behind upper front teeth',
                            '3. Exhale completely through mouth (whoosh sound)',
                            '4. Close mouth, inhale through nose for 4 counts',
                            '5. Hold breath for 7 counts',
                            '6. Exhale through mouth for 8 counts (whoosh sound)',
                            '7. Repeat cycle 4 times total'
                        ],
                        'when_to_use': 'Before sleep, during panic attacks, when feeling overwhelmed'
                    },
                    {
                        'name': 'Progressive Muscle Relaxation (PMR)',
                        'description': 'Systematically tense and release each muscle group from toes to head. Tense for 5 seconds, release for 10 seconds, notice the difference.',
                        'duration': '10-15 minutes',
                        'benefit': 'Releases physical tension, reduces muscle pain and stress',
                        'steps': [
                            '1. Lie down or sit comfortably',
                            '2. Start with your feet - curl toes tightly (5 sec)',
                            '3. Release and notice the relaxation (10 sec)',
                            '4. Move to calves, thighs, buttocks, stomach',
                            '5. Continue to hands, arms, shoulders, neck',
                            '6. Finish with facial muscles',
                            '7. Take 3 deep breaths at the end'
                        ],
                        'when_to_use': 'Before bedtime, when body feels tense, after stressful events'
                    },
                    {
                        'name': '5-4-3-2-1 Grounding Technique',
                        'description': 'Use your 5 senses to anchor yourself in the present moment. Name 5 things you see, 4 you can touch, 3 you hear, 2 you smell, 1 you taste.',
                        'duration': '3-5 minutes',
                        'benefit': 'Stops panic attacks, reduces dissociation, brings you back to present',
                        'steps': [
                            '1. Look around and name 5 things you can SEE',
                            '2. Notice 4 things you can TOUCH (texture, temperature)',
                            '3. Listen for 3 things you can HEAR',
                            '4. Identify 2 things you can SMELL',
                            '5. Notice 1 thing you can TASTE',
                            '6. Take 3 slow, deep breaths'
                        ],
                        'when_to_use': 'During panic attacks, flashbacks, anxiety spirals, dissociation'
                    },
                    {
                        'name': 'Box Breathing (Navy SEAL Technique)',
                        'description': 'Breathe in a square pattern: Inhale for 4, hold for 4, exhale for 4, hold for 4. Used by Navy SEALs to stay calm under pressure.',
                        'duration': '5-10 minutes',
                        'benefit': 'Lowers heart rate, improves focus, reduces stress hormones',
                        'steps': [
                            '1. Sit with feet flat on floor, hands on lap',
                            '2. Exhale completely to empty lungs',
                            '3. Inhale slowly through nose for 4 counts',
                            '4. Hold your breath for 4 counts',
                            '5. Exhale slowly through mouth for 4 counts',
                            '6. Hold empty lungs for 4 counts',
                            '7. Repeat for 5-10 cycles'
                        ],
                        'when_to_use': 'Before important meetings, exams, stressful situations'
                    },
                    {
                        'name': 'Gratitude Journaling (3 Good Things)',
                        'description': 'Write down 3 specific things you\'re grateful for today, no matter how small. Include WHY you\'re grateful for each.',
                        'duration': '5-10 minutes',
                        'benefit': 'Shifts focus from negative to positive, improves mood and sleep',
                        'steps': [
                            '1. Get a notebook or open notes app',
                            '2. Write today\'s date',
                            '3. List 3 things you\'re grateful for',
                            '4. For each, write WHY you\'re grateful',
                            '5. Be specific (not just "my family" but "my sister called to check on me")',
                            '6. Reread your entries when feeling down'
                        ],
                        'when_to_use': 'Before bedtime, when feeling pessimistic, as daily morning ritual'
                    },
                    {
                        'name': 'Mindful Walking (Walking Meditation)',
                        'description': 'Walk slowly and deliberately, paying full attention to each step. Feel your feet touching the ground, notice your surroundings with all senses.',
                        'duration': '10-20 minutes',
                        'benefit': 'Combines physical activity with mindfulness, reduces rumination',
                        'steps': [
                            '1. Find a quiet path or room',
                            '2. Stand still, feel your body\'s weight',
                            '3. Begin walking very slowly',
                            '4. Notice heel touching ground, then toes',
                            '5. Feel weight shifting from foot to foot',
                            '6. Notice sights, sounds, smells around you',
                            '7. When mind wanders, gently return focus to feet'
                        ],
                        'when_to_use': 'When too restless to sit still, need gentle movement, feeling stuck'
                    },
                    {
                        'name': 'Body Scan Meditation',
                        'description': 'Mentally scan your body from head to toe, noticing sensations without judgment. Release tension as you go.',
                        'duration': '10-20 minutes',
                        'benefit': 'Increases body awareness, releases stored tension, improves sleep',
                        'steps': [
                            '1. Lie down in a comfortable position',
                            '2. Close eyes, take 3 deep breaths',
                            '3. Focus attention on top of head',
                            '4. Slowly move awareness down through body',
                            '5. Notice sensations in each area (2-3 min per area)',
                            '6. Breathe into any tension you notice',
                            '7. Imagine releasing tension with each exhale'
                        ],
                        'when_to_use': 'Before sleep, when body feels tense, during chronic pain episodes'
                    },
                    {
                        'name': 'Emotional Freedom Technique (EFT Tapping)',
                        'description': 'Tap specific acupressure points while stating affirmations to release emotional distress.',
                        'duration': '5-10 minutes',
                        'benefit': 'Reduces anxiety, calms nervous system, releases emotional blocks',
                        'steps': [
                            '1. Identify the emotion/issue (rate intensity 0-10)',
                            '2. Create setup statement: "Even though I feel [emotion], I deeply accept myself"',
                            '3. Tap karate chop point while saying setup 3 times',
                            '4. Tap each point 7 times while stating reminder phrase:',
                            '   - Top of head, eyebrow, side of eye, under eye',
                            '   - Under nose, chin, collarbone, under arm',
                            '5. Take deep breath, re-rate intensity',
                            '6. Repeat until intensity drops below 3'
                        ],
                        'when_to_use': 'During emotional overwhelm, before triggering situations, daily stress relief'
                    }
                ],
                'articles': [
                    {
                        'title': 'Understanding Anxiety and Depression',
                        'url': 'https://www.nimh.nih.gov/health/topics/anxiety-disorders',
                        'summary': 'Comprehensive guide on anxiety disorders, symptoms, and treatments from NIMH',
                        'source': 'National Institute of Mental Health'
                    },
                    {
                        'title': 'Grounding Techniques for Stress Relief',
                        'url': 'https://click2pro.com/blog/grounding-techniques-stress-guided-meditation',
                        'summary': 'Best grounding techniques and guided meditation tips for stress management',
                        'source': 'Click2Pro'
                    },
                    {
                        'title': 'Evidence-Based Coping Strategies for Mental Health',
                        'url': 'https://www.mentalhealth.org.uk/explore-mental-health',
                        'summary': 'Science-backed strategies for managing mental health challenges',
                        'source': 'Mental Health Foundation'
                    },
                    {
                        'title': 'Mindfulness Meditation: A Research-Backed Approach',
                        'url': 'https://www.apa.org/topics/mindfulness/meditation',
                        'summary': 'How mindfulness meditation reduces stress and improves well-being',
                        'source': 'American Psychological Association'
                    }
                ],
                'professional_resources': [
                    {
                        'name': 'BetterHelp - Online Therapy',
                        'description': 'Connect with licensed therapists via video, phone, or messaging',
                        'url': 'https://www.betterhelp.com',
                        'type': 'Online Therapy Platform',
                        'cost': 'Starting at $65/week'
                    },
                    {
                        'name': 'SAMHSA National Helpline',
                        'description': 'Free, confidential, 24/7 treatment referral and information service',
                        'number': '1-800-662-4357',
                        'type': 'Crisis Helpline',
                        'cost': 'Free'
                    },
                    {
                        'name': 'Psychology Today - Find a Therapist',
                        'description': 'Search for therapists by location, specialty, and insurance',
                        'url': 'https://www.psychologytoday.com/us/therapists',
                        'type': 'Therapist Directory',
                        'cost': 'Varies by provider'
                    },
                    {
                        'name': 'Crisis Text Line',
                        'description': 'Free 24/7 crisis support via text message',
                        'number': 'Text HOME to 741741',
                        'type': 'Text Support',
                        'cost': 'Free'
                    },
                    {
                        'name': 'Talkspace - Online Therapy',
                        'description': 'Licensed therapists available for text, video, and audio sessions',
                        'url': 'https://www.talkspace.com',
                        'type': 'Online Therapy Platform',
                        'cost': 'Starting at $69/week'
                    }
                ]
            },
            'positive': {
                'videos': [
                    {
                        'title': 'Energizing Morning Yoga Flow - 15 Minutes',
                        'url': 'https://www.youtube.com/watch?v=gC_L9qAHVJ8',
                        'type': 'energetic',
                        'duration': '15 min',
                        'description': 'Energizing yoga to start your day with positive energy'
                    },
                    {
                        'title': 'Upbeat Motivational Music for Positive Vibes',
                        'url': 'https://www.youtube.com/watch?v=ZXsQAWx_ao0',
                        'type': 'motivational',
                        'duration': '30 min',
                        'description': 'Uplifting music compilation to boost your mood'
                    },
                    {
                        'title': 'Guided Meditation for Gratitude & Joy',
                        'url': 'https://www.youtube.com/watch?v=q97MANMpsxI',
                        'type': 'meditation',
                        'duration': '10 min',
                        'description': 'Enhance positive feelings with gratitude meditation'
                    },
                    {
                        'title': '5-Minute Positive Energy Meditation',
                        'url': 'https://www.youtube.com/watch?v=VpHz8Mb13_Y',
                        'type': 'meditation',
                        'duration': '5 min',
                        'description': 'Quick meditation to amplify positive emotions'
                    }
                ],
                'exercises': [
                    {
                        'name': 'Gratitude Amplification Practice',
                        'description': 'Take your current positive feeling and intentionally amplify it by identifying 5 specific reasons you feel good right now.',
                        'duration': '5 minutes',
                        'benefit': 'Strengthens positive emotions, creates lasting joy',
                        'steps': [
                            '1. Notice your current positive feeling',
                            '2. Write down 5 specific reasons you feel this way',
                            '3. For each reason, write why it matters to you',
                            '4. Reread your list slowly, savoring each one',
                            '5. Take 3 deep breaths while holding this feeling'
                        ]
                    },
                    {
                        'name': 'Joy Journaling',
                        'description': 'Document your positive moments in detail to make them last longer and create a resource for difficult days.',
                        'duration': '10 minutes',
                        'benefit': 'Extends positive emotions, creates resilience bank',
                        'steps': [
                            '1. Describe what happened in detail',
                            '2. Note how you felt physically in your body',
                            '3. Write about who was involved',
                            '4. Identify what made this moment special',
                            '5. Write how you can create more moments like this'
                        ]
                    },
                    {
                        'name': 'Savoring Exercise',
                        'description': 'Fully experience and extend your positive moment by engaging all five senses deliberately.',
                        'duration': '5-10 minutes',
                        'benefit': 'Maximizes positive emotion duration, increases life satisfaction',
                        'steps': [
                            '1. Pause and notice you\'re having a good moment',
                            '2. Engage all 5 senses - what do you see, hear, feel, smell, taste?',
                            '3. Share this moment with someone (text, call, or tell them)',
                            '4. Take a mental photograph to remember later',
                            '5. Express gratitude for this moment out loud or in writing'
                        ]
                    }
                ],
                'articles': [
                    {
                        'title': 'The Science of Happiness: Maintaining Mental Wellness',
                        'url': 'https://www.mentalhealth.gov/basics/what-is-mental-health',
                        'summary': 'Research-backed strategies for sustaining positive mental health',
                        'source': 'MentalHealth.gov'
                    },
                    {
                        'title': 'Building Emotional Resilience',
                        'url': 'https://www.apa.org/topics/resilience',
                        'summary': 'How to build and maintain psychological resilience',
                        'source': 'American Psychological Association'
                    }
                ]
            },
            'neutral': {
                'videos': [
                    {
                        'title': 'Introduction to Mindfulness Meditation',
                        'url': 'https://www.youtube.com/watch?v=6p_yaNFSYao',
                        'type': 'educational',
                        'duration': '10 min',
                        'description': 'Learn the basics of mindfulness practice'
                    },
                    {
                        'title': 'Gentle Relaxation Music',
                        'url': 'https://www.youtube.com/watch?v=lFcSrYw-ARY',
                        'type': 'relaxation',
                        'duration': '30 min',
                        'description': 'Peaceful background music for focus and calm'
                    }
                ],
                'exercises': [
                    {
                        'name': 'Daily Emotional Check-In',
                        'description': 'Take 5 minutes to scan your emotional and physical state without judgment.',
                        'duration': '5 minutes',
                        'benefit': 'Builds self-awareness, prevents emotional buildup',
                        'steps': [
                            '1. Find a quiet moment in your day',
                            '2. Ask yourself: "How am I feeling physically?"',
                            '3. Ask: "What emotions am I experiencing?"',
                            '4. Ask: "What do I need right now?"',
                            '5. Write brief answers in a journal or notes app',
                            '6. Notice patterns over days and weeks'
                        ]
                    },
                    {
                        'name': 'Mindful Breathing Anchor',
                        'description': 'Use breath as an anchor to present moment awareness throughout your day.',
                        'duration': '3 minutes',
                        'benefit': 'Reduces stress, improves focus, creates mental clarity',
                        'steps': [
                            '1. Stop whatever you\'re doing',
                            '2. Close eyes or soften gaze',
                            '3. Notice natural rhythm of your breath',
                            '4. Count 10 breaths slowly',
                            '5. When mind wanders, gently return to counting',
                            '6. Open eyes, return to your day'
                        ]
                    }
                ]
            }
        }
    
    # ===== ADD: Smart resource matching using scikit-learn =====
    def find_best_resources_sklearn(self, emotion, user_context=None):
        """Use scikit-learn to intelligently match resources to user needs"""
        try:
            if emotion not in self.resources:
                emotion = 'negative'
            
            resource_set = self.resources[emotion]
            videos = resource_set.get('videos', [])
            
            # If user context provided, use ML for smart matching
            if user_context and videos:
                try:
                    # Vectorize video descriptions
                    video_texts = [
                        v.get('title', '') + ' ' + v.get('description', '') 
                        for v in videos
                    ]
                    
                    vectorizer = CountVectorizer(stop_words='english', max_features=50)
                    video_vectors = vectorizer.fit_transform(video_texts)
                    
                    # Vectorize user context
                    context_vector = vectorizer.transform([user_context])
                    
                    # Calculate similarity using cosine similarity
                    similarities = cosine_similarity(context_vector, video_vectors)[0]
                    
                    # Sort by similarity (highest first)
                    sorted_indices = np.argsort(similarities)[::-1]
                    
                    # Return top matches
                    best_videos = [videos[i] for i in sorted_indices[:5]]
                    return best_videos
                except:
                    return random.sample(videos, min(5, len(videos)))
            
            return random.sample(videos, min(5, len(videos)))
        except:
            return []
    # ===== END: Scikit-learn matching =====
    
    def recommend_resources(self, emotion, mood_preference=None, user_context=None):
        """
        Recommend resources based on emotion
        Returns: dict with videos, exercises, articles, and professional resources
        
        ===== UPDATED: Now with scikit-learn ML matching =====
        """
        
        if emotion not in self.resources:
            emotion = 'negative'  # Default fallback
        
        resources = self.resources[emotion].copy()
        
        # ===== ADD: Use ML-based resource matching =====
        videos = self.find_best_resources_sklearn(emotion, user_context)
        if not videos:
            videos = resources.get('videos', [])
        # ===== END: ML matching =====
        
        # Filter videos by mood preference if specified
        if mood_preference and videos:
            filtered_videos = [
                v for v in videos 
                if v.get('type') == mood_preference
            ]
            
            if filtered_videos:
                videos = filtered_videos
        
        # Return selection of resources
        result = {}
        
        # Return 4-5 videos (increased for more variety)
        result['videos'] = videos[:5] if videos else []
        
        if 'exercises' in resources:
            # Return 3-4 exercises with full details
            result['exercises'] = random.sample(
                resources['exercises'],
                min(4, len(resources['exercises']))
            )
        
        if 'articles' in resources:
            result['articles'] = resources['articles'][:3]
        
        if emotion == 'negative' and 'professional_resources' in resources:
            result['professional_resources'] = resources['professional_resources'][:3]
        
        return result
