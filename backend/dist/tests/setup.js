"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const database_1 = __importDefault(require("../database"));
beforeAll(async () => {
    // Setup test database
    process.env.DATABASE_URL = ':memory:';
});
afterAll(async () => {
    // Close database connections
    await database_1.default.getInstance().close();
});
beforeEach(() => {
    // Reset any mocks or test state
});
//# sourceMappingURL=setup.js.map