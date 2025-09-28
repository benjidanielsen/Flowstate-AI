# Flowstate-AI

Flowstate-AI is an AI-first, self-improving CRM-OS for network marketers and solo founders. It enforces the Frazer Method with a strict pipeline, automates follow-ups, tracks no-show and inactivity, and surfaces Next Best Actions (NBA). Built with React/Tailwind + Node/TypeScript and a Python AI worker, it learns from logs to get smarter with each iteration.

## Features

### 🎯 Frazer Pipeline Method
- **7-Stage Pipeline**: Lead → Relationship → Invited → Qualified → Presentation Sent → Follow-up → SIGNED-UP
- **Automated Stage Progression**: Smart recommendations for moving customers through the pipeline
- **Pipeline Analytics**: Visual dashboard showing distribution and conversion rates

### 👤 Customer Card System
- **Complete Customer Profiles**: Contact info, status, notes, and interaction history
- **Interaction Tracking**: Log calls, emails, meetings, and notes with timestamps
- **Next Step Management**: Define and track next actions with due dates
- **Smart Recommendations**: AI-powered suggestions for next best actions

### 🔔 Intelligent Reminder System
- **Multi-Interval Reminders**: 24h/48h, 2h/1d, and 7d follow-up schedules
- **Automated Escalation**: Progressive reminder sequences based on customer status
- **Smart Processing**: Python worker automatically processes due reminders

### 🧠 Next Best Action (NBA) Engine
- **AI-Powered Recommendations**: Smart suggestions based on customer data and behavior
- **Priority Scoring**: Weighted recommendations with urgency indicators
- **Global & Customer-Specific**: Both overview and detailed individual recommendations

### 📊 Event Logging & Analytics
- **Comprehensive Event Log**: JSON-based logging of all customer interactions and system events
- **Performance Tracking**: Monitor pipeline effectiveness and conversion metrics
- **Data-Driven Insights**: Learn from historical data to improve recommendations

## Technology Stack

- **Frontend**: React 18 + TypeScript + Tailwind CSS + Vite
- **Backend**: Node.js + Express + TypeScript + SQLite (dev) / PostgreSQL (prod)
- **AI Worker**: Python + FastAPI for reminders and NBA processing
- **Database**: SQLite for development, PostgreSQL for production
- **Containerization**: Docker + Docker Compose
- **CI/CD**: GitHub Actions

## Quick Start

### Prerequisites
- Node.js 18+ 
- Python 3.11+
- Docker & Docker Compose (optional)

### Option 1: Local Development

1. **Clone and Setup**
   ```bash
   git clone https://github.com/benjidanielsen/Flowstate-AI.git
   cd Flowstate-AI
   npm run setup  # Installs all dependencies
   ```

2. **Configure Environment**
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env with your configuration
   ```

3. **Initialize Database**
   ```bash
   npm run db:migrate  # Run database migrations
   npm run db:seed     # Seed with sample data
   ```

4. **Start Development Servers**
   ```bash
   npm run dev  # Starts all services concurrently
   ```

   Or start services individually:
   ```bash
   # Terminal 1 - Backend
   cd backend && npm run dev
   
   # Terminal 2 - Frontend  
   cd frontend && npm run dev
   
   # Terminal 3 - Python Worker
   cd python-worker && python -m uvicorn src.main:app --reload
   ```

5. **Access Application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:3001/api
   - Python Worker: http://localhost:8000
   - API Health: http://localhost:3001/api/health

### Option 2: Docker Compose

1. **Clone Repository**
   ```bash
   git clone https://github.com/benjidanielsen/Flowstate-AI.git
   cd Flowstate-AI
   ```

2. **Start with Docker Compose**
   ```bash
   docker-compose up -d
   ```

3. **Initialize Database**
   ```bash
   docker-compose exec backend npm run db:migrate
   docker-compose exec backend npm run db:seed
   ```

## API Endpoints

### Customers
- `GET /api/customers` - List all customers
- `GET /api/customers/:id` - Get customer details
- `POST /api/customers` - Create new customer
- `PUT /api/customers/:id` - Update customer
- `DELETE /api/customers/:id` - Delete customer
- `POST /api/customers/:id/next-stage` - Move to next pipeline stage
- `GET /api/customers/stats` - Get pipeline statistics

### Interactions
- `GET /api/interactions/customer/:id` - Get customer interactions
- `POST /api/interactions` - Create new interaction
- `PUT /api/interactions/:id` - Update interaction
- `DELETE /api/interactions/:id` - Delete interaction
- `GET /api/interactions/upcoming` - Get upcoming scheduled interactions

### Python Worker (NBA & Reminders)
- `GET /nba` - Get Next Best Action recommendations
- `POST /reminders` - Create reminder
- `GET /reminders/due` - Get due reminders
- `POST /reminders/process-due` - Process all due reminders

## Project Structure

```
Flowstate-AI/
├── backend/                 # Node.js/Express API
│   ├── src/
│   │   ├── controllers/     # Request handlers
│   │   ├── services/        # Business logic
│   │   ├── database/        # Database setup and migrations
│   │   ├── routes/          # API routes
│   │   ├── types/           # TypeScript types
│   │   └── tests/           # Unit tests
├── frontend/                # React application
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   ├── services/        # API client
│   │   └── types/           # TypeScript types
├── python-worker/           # AI worker service
│   ├── src/                 # FastAPI application
│   └── services/            # NBA and reminder services
├── .github/workflows/       # CI/CD pipelines
└── docker-compose.yml       # Container orchestration
```

## Development

### Testing
```bash
# Run all tests
npm test

# Individual service tests
npm run test:frontend
npm run test:backend
cd python-worker && python -m pytest
```

### Linting
```bash
# Lint all code
npm run lint

# Auto-fix issues
npm run lint:fix
```

### Building
```bash
# Build all services
npm run build

# Individual builds
npm run build:frontend
npm run build:backend
```

## Production Deployment

1. **Environment Variables**
   - Set `NODE_ENV=production`
   - Configure PostgreSQL connection
   - Set strong JWT secrets
   - Configure Python worker endpoints

2. **Database Migration**
   ```bash
   npm run db:migrate
   ```

3. **Docker Production Build**
   ```bash
   docker-compose -f docker-compose.yml up -d --profile production
   ```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run linting and tests: `npm run lint && npm test`
5. Commit your changes: `git commit -m 'Add feature'`
6. Push to branch: `git push origin feature-name`
7. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please open an issue on GitHub or contact [support@flowstate-ai.com](mailto:support@flowstate-ai.com).

---

Built with ❤️ for network marketers and solo founders who want to scale their relationships systematically.
