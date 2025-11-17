# Backend - Flowstate-AI

Quick notes for local development and tests.

Start server (development):

1. Install dependencies from repo root or backend folder:

```powershell
cd backend
npm install
```

2. Start in dev mode (typescript watch):

```powershell
npm run dev
```

Run tests (with handle detection):

```powershell
npm run test -- --detectOpenHandles --runInBand
```

Notes:
- The server exports `createApp()`, `startServer()` and `shutdown()` in `src/index.ts` so tests can manage lifecycle without forcing process.exit.
- If you run the server directly (`node dist/index.js`), the process will attach SIGINT/SIGTERM handlers that call `shutdown()` and exit.
- Database access is configured via environment variables exposed by `backend/app/database.py`:
  - `BACKEND_DATABASE_URL` (preferred) or `DATABASE_URL` to point at Postgres or SQLite. Defaults to `sqlite:///./flowstate.db` for local work.
  - Optional pooling overrides for Postgres deployments: `BACKEND_DB_POOL_SIZE`, `BACKEND_DB_MAX_OVERFLOW`, `BACKEND_DB_POOL_TIMEOUT`, `BACKEND_DB_POOL_RECYCLE`.
  - The engine is created lazily so tests can safely monkeypatch the variables before importing the module.
