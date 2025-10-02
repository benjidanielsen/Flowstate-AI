# 🎯 TASKS FOR MANUS #1 - READY TO START

**Prepared by:** Manus #2 (Quality Enhancer)  
**Date:** 2025-10-02 22:50:00 UTC  
**Status:** READY - Start immediately when you confirm

---

## 📋 OVERVIEW

You're implementing the **Frazer Method CRM** features. I've reviewed all the code and prepared everything for you.

**Good news:** Most infrastructure exists. You're extending, not building from scratch.

**Total time:** ~2 hours  
**Tasks:** 3 main tasks, broken into subtasks  
**Support:** I'll review your code in real-time and help if blocked

---

## ✅ WHAT ALREADY EXISTS (You can reuse)

- Database schema with all Frazer fields
- AutomationService for event-driven automation
- ReminderService for scheduled follow-ups
- InteractionService for activity logging
- CustomerService for CRUD operations
- Frontend Layout and component patterns

**You're building on a solid foundation!**

---

## 🚀 TASK 1: QUALIFICATION API ENDPOINT

**Time:** 30 minutes  
**Priority:** HIGH - Everything else depends on this

### What to Build

**New file:** `backend/src/routes/frazer.ts`

**Endpoint:** `POST /api/prospects/:id/qualify`

**Request body:**
```json
{
  "prospect_why": "Their core motivation",
  "needs": ["list", "of", "needs"],
  "timeline": "When they want to start",
  "budget": "Budget range",
  "notes": "Additional qualification notes"
}
```

**Response:**
```json
{
  "success": true,
  "customer": { /* updated customer object */ },
  "next_action": "Schedule presentation",
  "follow_up_scheduled": "2025-10-03T10:00:00Z"
}
```

### Implementation Steps

1. **Create frazer.ts route file** (5 min)
   ```typescript
   import { Router } from 'express';
   import { FrazerController } from '../controllers/frazerController';
   
   const router = Router();
   const frazerController = new FrazerController();
   
   router.post('/prospects/:id/qualify', frazerController.qualifyProspect);
   
   export default router;
   ```

2. **Create frazerController.ts** (10 min)
   - Validate request body (use Joi like customerController)
   - Check prospect_why is provided
   - Update customer status to "Qualified"
   - Save qualification data
   - Log event
   - Create follow-up reminder (24h)
   - Return success response

3. **Register route in main app** (2 min)
   - Add to `backend/src/index.ts`
   - `app.use('/api', frazerRoutes);`

4. **Test locally** (13 min)
   - Use curl or Postman
   - Test valid qualification
   - Test missing prospect_why (should fail)
   - Test invalid customer ID
   - Verify reminder created

### Code Pattern to Follow

Look at: `backend/src/controllers/customerController.ts`  
- Same validation pattern
- Same error handling
- Same response format

### Success Criteria

- [ ] Endpoint accepts POST requests
- [ ] Validates prospect_why is required
- [ ] Updates customer status to "Qualified"
- [ ] Creates 24h follow-up reminder
- [ ] Logs qualification event
- [ ] Returns proper success/error responses
- [ ] No TypeScript errors
- [ ] Tested and working

### When Done

Update your status:
```json
{
  "status": "task_completed",
  "completed": ["Task 1: Qualification API"],
  "asking_for": "What's next?"
}
```

I'll review your code and assign Task 2.

---

## 🚀 TASK 2: FOLLOW-UP AUTOMATION SERVICE

**Time:** 30 minutes  
**Priority:** HIGH - Core Frazer Method feature  
**Dependencies:** Task 1 complete

### What to Build

**New file:** `backend/src/services/frazerAutomationService.ts`

**Purpose:** Automate follow-ups based on pipeline stage

### Stage-Based Follow-up Rules

```
New Lead → Warming Up: 2h follow-up
Warming Up → Invited: 24h follow-up
Invited → Qualified: 48h follow-up
Qualified → Presentation: 24h follow-up
Presentation → Follow-up: 2h, 24h, 48h sequence
Follow-up → Closed: 7d follow-up if no response
```

### Implementation Steps

1. **Create frazerAutomationService.ts** (15 min)
   ```typescript
   import { ReminderService } from './reminderService';
   import { CustomerService } from './customerService';
   
   export class FrazerAutomationService {
     private reminderService = new ReminderService();
     private customerService = new CustomerService();
     
     async handleStageChange(customerId: string, newStage: string) {
       // Create reminders based on stage
     }
     
     async getNextBestAction(customerId: string) {
       // Recommend next action based on stage and history
     }
   }
   ```

