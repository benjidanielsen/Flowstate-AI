import DatabaseManager from '../database';
import { Customer, PipelineStatus } from '../types';
import { v4 as uuidv4 } from 'uuid';
import { EventLogService } from './eventLogService';
import { PipelineValidationService } from './pipelineValidationService';

export class CustomerService {
  private eventLogService: EventLogService;
  private pipelineValidationService: PipelineValidationService;

  constructor() {
    this.eventLogService = new EventLogService();
    this.pipelineValidationService = new PipelineValidationService();
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

    const customer: Customer = {
      id,
      ...customerData,
      status: customerData.status || PipelineStatus.LEAD,
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
            status: customer.status
          }, customer.id);

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
    const updatedCustomer = {
      ...existingCustomer,
      ...updates,
      updated_at: new Date()
    };

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
      ], (err) => {
        if (err) {
          reject(err);
        } else {
          // Log event if status changed
          if (updates.status && updates.status !== existingCustomer.status) {
            this.eventLogService.logEvent('status_changed', {
              customer_id: id,
              old_status: existingCustomer.status,
              new_status: updates.status
            }, id);
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

    // Log the transition
    await this.pipelineValidationService.logStageTransition(id, customer.status, nextStatus);

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

    // Log the transition
    await this.pipelineValidationService.logStageTransition(id, customer.status, targetStage);

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
}
