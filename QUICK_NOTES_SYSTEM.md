# Quick Notes System - AI-Powered CRM Note Taking

## Overview

The Quick Notes System is an intelligent, always-accessible note-taking feature integrated into the Flowstate-AI CRM dashboard. It uses AI to automatically categorize notes, extract time information, match leads, and create reminders.

## Key Features

### 1. **Always Accessible**
- Floating widget available on every dashboard tab
- Keyboard shortcut: `Ctrl+N` or `Cmd+N`
- Quick access from anywhere in the system

### 2. **Bilingual Support**
- **Norwegian (Bokmål)**: Full support for Norwegian language notes
- **English**: Complete English language support
- Automatic language detection

### 3. **AI-Powered Processing**
- **Auto-Categorization**: Automatically determines note type (reminder, follow-up, meeting, task, general)
- **Time Extraction**: Understands natural language time references
  - Specific times: "20:00", "15:30"
  - Relative times: "om 2 timer" (in 2 hours), "i morgen" (tomorrow)
- **Lead Matching**: Automatically finds and matches person names to CRM leads
- **Priority Detection**: Assigns priority levels (low, normal, high, urgent)

### 4. **Smart Disambiguation**
- When multiple leads match a name, the system asks for clarification
- Visual notification with sound alert
- Screen blink effect to grab attention
- Options to:
  - Select the correct lead
  - Skip and save as general note
  - Cancel (press ESC)

### 5. **Automatic Reminders**
- Creates reminders when time/date is detected
- Integrates with calendar system
- Notification system for upcoming reminders

## Usage Examples

### Norwegian Examples

**Example 1: Simple Reminder**
```
Skrive til Nora å høre om hun kommer på callen 20:00
```
**AI Processing:**
- Detects: Nora (person name)
- Time: 20:00 (today or tomorrow if past)
- Type: Follow-up
- Creates reminder for 20:00

**Example 2: Meeting Note**
```
Henrik ville bli med på en call likevell, 15:30
```
**AI Processing:**
- Detects: Henrik (person name)
- Time: 15:30
- Type: Meeting
- Creates reminder for 15:30

**Example 3: General Note**
```
Må huske å følge opp med Emma neste uke
```
**AI Processing:**
- Detects: Emma (person name)
- Time: Next week (relative)
- Type: Reminder
- Creates reminder for next week

### English Examples

**Example 1: Task Note**
```
Call Jonas about the proposal tomorrow at 2pm
```
**AI Processing:**
- Detects: Jonas (person name)
- Time: Tomorrow at 14:00
- Type: Task
- Creates reminder for tomorrow 14:00

**Example 2: Follow-up**
```
Need to send contract to Nora Fredriksen by Friday
```
**AI Processing:**
- Detects: Nora Fredriksen (full name)
- Time: Friday
- Type: Follow-up
- Creates reminder for Friday

## Disambiguation Flow

When the system finds multiple leads with similar names:

1. **Visual Alert**
   - Screen blinks (subtle pulse effect)
   - Notification sound plays
   - Modal dialog appears

2. **Options Presented**
   ```
   Found multiple matches for "Nora":
   
   ○ Nora Fredriksen (nora.f@example.com) - Qualified, Sales
   ○ Nora Henriksen (nora.h@example.com) - New, Sales
   
   [Select Lead] [Skip] [Cancel (ESC)]
   ```

3. **User Actions**
   - **Select**: Choose the correct lead and commit note
   - **Skip**: Save as general note without lead assignment
   - **Cancel**: Discard the note (press ESC or click outside)

## Database Schema

### quick_notes Table
```sql
- id: Primary key
- content: AI-generated summary
- raw_content: Original note text
- note_type: reminder|follow_up|meeting|task|general
- lead_id: Foreign key to leads table
- lead_name: Cached lead name
- extracted_time: Time extracted (HH:MM)
- extracted_date: Date extracted (YYYY-MM-DD)
- reminder_datetime: Full datetime for reminder
- language: no|en
- priority: low|normal|high|urgent
- status: pending|processed|auto_assigned|skipped
- ai_confidence: 0.0-1.0
- ai_suggestions: JSON with AI analysis
- requires_disambiguation: Boolean
- disambiguation_options: JSON with lead options
- created_at, processed_at, committed_at: Timestamps
```

### reminders Table
```sql
- id: Primary key
- note_id: Foreign key to quick_notes
- lead_id: Foreign key to leads
- reminder_datetime: When to remind
- title: Reminder title
- description: Reminder description
- status: pending|completed|cancelled
- notification_sent: Boolean
- created_at, completed_at: Timestamps
```

### leads Table (Enhanced)
```sql
- id: Primary key
- external_id: Unique external identifier
- name: Full name
- email, phone, handle_ig: Contact info
- lifecycle_stage: subscriber|lead|mql|sql|customer|partner
- stage: Pipeline stage
- pipeline: Sales|Recruiting
- consent_*: GDPR consent fields
- utm_*: Marketing attribution
- score: Lead score
- owner_id: Assigned team member
- created_at, updated_at: Timestamps
```

## API Endpoints

