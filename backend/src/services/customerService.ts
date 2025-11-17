import DatabaseManager from '../database';
import { Customer, PipelineStatus } from '../types';
import { v4 as uuidv4 } from 'uuid';
import { EventLogService } from './eventLogService';
import { PipelineValidationService } from './pipelineValidationService';
import { ReminderService } from './reminderService';
import { interactionService } from './interactionService';
import { FrazerStageDefinition, getStageDefinition } from './frazerStageConfig';

export class CustomerService {
  private eventLogService: EventLogService;
  private pipelineValidationService: PipelineValidationService;
  private reminderService: ReminderService;

  constructor() {
    this.eventLogService = new EventLogService();
    this.pipelineValidationService = new PipelineValidationService();
    this.reminderService = new ReminderService();
  }

  async getAllCustomers(filters: { 
    status?: PipelineStatus; 
    search?: string; 
    source?: string; 
    country?: string; 
    language?: string; 
    next_action?: string; 
    sortBy?: string; 
    sortOrder?: 'ASC' | 'DESC'; 
  } = {}): Promise<Customer[]> {
    const db = DatabaseManager.getInstance().getDb();
    let query = 'SELECT * FROM customers WHERE 1=1';
    const params: any[] = [];

    if (filters.status) {
      query += ' AND status = ?';
      params.push(filters.status);
    }
    if (filters.source) {
      query += ' AND source = ?';
      params.push(filters.source);
    }
    if (filters.country) {
      query += ' AND country = ?';
      params.push(filters.country);
    }
    if (filters.language) {
      query += ' AND language = ?';
      params.push(filters.language);
    }
    if (filters.next_action) {
      query += ' AND next_action = ?';
      params.push(filters.next_action);
    }
    if (filters.search) {
      const searchTerm = `%${filters.search}%`;
      query += ' AND (name LIKE ? OR email LIKE ? OR phone LIKE ? OR notes LIKE ?)';
      params.push(searchTerm, searchTerm, searchTerm, searchTerm);
    }

    const sortBy = filters.sortBy || 'updated_at';
    const sortOrder = filters.sortOrder || 'DESC';
    query += ` ORDER BY ${sortBy} ${sortOrder}`;
    
    return new Promise((resolve, reject) => {
      db.all(query, params, (err, rows: any[]) => {
        if (err) {
          reject(err);
        } else {
          const customers = rows.map(row => ({
            ...row,
            created_at: new Date(row.created_at),
            updated_at: new Date(row.updated_at),
            next_action_date: row.next_action_date ? new Date(row.next_action_date) : undefined,
            consent_json: row.consent_json ? JSON.parse(row.consent_json) : undefined,
            utm_json: row.utm_json ? JSON.parse(row.utm_json) : undefined
          }));
          resolve(customers);
        }
      });
    });
  }

  async getCustomerById(id: string): Promise<Customer | null> {
    const db = DatabaseManager.getInstance().getDb();
    
    return new Promise((resolve, reject) => {
      db.get("SELECT * FROM customers WHERE id = ?", [id], (err, row: any) => {
        if (err) {
          reject(err);
        } else if (!row) {
          resolve(null);
        } else {
          const customer = {
            ...row,
            created_at: new Date(row.created_at),
            updated_at: new Date(row.created_at),
            next_action_date: row.next_action_date ? new Date(row.next_action_date) : undefined,
            consent_json: row.consent_json ? JSON.parse(row.consent_json) : undefined,
            utm_json: row.utm_json ? JSON.parse(row.utm_json) : undefined
          };
          resolve(customer);
        }
      });
    });
  }

  async createCustomer(customerData: Omit<Customer, 'id' | 'created_at' | 'updated_at'>): Promise<Customer> {
    const db = DatabaseManager.getInstance().getDb();
    const id = uuidv4();
    const now = new Date();

    const status = customerData.status || PipelineStatus.NEW_LEAD;
    const stageDefinition = getStageDefinition(status);
    const defaultNextAction = this.getNextActionForStage(stageDefinition);

    const customer: Customer = {
      id,
      ...customerData,
      status,
      next_action: customerData.next_action || defaultNextAction.action,
      next_action_date: customerData.next_action_date || defaultNextAction.date,
      created_at: now,
      updated_at: now
    };

    return new Promise((resolve, reject) => {
      const stmt = db.prepare(`
        INSERT INTO customers (
          id, name, email, phone, status, notes, next_action, next_action_date,
          created_at, updated_at, source, handle_ig, handle_whatsapp, country, language,
          consent_json, utm_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      `);

      stmt.run([
        customer.id,
        customer.name,
        customer.email,
        customer.phone,
        customer.status,
        customer.notes,
        customer.next_action,
        customer.next_action_date?.toISOString(),
        customer.created_at.toISOString(),
        customer.updated_at.toISOString(),
        (customerData as any).source || null,
        (customerData as any).handle_ig || null,
        (customerData as any).handle_whatsapp || null,
        (customerData as any).country || null,
        (customerData as any).language || null,
        (customerData as any).consent_json ? JSON.stringify((customerData as any).consent_json) : null,
        (customerData as any).utm_json ? JSON.stringify((customerData as any).utm_json) : null
      ], (err) => {
        if (err) {
          reject(err);
        } else {
          // Log event
          this.eventLogService.logEvent('customer_created', {
            customer_id: customer.id,
            name: customer.name,
            status: customer.status,
            frazer_step: stageDefinition.frazerStep
          }, customer.id);

          this.reminderService.scheduleStageReminder(customer.id, customer.status, {
            context: 'New profile intake',
            skipIfExists: true
          }).catch((reminderError) => {
            console.warn('Failed to schedule initial Frazer reminder', reminderError);
          });

          resolve(customer);
        }
      });

      stmt.finalize();
    });
  }

