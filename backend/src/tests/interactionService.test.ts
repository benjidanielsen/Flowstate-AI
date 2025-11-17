import { interactionService } from '../services/interactionService';
import { CustomerService } from '../services/customerService';
import DatabaseManager from '../database';
import { runMigrations } from '../database/migrate';
import { InteractionType, PipelineStatus } from '../types';

const dbManager = DatabaseManager.getInstance();

describe('interactionService', () => {
  const customerService = new CustomerService();
  let customerId: string;

  beforeEach(async () => {
    await dbManager.connect();
    await resetDatabase();
    await runMigrations();
    const customer = await customerService.createCustomer({
      name: 'Interaction Demo',
      email: `frazer-int-${Date.now()}@example.com`,
      status: PipelineStatus.NEW_LEAD
    });
    customerId = customer.id;
  });

  afterEach(async () => {
    await dbManager.close();
  });

  it('creates and fetches interactions for a customer', async () => {
    const created = await interactionService.create({
      customer_id: customerId,
      type: InteractionType.CALL,
      summary: 'Initial connect call',
      notes: 'Talked through WHY and confirmed invite',
      interaction_date: new Date()
    });

    expect(created.id).toBeDefined();
    expect(created.customer_id).toBe(customerId);

    const interactions = await interactionService.getByCustomerId(customerId);
    expect(interactions.length).toBeGreaterThanOrEqual(1);
    expect(interactions[0].summary).toContain('Initial connect');
  });

  it('logs Frazer touchpoints and reports activity score', async () => {
    await interactionService.logFrazerTouchpoint(customerId, PipelineStatus.WARMING_UP);
    await interactionService.logFrazerTouchpoint(customerId, PipelineStatus.INVITED);

    const score = await interactionService.getActivityScore(customerId, 48);

    expect(score.touches).toBeGreaterThanOrEqual(2);
    expect(score.score).toBeGreaterThan(0);
    expect(score.recommendedAction.length).toBeGreaterThan(0);
  });
});

async function resetDatabase() {
  const db = dbManager.getDb();
  await new Promise<void>((resolve, reject) => {
    db.exec(
      'DROP TABLE IF EXISTS reminders; DROP TABLE IF EXISTS interactions; DROP TABLE IF EXISTS event_logs; DROP TABLE IF EXISTS customers;',
      (err) => {
        if (err) reject(err);
        else resolve();
      }
    );
  });
}
