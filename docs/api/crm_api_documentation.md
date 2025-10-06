# Flowstate-AI CRM API Documentation

Welcome to the comprehensive API documentation for the Flowstate-AI CRM endpoints. This document covers all available CRM-related API endpoints, including usage, request and response formats, authentication, and examples.

---

## Authentication

All CRM API endpoints require Bearer Token authentication. Include your API token in the `Authorization` header:

```
Authorization: Bearer YOUR_API_TOKEN
```


---

## Base URL

```
https://api.flowstate-ai.com/v1/crm
```


---

## Endpoints

### 1. Create a New Contact

```
POST /contacts
```

**Description:** Add a new contact to the CRM.

**Request Body:**

```json
{
  "first_name": "string",
  "last_name": "string",
  "email": "string",
  "phone": "string",
  "company": "string",
  "position": "string",
  "tags": ["string"]
}
```

**Response:**

```json
{
  "id": "string",
  "first_name": "string",
  "last_name": "string",
  "email": "string",
  "phone": "string",
  "company": "string",
  "position": "string",
  "tags": ["string"],
  "created_at": "ISO8601 timestamp",
  "updated_at": "ISO8601 timestamp"
}
```


---

### 2. Retrieve Contact by ID

```
GET /contacts/{contact_id}
```

**Description:** Retrieve detailed information of a contact by their unique ID.

**Response:**

```json
{
  "id": "string",
  "first_name": "string",
  "last_name": "string",
  "email": "string",
  "phone": "string",
  "company": "string",
  "position": "string",
  "tags": ["string"],
  "created_at": "ISO8601 timestamp",
  "updated_at": "ISO8601 timestamp"
}
```


---

### 3. Update Contact

```
PUT /contacts/{contact_id}
```

**Description:** Update details for an existing contact.

**Request Body:**

```json
{
  "first_name": "string",
  "last_name": "string",
  "email": "string",
  "phone": "string",
  "company": "string",
  "position": "string",
  "tags": ["string"]
}
```

**Response:**

```json
{
  "id": "string",
  "first_name": "string",
  "last_name": "string",
  "email": "string",
  "phone": "string",
  "company": "string",
  "position": "string",
  "tags": ["string"],
  "created_at": "ISO8601 timestamp",
  "updated_at": "ISO8601 timestamp"
}
```


---

### 4. Delete Contact

```
DELETE /contacts/{contact_id}
```

**Description:** Remove a contact from the CRM.

**Response:**

```json
{
  "message": "Contact deleted successfully"
}
```


---

### 5. List Contacts

```
GET /contacts
```

**Description:** Retrieve a paginated list of contacts.

**Query Parameters:**

- `page` (integer, optional, default=1): Page number
- `limit` (integer, optional, default=25): Number of contacts per page
- `search` (string, optional): Search term to filter contacts by name or email
- `tags` (string, optional): Comma-separated tags to filter contacts

**Response:**

```json
{
  "page": 1,
  "limit": 25,
  "total": 100,
  "contacts": [
    {
      "id": "string",
      "first_name": "string",
      "last_name": "string",
      "email": "string",
      "phone": "string",
      "company": "string",
      "position": "string",
      "tags": ["string"],
      "created_at": "ISO8601 timestamp",
      "updated_at": "ISO8601 timestamp"
    }
  ]
}
```


---

### 6. Add Note to Contact

```
POST /contacts/{contact_id}/notes
```

**Description:** Add a note to a contact.

**Request Body:**

```json
{
  "content": "string"
}
```

**Response:**

```json
{
  "note_id": "string",
  "contact_id": "string",
  "content": "string",
  "created_at": "ISO8601 timestamp",
  "updated_at": "ISO8601 timestamp"
}
```


---

### 7. List Notes for Contact

```
GET /contacts/{contact_id}/notes
```

**Description:** Retrieve all notes associated with a contact.

**Response:**

```json
[
  {
    "note_id": "string",
    "contact_id": "string",
    "content": "string",
    "created_at": "ISO8601 timestamp",
    "updated_at": "ISO8601 timestamp"
  }
]
```


---

### 8. Delete Note

```
DELETE /contacts/{contact_id}/notes/{note_id}
```

**Description:** Delete a specific note from a contact.

**Response:**

```json
{
  "message": "Note deleted successfully"
}
```


---

For questions or support, please contact Flowstate-AI developer support.

---

*End of CRM API documentation.*