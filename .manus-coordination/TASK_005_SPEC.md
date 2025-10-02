# TASK-005: Write API Documentation

## Objective
Document all API endpoints for developers

## File to Create
API_DOCUMENTATION.md

## Structure
```markdown
# FlowState-AI API Documentation

## Base URL
http://localhost:3001/api

## Authentication
(None currently - add if needed)

## Endpoints

### Customers

#### GET /customers
Returns all customers
Response: Array of customer objects

#### POST /customers
Create new customer
Body: {name, email, phone, pipeline_status}
Response: Created customer object

#### PUT /customers/:id
Update customer
Body: Customer fields to update
Response: Updated customer object

#### POST /customers/:id/next-stage
Move customer to next pipeline stage
Response: Updated customer

### Interactions
(Document all interaction endpoints)

### Reminders
(Document all reminder endpoints)

### Events
(Document all event endpoints)

### NBA (Next Best Action)
(Document NBA endpoints)

## Error Responses
(Document error formats)

## Examples
(Provide curl examples for each endpoint)
```

## Done When
- All endpoints documented
- Examples provided
- Error responses documented
- Easy to understand

GRAB IT!
