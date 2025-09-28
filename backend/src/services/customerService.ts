import DatabaseManager from '../database';
import { Customer, PipelineStatus } from '../types';
import { v4 as uuidv4 } from 'uuid';
import { EventLogService } from './eventLogService';

export class CustomerService {
  private eventLogService: EventLogService;

  constructor() {
    this.eventLogService = new EventLogService();
  }

  async getAllCustomers(): Promise<Customer[]> {
    const db = DatabaseManager.getInstance().getDb();
    
    return new Promise((resolve, reject) => {
      db.all('SELECT * FROM customers ORDER BY updated_at DESC', (err, rows: any[]) => {
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

  async getCustomerById(id: string): Promise<Customer | null> {
    const db = DatabaseManager.getInstance().getDb();
    
    return new Promise((resolve, reject) => {
      db.get('SELECT * FROM customers WHERE id = ?', [id], (err, row: any) => {
        if (err) {
          reject(err);
        } else if (!row) {
          resolve(null);
        } else {
          const customer = {
            ...row,
            created_at: new Date(row.created_at),
            updated_at: new Date(row.updated_at),
            next_action_date: row.next_action_date ? new Date(row.next_action_date) : undefined
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
        INSERT INTO customers (id, name, email, phone, status, notes, next_action, next_action_date, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
        customer.updated_at.toISOString()
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
        SET name = ?, email = ?, phone = ?, status = ?, notes = ?, next_action = ?, next_action_date = ?, updated_at = ?
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

    const stageOrder = [
      PipelineStatus.LEAD,
      PipelineStatus.RELATIONSHIP,
      PipelineStatus.INVITED,
      PipelineStatus.QUALIFIED,
      PipelineStatus.PRESENTATION_SENT,
      PipelineStatus.FOLLOW_UP,
      PipelineStatus.SIGNED_UP
    ];

    const currentIndex = stageOrder.indexOf(customer.status);
    if (currentIndex === -1 || currentIndex === stageOrder.length - 1) {
      return customer; // Already at final stage or invalid status
    }

    const nextStatus = stageOrder[currentIndex + 1];
    return this.updateCustomer(id, { status: nextStatus });
  }
}
