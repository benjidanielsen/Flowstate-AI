# TASK-002: Build Follow-up Automation Service

## Objective
Automate follow-ups based on Frazer Method pipeline stages

## File to Create
backend/src/services/followUpService.ts

## Implementation
```typescript
import { db } from '../database';

export class FollowUpService {
  async createFollowUp(customerId: string, stage: string) {
    const followUpTimes = {
      'new_lead': 1,           // 1 day
      'qualified': 3,          // 3 days
      'presentation': 7,       // 7 days
      'follow_up': 14,         // 14 days
      'closed': 30             // 30 days
    };
    
    const days = followUpTimes[stage] || 7;
    const scheduledFor = new Date();
    scheduledFor.setDate(scheduledFor.getDate() + days);
    
    await db.run(
      'INSERT INTO reminders (customer_id, type, message, scheduled_for) VALUES (?, ?, ?, ?)',
      [customerId, 'follow_up', `Follow up on ${stage}`, scheduledFor.toISOString()]
    );
  }
  
  async autoScheduleFollowUps() {
    const customers = await db.all('SELECT id, pipeline_status FROM customers WHERE pipeline_status != "closed"');
    
    for (const customer of customers) {
      await this.createFollowUp(customer.id, customer.pipeline_status);
    }
  }
}
```

## Integration
Add to backend/src/controllers/customerController.ts:
```typescript
import { FollowUpService } from '../services/followUpService';
const followUpService = new FollowUpService();

// In moveToNextStage method:
await followUpService.createFollowUp(id, newStatus);
```

## Test
```bash
curl -X POST http://localhost:3001/api/customers/123/next-stage
# Check reminders table for new follow-up
```

## Done When
- Service creates follow-ups automatically
- Integrated with pipeline moves
- Reminders appear in database
- Works for all stages

GRAB NOW!
