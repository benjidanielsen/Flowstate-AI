import { AsyncLocalStorage } from 'async_hooks';

interface CorrelationContext {
  correlationId?: string;
}

const storage = new AsyncLocalStorage<CorrelationContext>();

export const correlationContext = {
  runWithCorrelation<T>(correlationId: string, callback: () => T): T {
    return storage.run({ correlationId }, callback);
  },
  getCorrelationId(): string | undefined {
    return storage.getStore()?.correlationId;
  },
};

export default correlationContext;
