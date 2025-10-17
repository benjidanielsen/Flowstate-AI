"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.NBAController = void 0;
const axios_1 = __importDefault(require("axios"));
function getWorkerBase() {
    return process.env.PYTHON_WORKER_URL || 'http://localhost:8000';
}
class NBAController {
    constructor() {
        this.getRecommendations = async (req, res) => {
            try {
                const base = getWorkerBase();
                const { customer_id, limit } = req.query;
                const response = await axios_1.default.get(`${base}/nba`, { params: { customer_id, limit } });
                res.json(response.data);
            }
            catch (err) {
                const status = err?.response?.status || 500;
                console.error('NBA proxy error:', err?.message || err);
                res.status(status).json({ error: 'Failed to fetch NBA', details: err?.response?.data });
            }
        };
        this.analyze = async (_req, res) => {
            try {
                const base = getWorkerBase();
                const response = await axios_1.default.post(`${base}/nba/analyze`);
                res.json(response.data);
            }
            catch (err) {
                const status = err?.response?.status || 500;
                console.error('NBA analyze proxy error:', err?.message || err);
                res.status(status).json({ error: 'Failed to analyze NBA', details: err?.response?.data });
            }
        };
    }
}
exports.NBAController = NBAController;
//# sourceMappingURL=nbaController.js.map