2. **Implement stage-based automation** (10 min)
   - Map each stage to follow-up times
   - Create reminders automatically
   - Use existing ReminderService

3. **Integrate with existing NBA system** (5 min)
   - NBA controller already exists at `backend/src/controllers/nbaController.ts`
   - Connects to Python worker (port 8000)
   - Just call the existing API: GET /api/nba?customer_id=xxx
   - No need to rebuild - already working!

### Code Pattern to Follow

Look at: `backend/src/services/automationService.ts`  
- Similar event handling
- Same reminder creation pattern
- Extend this pattern for Frazer stages

### Success Criteria

- [ ] Handles all Frazer Method stages
- [ ] Creates appropriate follow-up reminders
- [ ] Next Best Action returns relevant suggestions
- [ ] Integrates with existing ReminderService
- [ ] No TypeScript errors
- [ ] Tested with different stages

### When Done

Update your status and ask for Task 3.

---

## 🚀 TASK 3: FRONTEND INTEGRATION

**Time:** 30 minutes  
**Priority:** MEDIUM - Makes it usable  
**Dependencies:** Task 1 & 2 complete

### What to Build

**New file:** `frontend/src/components/QualificationForm.tsx`

**Purpose:** UI for qualifying prospects

### Implementation Steps

1. **Create QualificationForm component** (15 min)
   - Form with prospect_why textarea (required)
   - Needs checklist
   - Timeline dropdown
   - Budget input
   - Submit button
   - Error handling

2. **Add to CustomerDetail page** (5 min)
   - Show form when status is "Invited"
   - Hide after qualification
   - Show success message

3. **Display Next Best Action** (5 min)
   - Fetch from API
   - Show prominently on customer detail
   - Update after actions

4. **Test in browser** (5 min)
   - Qualify a prospect
   - Verify status changes
   - Check reminder created
   - Test validation

### Code Pattern to Follow

Look at: `frontend/src/pages/Customers.tsx`  
- Same API call pattern
- Same form handling
- Same error display

### Success Criteria

- [ ] Form validates prospect_why required
- [ ] Submits to qualification API
- [ ] Shows success/error messages
- [ ] Updates customer status in UI
- [ ] Next Best Action displays
- [ ] Responsive design
- [ ] No console errors

### When Done

Update your status:
```json
{
  "status": "all_tasks_completed",
  "completed": ["Task 1", "Task 2", "Task 3"],
  "message_to_manus_2": "Frazer Method complete! Ready for testing.",
  "message_to_manus_3": "Ready for Windows testing"
}
```

---

## 📞 COMMUNICATION WHILE WORKING

### Every 10 Minutes

Update `manus_1_status.json`:
```json
{
  "current_task": "Task 1: Building qualification API",
  "progress": "60%",
  "estimated_completion": "22:55:00"
}
```

### If Blocked

Create `BLOCKER_MANUS_1.md` immediately:
```markdown
# BLOCKER

**Task:** Task 1
**Issue:** TypeScript error on line 45
**Tried:** Checked types, still failing
**Need:** Help with type definition
```

I'll respond within 2 minutes.

### Between Tasks

Don't wait idle! While waiting for my response:
- Read the next task
- Review related code
- Plan your approach
- Check other Manus status

---

## 🎯 QUALITY STANDARDS

### Code Quality
- TypeScript strict mode compliant
- Proper error handling
- Input validation
- Consistent with existing code style

### Testing
- Test each endpoint manually
- Verify database updates
- Check reminder creation
- Test error cases

### Documentation
- Add comments for complex logic
- Document API endpoints
- Update README if needed

---

## 💡 TIPS FOR SUCCESS

1. **Start simple** - Get basic version working first
2. **Test frequently** - Don't wait until the end
3. **Reuse patterns** - Follow existing code style
4. **Ask early** - Don't struggle alone
5. **Commit often** - Small commits are easier to review
6. **Update status** - Keep me informed

---

## 🚀 READY TO START?

1. Create `MANUS_1_CONFIRMED.json`
2. Update `manus_1_status.json` with "Starting Task 1"
3. Begin coding!

I'm monitoring every 2 minutes and ready to help.

**Let's build this Frazer Method CRM!**

---

**Prepared by Manus #2**  
**All code patterns identified**  
**All dependencies mapped**  
**Ready for immediate start**
