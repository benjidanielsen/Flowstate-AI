#!/usr/bin/env python3
"""
AI-Powered Notes Processor for Flowstate-AI CRM
Handles natural language processing, time extraction, and lead matching
"""

import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from openai import OpenAI

client = OpenAI()

class NotesProcessor:
    """Process quick notes with AI-powered categorization and extraction"""
    
    # Norwegian and English time patterns
    TIME_PATTERNS = {
        'no': {
            'time': r'(\d{1,2}):(\d{2})',
            'relative_time': r'(om|i|etter)\s+(\d+)\s+(minutt|timer|time|dag|dager|uke|uker)',
            'specific_day': r'(i\s+dag|i\s+morgen|neste\s+uke|på\s+(mandag|tirsdag|onsdag|torsdag|fredag|lørdag|søndag))',
        },
        'en': {
            'time': r'(\d{1,2}):(\d{2})',
            'relative_time': r'(in|after)\s+(\d+)\s+(minute|minutes|hour|hours|day|days|week|weeks)',
            'specific_day': r'(today|tomorrow|next\s+week|on\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday))',
        }
    }
    
    def __init__(self):
        self.client = OpenAI()
    
    def detect_language(self, text: str) -> str:
        """Detect if text is Norwegian or English"""
        norwegian_words = ['å', 'høre', 'skulle', 'ville', 'kommer', 'på', 'til']
        english_words = ['to', 'hear', 'should', 'would', 'comes', 'on', 'at']
        
        no_count = sum(1 for word in norwegian_words if word in text.lower())
        en_count = sum(1 for word in english_words if word in text.lower())
        
        return 'no' if no_count > en_count else 'en'
    
    def extract_time_info(self, text: str, language: str) -> Dict:
        """Extract time and date information from text"""
        result = {
            'time': None,
            'date': None,
            'datetime': None,
            'relative': None
        }
        
        patterns = self.TIME_PATTERNS.get(language, self.TIME_PATTERNS['en'])
        
        # Extract specific time (HH:MM)
        time_match = re.search(patterns['time'], text)
        if time_match:
            hour, minute = int(time_match.group(1)), int(time_match.group(2))
            result['time'] = f"{hour:02d}:{minute:02d}"
            
            # Assume today if no date specified
            now = datetime.now()
            target_datetime = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # If time has passed today, assume tomorrow
            if target_datetime < now:
                target_datetime += timedelta(days=1)
            
            result['datetime'] = target_datetime.isoformat()
            result['date'] = target_datetime.date().isoformat()
        
        # Extract relative time
        relative_match = re.search(patterns['relative_time'], text, re.IGNORECASE)
        if relative_match:
            amount = int(relative_match.group(2))
            unit = relative_match.group(3).lower()
            
            now = datetime.now()
            if 'minutt' in unit or 'minute' in unit:
                target_datetime = now + timedelta(minutes=amount)
            elif 'time' in unit or 'hour' in unit:
                target_datetime = now + timedelta(hours=amount)
            elif 'dag' in unit or 'day' in unit:
                target_datetime = now + timedelta(days=amount)
            elif 'uke' in unit or 'week' in unit:
                target_datetime = now + timedelta(weeks=amount)
            else:
                target_datetime = now
            
            result['datetime'] = target_datetime.isoformat()
            result['date'] = target_datetime.date().isoformat()
            result['relative'] = f"{amount} {unit}"
        
        return result
    
    def extract_person_names(self, text: str) -> List[str]:
        """Extract potential person names from text (capitalized words)"""
        # Simple heuristic: look for capitalized words that might be names
        words = text.split()
        potential_names = []
        
        for i, word in enumerate(words):
            # Remove punctuation
            clean_word = re.sub(r'[^\w\s]', '', word)
            if clean_word and clean_word[0].isupper() and len(clean_word) > 2:
                # Check if it's not a common word
                common_words = ['Skrive', 'Write', 'Send', 'Call', 'Email', 'Message']
                if clean_word not in common_words:
                    potential_names.append(clean_word)
        
        return potential_names
    
    def match_leads(self, names: List[str], conn) -> List[Dict]:
        """Match extracted names against leads in database"""
        if not names:
            return []
        
        cursor = conn.cursor()
        matches = []
        
        for name in names:
            # Search for leads with similar names
            cursor.execute("""
                SELECT id, name, email, phone, stage, pipeline
                FROM leads
                WHERE name LIKE ? OR name LIKE ?
                ORDER BY 
                    CASE 
                        WHEN name LIKE ? THEN 1
                        WHEN name LIKE ? THEN 2
                        ELSE 3
                    END
                LIMIT 5
            """, (f"{name}%", f"% {name}%", f"{name}%", f"% {name}%"))
            
            results = cursor.fetchall()
            for row in results:
                matches.append({
                    'id': row[0],
                    'name': row[1],
                    'email': row[2],
                    'phone': row[3],
                    'stage': row[4],
                    'pipeline': row[5],
                    'matched_on': name
                })
        
        return matches
    
    def categorize_note_with_ai(self, text: str, language: str) -> Dict:
        """Use AI to categorize and extract structured information from note"""
        
        system_prompt = """You are an AI assistant helping to categorize and extract information from quick notes in a CRM system.
        
Analyze the note and extract:
1. note_type: "reminder", "follow_up", "meeting", "general", "task"
2. priority: "low", "normal", "high", "urgent"
3. action_required: true/false
4. summary: A brief 1-sentence summary
5. suggested_lead_name: If a person's name is mentioned
6. confidence: 0.0-1.0 score of how confident you are

Respond in JSON format only."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Language: {language}\nNote: {text}"}
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            print(f"AI categorization error: {e}")
            return {
                "note_type": "general",
                "priority": "normal",
                "action_required": False,
                "summary": text[:100],
                "confidence": 0.5
            }
    
    def process_note(self, text: str, conn) -> Dict:
        """Main processing function for a quick note"""
        
        # Detect language
        language = self.detect_language(text)
        
        # Extract time information
        time_info = self.extract_time_info(text, language)
        
        # Extract person names
        names = self.extract_person_names(text)
        
        # Match leads
        lead_matches = self.match_leads(names, conn)
        
        # AI categorization
        ai_analysis = self.categorize_note_with_ai(text, language)
        
        # Determine if disambiguation is needed
        requires_disambiguation = len(lead_matches) > 1
        
        result = {
            'raw_content': text,
            'language': language,
            'time_info': time_info,
            'extracted_names': names,
            'lead_matches': lead_matches,
            'ai_analysis': ai_analysis,
            'requires_disambiguation': requires_disambiguation,
            'note_type': ai_analysis.get('note_type', 'general'),
            'priority': ai_analysis.get('priority', 'normal'),
            'confidence': ai_analysis.get('confidence', 0.5)
        }
        
        return result
