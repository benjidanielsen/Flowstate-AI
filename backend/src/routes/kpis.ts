import { Router } from 'express';
import { authenticateToken } from '../middleware/authMiddleware';
import { safeLogger } from '../utils/piiRedaction';

const router = Router();

// Mock KPI data for demonstration
const mockKpis = {
  executive: [
    { name: 'Monthly Active Users', value: 4200, unit: '', change: 200, changeType: 'increase', description: 'Total unique users interacting with the system.', status: 'success' },
    { name: 'Customer Lifetime Value', value: 1250, unit: '$', change: 50, changeType: 'increase', description: 'Average revenue generated per customer.', status: 'success' },
    { name: 'Lead Conversion Rate', value: 15, unit: '%', change: 1, changeType: 'increase', description: 'Percentage of leads converted to customers.', status: 'success' },
    { name: 'Churn Rate', value: 2, unit: '%', change: 0.5, changeType: 'decrease', description: 'Percentage of customers lost over a period.', status: 'success' },
  ],
  operational: [
    { name: 'API Latency', value: 120, unit: 'ms', change: -10, changeType: 'decrease', description: 'Average response time for API requests.', status: 'success' },
    { name: 'System Uptime', value: 99.99, unit: '%', change: 0.01, changeType: 'increase', description: 'Percentage of time the system is operational.', status: 'success' },
    { name: 'Error Rate', value: 0.05, unit: '%', change: -0.01, changeType: 'decrease', description: 'Percentage of requests resulting in errors.', status: 'success' },
    { name: 'Database Query Time', value: 50, unit: 'ms', change: -5, changeType: 'decrease', description: 'Average time for database queries.', status: 'success' },
  ],
  business: [
    { name: 'Revenue Growth', value: 10, unit: '%', change: 2, changeType: 'increase', description: 'Quarterly revenue growth.', status: 'success' },
    { name: 'Customer Acquisition Cost', value: 150, unit: '$', change: -10, changeType: 'decrease', description: 'Cost to acquire a new customer.', status: 'success' },
    { name: 'ROI on AI Features', value: 25, unit: '%', change: 3, changeType: 'increase', description: 'Return on investment for AI-driven features.', status: 'success' },
  ],
  quality: [
    { name: 'Code Quality Score', value: 85, unit: '/100', change: 2, changeType: 'increase', description: 'Automated code quality assessment score.', status: 'success' },
    { name: 'Test Coverage', value: 80, unit: '%', change: 5, changeType: 'increase', description: 'Percentage of code covered by automated tests.', status: 'success' },
    { name: 'Bug Count (Critical)', value: 0, unit: '', change: 0, changeType: 'neutral', description: 'Number of critical bugs in production.', status: 'success' },
  ],
  learning: [
    { name: 'Automation Learning Rate', value: 0.8, unit: '', change: 0.1, changeType: 'increase', description: 'Rate at which AI improves its autonomous decision-making.', status: 'success' },
    { name: 'Edge Cases Handled', value: 50, unit: '', change: 5, changeType: 'increase', description: 'Number of unique edge cases autonomously identified and resolved.', status: 'success' },
    { name: 'Human Intervention Frequency', value: 10, unit: '/day', change: -2, changeType: 'decrease', description: 'Number of times human intervention was required per day.', status: 'success' },
  ],
};

router.get('/', authenticateToken, (req, res) => {
  const category = req.query.category as string;
  if (category && mockKpis[category as keyof typeof mockKpis]) {
    safeLogger.info(`Fetching KPIs for category: ${category}`);
    res.json(mockKpis[category as keyof typeof mockKpis]);
  } else {
    safeLogger.warn('Invalid or missing KPI category', { category });
    res.status(400).json({ error: 'Invalid or missing KPI category' });
  }
});

export default router;

