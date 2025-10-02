# FlowState-AI API Documentation

**Version:** 1.0  
**Base URL:** `http://localhost:3001/api`  
**Last Updated:** 2025-10-02

---

## Table of Contents

1. [Authentication](#authentication)
2. [Customers](#customers)
3. [Qualification](#qualification)
4. [Interactions](#interactions)
5. [Reminders](#reminders)
6. [Events](#events)
7. [NBA (Next Best Action)](#nba-next-best-action)
8. [Error Responses](#error-responses)

---

## Authentication

**Currently:** No authentication required  
**Future:** Will implement JWT-based authentication

---

## Customers

### Get All Customers

**Endpoint:** `GET /customers`

**Query Parameters:**
- `status` (optional): Filter by pipeline status

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "555-1234",
    "status": "New Lead",
    "prospect_why": "Wants financial freedom",
    "created_at": "2025-10-02T00:00:00.000Z",
    "updated_at": "2025-10-02T00:00:00.000Z"
  }
]
```

**Example:**
```bash
curl http://localhost:3001/api/customers
curl http://localhost:3001/api/customers?status=Qualified
```

---

### Get Single Customer

**Endpoint:** `GET /customers/:id`

**Response:**
```json
{
  "id": "uuid",
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "555-1234",
  "status": "Qualified",
  "prospect_why": "Wants financial freedom",
  "qualification_data": {...},
  "created_at": "2025-10-02T00:00:00.000Z",
  "updated_at": "2025-10-02T00:00:00.000Z"
}
```

**Example:**
```bash
curl http://localhost:3001/api/customers/956680d4-cbd7-4efc-b68d-bc65e05c8bb5
```

---

### Create Customer

**Endpoint:** `POST /customers`

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "555-1234",
  "status": "New Lead",
  "source": "ig",
  "notes": "Met at conference"
}
```

**Required Fields:**
- `name` (string, min 1 character)

**Optional Fields:**
- `email` (string, valid email)
- `phone` (string)
- `status` (enum): One of:
  - "New Lead"
  - "Warming Up"
  - "Invited"
  - "Qualified"
  - "Presentation Sent"
  - "Follow-up"
  - "Closed - Won"
  - "Not Now"
  - "Long-term Nurture"
- `source` (enum): "ig", "messenger", "whatsapp", "web", "ads", "manual", "other"
- `notes` (string)
- `prospect_why` (string) - **Required for "Qualified" status**

**Response:**
```json
{
  "id": "uuid",
  "name": "John Doe",
  "email": "john@example.com",
  "status": "New Lead",
  "created_at": "2025-10-02T00:00:00.000Z"
}
```

**Example:**
```bash
curl -X POST http://localhost:3001/api/customers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "555-1234",
    "status": "New Lead"
  }'
```

---

### Update Customer

**Endpoint:** `PUT /customers/:id`

**Request Body:** Same as Create Customer (all fields optional)

**Frazer Method Rule:** If updating status to "Qualified", `prospect_why` is required

**Response:** Updated customer object

**Example:**
```bash
curl -X PUT http://localhost:3001/api/customers/uuid \
  -H "Content-Type: application/json" \
  -d '{
    "status": "Qualified",
    "prospect_why": "Wants to retire early and travel"
  }'
```

---

### Delete Customer

**Endpoint:** `DELETE /customers/:id`

**Response:** 204 No Content

**Example:**
```bash
curl -X DELETE http://localhost:3001/api/customers/uuid
```

---

### Move Customer to Next Stage

**Endpoint:** `POST /customers/:id/next-stage`

**Description:** Automatically moves customer to the next pipeline stage and schedules follow-up

**Response:** Updated customer object

**Example:**
```bash
curl -X POST http://localhost:3001/api/customers/uuid/next-stage
```

**Note:** This automatically triggers follow-up scheduling via the Follow-up Service

---

### Get Pipeline Stats

**Endpoint:** `GET /customers/stats/pipeline`

**Response:**
```json
{
  "counts_by_status": {
    "New Lead": 5,
    "Qualified": 3,
    "Closed - Won": 2
  },
  "dmo_today": 10,
  "dmo_week": 45
}
```

**Example:**
```bash
curl http://localhost:3001/api/customers/stats/pipeline
```

---

## Qualification

### Save Qualification

**Endpoint:** `POST /qualification`

**Request Body:**
```json
{
  "customer_id": "uuid",
  "prospect_why": "Wants financial freedom to spend time with family",
  "qualification_data": {
    "goals": "Retire in 5 years",
    "timeline": "Ready to start immediately",
    "budget": "Willing to invest $500/month",
    "decision_maker": "Makes own decisions",
    "pain_points": "Stuck in 9-5 job, no time freedom",
    "current_situation": "Working full-time, looking for side income"
  }
}
```

**Required Fields:**
- `customer_id` (string, UUID)

**Optional Fields:**
- `prospect_why` (string) - Core motivation
- `qualification_data` (object) - Structured qualification information

**Response:**
```json
{
  "success": true,
  "message": "Qualification saved successfully"
}
```

**Example:**
```bash
curl -X POST http://localhost:3001/api/qualification \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "uuid",
    "prospect_why": "Financial freedom",
    "qualification_data": {
      "goals": "Retire early",
      "timeline": "1-2 years"
    }
  }'
```

---

### Get Qualification

**Endpoint:** `GET /qualification/:id`

**Response:**
```json
{
  "id": "uuid",
  "name": "John Doe",
  "prospect_why": "Financial freedom",
  "qualification_data": {
    "goals": "Retire early",
    "timeline": "1-2 years",
    "budget": "Moderate investment",
    "decision_maker": "Yes"
  }
}
```

**Example:**
```bash
curl http://localhost:3001/api/qualification/uuid
```

---

## Interactions

### Get All Interactions

**Endpoint:** `GET /interactions`

**Query Parameters:**
- `customer_id` (optional): Filter by customer

**Response:** Array of interaction objects

**Example:**
```bash
curl http://localhost:3001/api/interactions
curl http://localhost:3001/api/interactions?customer_id=uuid
```

---

### Create Interaction

**Endpoint:** `POST /interactions`

**Request Body:**
```json
{
  "customer_id": "uuid",
  "type": "call",
  "notes": "Had great conversation about opportunity",
  "outcome": "positive"
}
```

**Example:**
```bash
curl -X POST http://localhost:3001/api/interactions \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "uuid",
    "type": "call",
    "notes": "Follow-up call scheduled"
  }'
```

---

## Reminders

### Get All Reminders

**Endpoint:** `GET /reminders`

**Query Parameters:**
- `customer_id` (optional): Filter by customer
- `completed` (optional): Filter by completion status (0 or 1)

**Response:** Array of reminder objects

**Example:**
```bash
curl http://localhost:3001/api/reminders
curl http://localhost:3001/api/reminders?completed=0
```

---

### Create Reminder

**Endpoint:** `POST /reminders`

**Request Body:**
```json
{
  "customer_id": "uuid",
  "type": "follow_up",
  "message": "Call to check on decision",
  "scheduled_for": "2025-10-05T14:00:00.000Z"
}
```

**Example:**
```bash
curl -X POST http://localhost:3001/api/reminders \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "uuid",
    "type": "follow_up",
    "message": "Follow up on presentation",
    "scheduled_for": "2025-10-05T14:00:00.000Z"
  }'
```

---

### Mark Reminder Complete

**Endpoint:** `PUT /reminders/:id/complete`

**Response:** Updated reminder object

**Example:**
```bash
curl -X PUT http://localhost:3001/api/reminders/uuid/complete
```

---

## Events

### Get All Events

**Endpoint:** `GET /events`

**Query Parameters:**
- `customer_id` (optional): Filter by customer
- `type` (optional): Filter by event type

**Response:** Array of event objects

**Example:**
```bash
curl http://localhost:3001/api/events
curl http://localhost:3001/api/events?customer_id=uuid
```

---

### Create Event

**Endpoint:** `POST /events`

**Request Body:**
```json
{
  "customer_id": "uuid",
  "type": "stage_change",
  "description": "Moved to Qualified stage",
  "metadata": {}
}
```

**Example:**
```bash
curl -X POST http://localhost:3001/api/events \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "uuid",
    "type": "stage_change",
    "description": "Customer qualified"
  }'
```

---

## NBA (Next Best Action)

### Get Next Best Action

**Endpoint:** `GET /nba/:customer_id`

**Description:** Returns AI-powered recommendation for the next best action to take with this customer

**Response:**
```json
{
  "customer_id": "uuid",
  "recommendation": "Schedule follow-up call",
  "reasoning": "Customer showed interest but needs more information",
  "priority": "high",
  "suggested_date": "2025-10-05"
}
```

**Example:**
```bash
curl http://localhost:3001/api/nba/uuid
```

**Note:** Requires Python Worker (port 8000) to be running

---

## Error Responses

### Standard Error Format

```json
{
  "error": "Error message",
  "details": [...]
}
```

### Common HTTP Status Codes

- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `204 No Content` - Successful deletion
- `400 Bad Request` - Invalid request data
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

### Validation Errors

```json
{
  "error": "Invalid payload",
  "details": [
    {
      "message": "\"name\" is required",
      "path": ["name"],
      "type": "any.required"
    }
  ]
}
```

---

## Frazer Method Pipeline Stages

The system enforces the Frazer Method pipeline:

1. **New Lead** → Initial contact
2. **Warming Up** → Building relationship
3. **Invited** → Invited to learn more
4. **Qualified** → Understands their WHY (requires `prospect_why`)
5. **Presentation Sent** → Received full presentation
6. **Follow-up** → Nurturing decision process
7. **Closed - Won** → Joined the opportunity
8. **Not Now** → Not ready at this time
9. **Long-term Nurture** → Future potential

### Automatic Follow-ups

When a customer moves to a new stage, the system automatically schedules a follow-up:

- **New Lead:** 1 day
- **Qualified:** 3 days
- **Presentation:** 7 days
- **Follow-up:** 14 days
- **Closed:** 30 days

---

## Rate Limiting

**Currently:** No rate limiting  
**Future:** 100 requests per minute per IP

---

## Support

For API support or questions:
- Check the GitHub repository
- Review the test report (TEST_REPORT.md)
- Contact the development team

---

**Documentation maintained by:** Manus #2  
**Last tested:** 2025-10-02
