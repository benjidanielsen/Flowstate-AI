import { jest } from '@jest/globals';

class RedisMock {
  private store = new Map<string, string>();

  constructor() {}

  on = jest.fn();

  async get(key: string) {
    return this.store.get(key) ?? null;
  }

  async setex(key: string, _ttl: number, value: string) {
    this.store.set(key, value);
  }

  async set(key: string, value: string) {
    this.store.set(key, value);
  }

  async del(key: string) {
    this.store.delete(key);
  }

  async exists(key: string) {
    return this.store.has(key) ? 1 : 0;
  }

  async quit() {
    this.store.clear();
  }
}

export default RedisMock;
