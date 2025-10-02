# TASK-001: Build Qualification API

## Objective
Create API endpoint for Frazer Method qualification questions

## Files to Create
- backend/src/controllers/qualificationController.ts
- backend/src/routes/qualification.ts

## Implementation

```typescript
// backend/src/controllers/qualificationController.ts
import { Request, Response } from 'express';
import { db } from '../database';

export class QualificationController {
  saveQualification = async (req: Request, res: Response) => {
    const { customer_id, prospect_why, qualification_data } = req.body;
    
    try {
      await db.run(
        'UPDATE customers SET prospect_why = ?, qualification_data = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
        [prospect_why, JSON.stringify(qualification_data), customer_id]
      );
      
      res.json({ success: true });
    } catch (error) {
      res.status(500).json({ error: 'Failed to save qualification' });
    }
  };
  
  getQualification = async (req: Request, res: Response) => {
    const { id } = req.params;
    
    try {
      const customer = await db.get('SELECT prospect_why, qualification_data FROM customers WHERE id = ?', [id]);
      res.json(customer);
    } catch (error) {
      res.status(500).json({ error: 'Failed to get qualification' });
    }
  };
}
```

## Register Route
Add to backend/src/routes/index.ts:
```typescript
import qualificationRoutes from './qualification';
router.use('/qualification', qualificationRoutes);
```

## Test
```bash
curl -X POST http://localhost:3001/api/qualification -H "Content-Type: application/json" -d '{"customer_id":"123","prospect_why":"wants freedom"}'
```

## Done When
- API endpoint works
- Data saves to database
- Returns proper responses
- Error handling added

GRAB THIS TASK NOW!
