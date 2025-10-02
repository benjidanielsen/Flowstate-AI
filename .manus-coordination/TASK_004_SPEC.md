# TASK-004: Test All Services

## Objective
Verify all system components work correctly

## Test Checklist

### Backend API (Port 3001)
```bash
# Health check
curl http://localhost:3001/api/health

# Get customers
curl http://localhost:3001/api/customers

# Create customer
curl -X POST http://localhost:3001/api/customers -H "Content-Type: application/json" -d '{"name":"Test","email":"test@test.com","phone":"123"}'

# Get reminders
curl http://localhost:3001/api/reminders

# NBA endpoint
curl http://localhost:3001/api/nba/123
```

### Frontend (Port 3000)
- Open http://localhost:3000
- Navigate to Dashboard
- Navigate to Customers page
- Try adding a customer
- Check if data appears

### Dashboard (Port 3333)
- Open http://localhost:3333
- Verify AI agent status shows
- Check system metrics
- Verify real-time updates

### Python Worker (Port 8000)
```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/nba -H "Content-Type: application/json" -d '{"customer_id":"123"}'
```

## Create Test Report
File: TEST_REPORT.md

Include:
- What works ✅
- What's broken ❌
- Performance notes
- Recommendations

## Done When
- All services tested
- Report created
- Issues documented
- Recommendations made

GRAB NOW!