  async updateCustomer(id: string, updates: Partial<Customer>): Promise<Customer | null> {
    const existingCustomer = await this.getCustomerById(id);
    if (!existingCustomer) {
      return null;
    }

    const db = DatabaseManager.getInstance().getDb();
    const updatedAt = new Date();
    const updatedCustomer: Customer = {
      ...existingCustomer,
      ...updates,
      updated_at: updatedAt
    };
    const stageChanged = Boolean(updates.status && updates.status !== existingCustomer.status);
    let stageDefinition: FrazerStageDefinition | null = null;

    if (stageChanged && updates.status) {
      stageDefinition = getStageDefinition(updates.status);
      const validationResult = await this.pipelineValidationService.validateStageTransition(
        id,
        existingCustomer.status,
        updates.status
      );

      if (!validationResult.allowed) {
        throw new Error(validationResult.reason || 'Stage transition not allowed');
      }

      const nextAction = this.getNextActionForStage(stageDefinition);
      updatedCustomer.next_action = nextAction.action;
      updatedCustomer.next_action_date = nextAction.date;
    } else {
      updatedCustomer.next_action = updates.next_action ?? existingCustomer.next_action;
      updatedCustomer.next_action_date = updates.next_action_date ?? existingCustomer.next_action_date;
    }

    const hoursInPreviousStage = (updatedAt.getTime() - existingCustomer.updated_at.getTime()) / (1000 * 60 * 60);

    return new Promise((resolve, reject) => {
      const stmt = db.prepare(`
        UPDATE customers
        SET name = ?, email = ?, phone = ?, status = ?, notes = ?, next_action = ?, next_action_date = ?, updated_at = ?,
            source = ?, handle_ig = ?, handle_whatsapp = ?, country = ?, language = ?,
            consent_json = ?, utm_json = ?
        WHERE id = ?
      `);

      stmt.run([
        updatedCustomer.name,
        updatedCustomer.email,
        updatedCustomer.phone,
        updatedCustomer.status,
        updatedCustomer.notes,
        updatedCustomer.next_action,
        updatedCustomer.next_action_date?.toISOString(),
        updatedCustomer.updated_at.toISOString(),
        (updates as any).source ?? (existingCustomer as any).source ?? null,
        (updates as any).handle_ig ?? (existingCustomer as any).handle_ig ?? null,
        (updates as any).handle_whatsapp ?? (existingCustomer as any).handle_whatsapp ?? null,
        (updates as any).country ?? (existingCustomer as any).country ?? null,
        (updates as any).language ?? (existingCustomer as any).language ?? null,
        (updates as any).consent_json ? JSON.stringify((updates as any).consent_json) : (existingCustomer as any).consent_json ? JSON.stringify((existingCustomer as any).consent_json) : null,
        (updates as any).utm_json ? JSON.stringify((updates as any).utm_json) : (existingCustomer as any).utm_json ? JSON.stringify((existingCustomer as any).utm_json) : null,
        id
      ], async (err) => {
        if (err) {
          reject(err);
        } else {
          try {
            if (stageChanged && updates.status && stageDefinition) {
              await this.pipelineValidationService.logStageTransition(id, existingCustomer.status, updates.status);
              await this.handleStageTransition(updatedCustomer, existingCustomer.status, updates.status, hoursInPreviousStage, stageDefinition);
            }

            if (stageChanged && updates.status) {
              await this.eventLogService.logEvent('status_changed', {
                customer_id: id,
                old_status: existingCustomer.status,
                new_status: updates.status,
                frazer_step: stageDefinition?.frazerStep
              }, id);
            }
          } catch (transitionError) {
            return reject(transitionError);
          }

          resolve(updatedCustomer);
        }
      });

      stmt.finalize();
    });
  }

  async deleteCustomer(id: string): Promise<boolean> {
    const db = DatabaseManager.getInstance().getDb();
    
    return new Promise((resolve, reject) => {
      db.run('DELETE FROM customers WHERE id = ?', [id], function(err) {
        if (err) {
          reject(err);
        } else {
          resolve(this.changes > 0);
        }
      });
    });
  }