### POST /api/quick_note
Create and process a new quick note.

**Request:**
```json
{
  "note": "Skrive til Nora å høre om hun kommer på callen 20:00"
}
```

**Response:**
```json
{
  "note_id": 1,
  "status": "success",
  "requires_disambiguation": true,
  "lead_matches": [
    {
      "id": 1,
      "name": "Nora Fredriksen",
      "email": "nora.f@example.com",
      "stage": "Qualified",
      "pipeline": "Sales"
    },
    {
      "id": 2,
      "name": "Nora Henriksen",
      "email": "nora.h@example.com",
      "stage": "New",
      "pipeline": "Sales"
    }
  ],
  "time_info": {
    "time": "20:00",
    "date": "2025-10-06",
    "datetime": "2025-10-06T20:00:00"
  },
  "ai_analysis": {
    "note_type": "follow_up",
    "priority": "normal",
    "action_required": true,
    "summary": "Follow up with Nora about call at 20:00",
    "confidence": 0.85
  },
  "language": "no"
}
```

### POST /api/quick_note/<note_id>/resolve
Resolve disambiguation by selecting a lead.

**Request:**
```json
{
  "lead_id": 1,
  "action": "assign"
}
```

**Response:**
```json
{
  "status": "success"
}
```

### GET /api/quick_notes/pending
Get all notes requiring disambiguation.

**Response:**
```json
[
  {
    "id": 1,
    "content": "Skrive til Nora å høre om hun kommer på callen 20:00",
    "options": [...],
    "created_at": "2025-10-06T13:45:00",
    "priority": "normal"
  }
]
```

### GET /api/reminders/upcoming
Get upcoming reminders.

**Response:**
```json
[
  {
    "id": 1,
    "reminder_datetime": "2025-10-06T20:00:00",
    "title": "Follow up: Nora Fredriksen",
    "description": "Skrive til Nora å høre om hun kommer på callen 20:00",
    "lead_name": "Nora Fredriksen",
    "email": "nora.f@example.com",
    "phone": "+4791234567"
  }
]
```

## Frontend Components

### Quick Notes Widget
- Floating button (bottom-right corner)
- Expandable textarea
- Real-time character count
- Submit button with loading state

### Disambiguation Modal
- Centered modal dialog
- Lead options with radio buttons
- Lead details (email, stage, pipeline)
- Action buttons (Select, Skip, Cancel)
- Keyboard navigation (Tab, Enter, ESC)

### Notification System
- Visual: Screen blink effect
- Audio: Notification sound
- Badge: Pending notes counter
- Toast: Success/error messages

## Integration with Frazer Method

The Quick Notes System is fully compatible with the Frazer Method CRM pipeline:

1. **Pipeline Stages**: Lead Generation → Qualification → Nurturing → Conversion → Retention
2. **Lifecycle Stages**: subscriber → lead → mql → sql → customer → partner
3. **GDPR Compliance**: Consent tracking for email, SMS, messaging
4. **UTM Tracking**: Full marketing attribution support
5. **Multi-Pipeline**: Supports both Sales and Recruiting pipelines

## Technical Implementation

### Backend (Python/Flask)
- `unified_dashboard.py`: API endpoints
- `brain/notes_processor.py`: AI processing logic
- `setup_crm_database.py`: Database schema

### Frontend (JavaScript)
- `static/js/quick_notes.js`: Widget and interaction logic
- `static/css/style.css`: Styling (integrated)

### AI Processing (OpenAI)
- Model: `gpt-4.1-mini`
- Temperature: 0.3 (for consistency)
- Max tokens: 300
- Response format: JSON

## Best Practices

1. **Be Natural**: Write notes as you would speak
2. **Include Names**: Mention person names for auto-matching
3. **Specify Times**: Use clear time references (20:00, tomorrow, next week)
4. **Review Disambiguation**: Always verify the correct lead when prompted
5. **Use Priorities**: System auto-detects, but you can override

## Future Enhancements

- [ ] Voice input support
- [ ] Mobile app integration
- [ ] Bulk note import
- [ ] Advanced search and filtering
- [ ] Note templates
- [ ] Team collaboration features
- [ ] Integration with external calendars (Google Calendar, Outlook)
- [ ] WhatsApp/SMS integration for reminders
- [ ] Machine learning improvement based on user corrections

## Troubleshooting

### Note not processing
- Check internet connection (AI requires API access)
- Verify OpenAI API key is configured
- Check browser console for errors

### Lead not matching
- Ensure lead exists in database
- Check name spelling
- Try using full name instead of first name only

### Reminder not created
- Verify time format is recognized
- Check that datetime is in the future
- Ensure lead was successfully matched

### Disambiguation not appearing
- Check if multiple leads actually exist with that name
- Verify JavaScript is enabled
- Check browser console for errors

## Support

For issues or questions:
- Check system logs: `/home/ubuntu/Flowstate-AI/dashboard.log`
- Review database: `sqlite3 godmode-state.db`
- Contact: System Administrator

---

**Version**: 1.0.0  
**Last Updated**: October 6, 2025  
**Author**: Manus AI + Flowstate-AI Team
