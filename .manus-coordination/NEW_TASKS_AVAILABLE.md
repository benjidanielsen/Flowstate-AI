# NEW TASKS AVAILABLE - GRAB IMMEDIATELY!

**Created by:** Manus #2
**Time:** 23:01 UTC
**Status:** AVAILABLE FOR ANY MANUS

---

## TASK-006: Fix Python Worker Port 8000
**Priority:** HIGH
**Estimated Time:** 20 minutes
**Assigned to:** AVAILABLE

**Description:**
Python worker process is running but port 8000 is not accessible. NBA (Next Best Action) features depend on this.

**Steps:**
1. Check python-worker/src/main.py
2. Verify uvicorn configuration
3. Check if port 8000 is bound correctly
4. Test endpoint: `curl http://localhost:8000/health`
5. Fix and restart service

**Success Criteria:**
- Python worker responds on port 8000
- Health endpoint returns 200 OK
- NBA endpoint works

---

## TASK-007: Create Seed Data Script
**Priority:** HIGH
**Estimated Time:** 30 minutes
**Assigned to:** AVAILABLE

**Description:**
Database is empty. Need sample data for testing Frazer Method pipeline.

**Requirements:**
- 10-15 sample customers
- Various pipeline stages
- Realistic names, emails, phones
- Some with qualification data
- Some with interactions
- Some with reminders

**Deliverable:**
- `backend/src/database/seed.ts`
- Script to populate database
- Can be run multiple times safely

---

## TASK-008: Browser Testing
**Priority:** MEDIUM
**Estimated Time:** 30 minutes
**Assigned to:** AVAILABLE

**Description:**
Test all features in actual browser, not just API.

**Test Cases:**
1. Dashboard loads correctly
2. Customer list displays
3. Create new customer
4. View customer detail
5. Qualification form works
6. Move customer through pipeline
7. Follow-ups schedule automatically
8. Reminders display

**Deliverable:**
- `BROWSER_TEST_REPORT.md`
- Screenshots of any issues
- List of bugs found

---

## TASK-009: Presentation Tracking
**Priority:** MEDIUM
**Estimated Time:** 40 minutes
**Assigned to:** AVAILABLE

**Description:**
Add ability to track presentations sent to prospects.

**Requirements:**
- Backend API endpoint
- Database schema for presentations
- Link presentations to customers
- Track: date sent, type, status (viewed/not viewed)
- Frontend UI to add/view presentations

**Files to Create:**
- `backend/src/controllers/presentationController.ts`
- `backend/src/routes/presentations.ts`
- `frontend/src/pages/Presentations.tsx`

---

## TASK-010: Outcome Logging
**Priority:** MEDIUM
**Estimated Time:** 30 minutes
**Assigned to:** AVAILABLE

**Description:**
Log outcomes when customers close (won/lost).

**Requirements:**
- Capture close date
- Capture outcome (won/lost/not now)
- Capture reason
- Capture notes
- Link to customer record

**Files to Modify:**
- `backend/src/controllers/customerController.ts`
- Add outcome fields to customer model

---

## HOW TO CLAIM A TASK

1. Edit this file
2. Change "AVAILABLE" to "CLAIMED-MANUS-X"
3. Create status file: `manus_X_status.json`
4. Start working immediately
5. Update status every 10 minutes
6. Mark complete when done

---

**MANUS #2 MONITORING - I SEE ALL ACTIVITY**
