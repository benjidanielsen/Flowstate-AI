import { Request, Response } from 'express';
import axios from 'axios';

function getWorkerBase(): string {
  return process.env.PYTHON_WORKER_URL || 'http://localhost:8000';
}

export class NBAController {
  getRecommendations = async (req: Request, res: Response) => {
    try {
      const base = getWorkerBase();
      const { customer_id, limit } = req.query;
      const response = await axios.get(`${base}/nba`, { params: { customer_id, limit } });
      res.json(response.data);
    } catch (err: any) {
      const status = err?.response?.status || 500;
      console.error('NBA proxy error:', err?.message || err);
      res.status(status).json({ error: 'Failed to fetch NBA', details: err?.response?.data });
    }
  };

  analyze = async (_req: Request, res: Response) => {
    try {
      const base = getWorkerBase();
      const response = await axios.post(`${base}/nba/analyze`);
      res.json(response.data);
    } catch (err: any) {
      const status = err?.response?.status || 500;
      console.error('NBA analyze proxy error:', err?.message || err);
      res.status(status).json({ error: 'Failed to analyze NBA', details: err?.response?.data });
    }
  };
}

