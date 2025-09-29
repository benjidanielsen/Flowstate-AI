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
