# API Documentation

## Overview

The Flowstate-AI API provides programmatic access to all system functionality. The API follows REST principles with JSON request and response bodies.

## Base URL

```
Production: https://api.flowstate-ai.com/v1
Staging: https://staging-api.flowstate-ai.com/v1
Development: http://localhost:3001/api/v1
```

## Authentication

All API requests require authentication using JWT tokens passed in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

## API Endpoints

### Authentication
- `POST /auth/login` - Authenticate user and receive tokens
- `POST /auth/refresh` - Refresh access token
- `POST /auth/logout` - Invalidate refresh token

### Users
- `GET /users/me` - Get current user profile
- `PUT /users/me` - Update current user profile
- `GET /users/:id` - Get user by ID (admin only)

### Contacts
- `GET /contacts` - List all contacts
- `POST /contacts` - Create new contact
- `GET /contacts/:id` - Get contact by ID
- `PUT /contacts/:id` - Update contact
- `DELETE /contacts/:id` - Delete contact

### Interactions
- `GET /interactions` - List all interactions
- `POST /interactions` - Create new interaction
- `GET /interactions/:id` - Get interaction by ID

### AI Features
- `POST /ai/analyze` - Analyze text with AI
- `POST /ai/recommend` - Get AI recommendations
- `GET /ai/insights` - Get AI-generated insights

## Rate Limiting

API requests are rate limited to:
- 100 requests per minute for authenticated users
- 10 requests per minute for unauthenticated requests

## Error Handling

The API uses standard HTTP status codes:
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 429: Too Many Requests
- 500: Internal Server Error

Error responses include a JSON body with details:

```json
{
  "error": {
    "code": "INVALID_INPUT",
    "message": "Email address is required",
    "field": "email"
  }
}
```

## Webhooks

Flowstate-AI can send webhooks for various events. Configure webhooks in your account settings.

Supported events:
- `contact.created`
- `contact.updated`
- `interaction.created`
- `ai.insight.generated`

## SDK and Client Libraries

Official client libraries are available for:
- JavaScript/TypeScript
- Python
- Ruby (coming soon)

See [GitHub repository](https://github.com/benjidanielsen/Flowstate-AI) for installation instructions.

## Support

For API support, please contact support@flowstate-ai.com or open an issue on GitHub.