  async getCustomersByStatus(status: PipelineStatus): Promise<Customer[]> {
    const db = DatabaseManager.getInstance().getDb();
    
    return new Promise((resolve, reject) => {
      db.all('SELECT * FROM customers WHERE status = ? ORDER BY updated_at DESC', [status], (err, rows: any[]) => {
        if (err) {
          reject(err);
        } else {
          const customers = rows.map(row => ({
            ...row,
            created_at: new Date(row.created_at),
            updated_at: new Date(row.updated_at),
            next_action_date: row.next_action_date ? new Date(row.next_action_date) : undefined
          }));
          resolve(customers);
        }
      });
    });
  }

  async moveCustomerToNextStage(id: string): Promise<Customer | null> {
    const customer = await this.getCustomerById(id);
    if (!customer) {
      return null;
    }

    const nextValidStages = this.pipelineValidationService.getNextValidStages(customer.status);
    
    if (nextValidStages.length === 0) {
      return customer; // Already at final stage or no valid next stages
    }

    // Get the first valid next stage (main pipeline progression)
    const nextStatus = nextValidStages[0];

    // Validate the transition
    const validationResult = await this.pipelineValidationService.validateStageTransition(
      id,
      customer.status,
      nextStatus
    );

    if (!validationResult.allowed) {
      throw new Error(validationResult.reason || 'Stage transition not allowed');
    }

    return this.updateCustomer(id, { status: nextStatus });
  }

  /**
   * Move customer to a specific stage with validation
   */
  async moveCustomerToStage(id: string, targetStage: PipelineStatus): Promise<Customer | null> {
    const customer = await this.getCustomerById(id);
    if (!customer) {
      return null;
    }

    // Validate the transition
    const validationResult = await this.pipelineValidationService.validateStageTransition(
      id,
      customer.status,
      targetStage
    );

    if (!validationResult.allowed) {
      throw new Error(validationResult.reason || 'Stage transition not allowed');
    }

    return this.updateCustomer(id, { status: targetStage });
  }

  /**
   * Get stage recommendations for a customer
   */
  async getStageRecommendations(id: string): Promise<{
    recommended_stage: PipelineStatus;
    confidence: number;
    reasoning: string[];
  } | null> {
    const customer = await this.getCustomerById(id);
    if (!customer) {
      return null;
    }

    return this.pipelineValidationService.getStageRecommendations(id, customer.status);
  }

  private getNextActionForStage(stageDefinition: FrazerStageDefinition): { action: string; date: Date } {
    const action = `${stageDefinition.frazerStep}: ${stageDefinition.touchpoint.summary}`;
    const date = new Date(Date.now() + stageDefinition.cadenceHours * 60 * 60 * 1000);
    return { action, date };
  }

  private buildAIScoringPayload(stageDefinition: FrazerStageDefinition, hoursInPreviousStage: number, activityScore: number) {
    const expectedHours = stageDefinition.cadenceHours || 1;
    const cadenceRatio = Math.max(0, 1 - (hoursInPreviousStage / expectedHours));
    const normalizedActivity = activityScore / 100;
    const score = Math.round(40 + (cadenceRatio * 40) + (normalizedActivity * 20));
    const risk_level = hoursInPreviousStage > expectedHours ? 'at_risk' : 'healthy';
    return {
      score: Math.min(100, Math.max(0, score)),
      risk_level,
      signals: stageDefinition.aiSignals
    };
  }

  private async handleStageTransition(
    customer: Customer,
    previousStage: PipelineStatus,
    nextStage: PipelineStatus,
    hoursInPreviousStage: number,
    stageDefinition: FrazerStageDefinition
  ): Promise<void> {
    const activitySnapshot = await interactionService.getActivityScore(customer.id, stageDefinition.cadenceHours);

    await interactionService.logFrazerTouchpoint(customer.id, nextStage, {
      summaryOverride: `Stage change: ${previousStage} → ${nextStage}`,
      notes: `${stageDefinition.touchpoint.notesHint} | ${activitySnapshot.recommendedAction}`
    });

    await this.reminderService.scheduleStageReminder(customer.id, nextStage, {
      cadenceHours: stageDefinition.cadenceHours,
      context: `Next ${stageDefinition.frazerStep} touchpoint`,
      skipIfExists: true
    });

    const aiScore = this.buildAIScoringPayload(stageDefinition, hoursInPreviousStage, activitySnapshot.score);

    await this.eventLogService.logEvent('frazer_stage_transition', {
      customer_id: customer.id,
      from_stage: previousStage,
      to_stage: nextStage,
      frazer_step: stageDefinition.frazerStep,
      cadence_hours: stageDefinition.cadenceHours,
      ai_score: aiScore.score,
      ai_signals: aiScore.signals,
      risk_level: aiScore.risk_level,
      activity_score: activitySnapshot.score,
      touches_in_cadence: activitySnapshot.touches
    }, customer.id);
  }
}
