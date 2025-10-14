# Flowstate-AI

Flowstate-AI is an AI-first, self-improving CRM-OS for network marketers and solo founders. It enforces the Frazer Method with a strict pipeline, automates follow-ups, tracks no-show and inactivity, and surfaces Next Best Actions (NBA). Built with React/Tailwind + Node/TypeScript and a Python AI worker, it learns from logs to get smarter with each iteration.

## 🚀 GODMODE Brain Launch Sequence

The "FlowState-AI GODMODE - Ultimate Autonomous AI Development System" now
ships with a single source of truth for bringing the platform online:

- **Roadmap:** `docs/GODMODE_BRAIN_ROADMAP.md` distills the four historical
  GODMODE planning docs into a nine-hour, three-phase playbook.
- **Checklist:** `docs/launch/FINAL_LAUNCH_CHECKLIST.md` turns the roadmap into
  claimable deliverables, readiness gates, and fast links for the launch team.
- **Automation:** `ai-gods/godmode_brain.py` keeps the roadmap JSON
  (`collective-memory/godmode_brain_plan.json`) and project status ledger in
  sync so autonomous agents or humans can execute the sequence instantly.
- **Validation:** `docs/launch/SYSTEM_VALIDATION.md` pairs with the
  one-command scripts in `scripts/unix` and `scripts/windows` to certify the
  stack before each launch milestone.
- **Command Board:** `AUTONOMOUS_WORK_LOG.md` contains the mandatory
  claim/complete task board. Update it before starting any task and include the
  deliverables once finished.

Advance phases or review progress with:

```bash
python ai-gods/godmode_brain.py --show-plan
python ai-gods/godmode_brain.py --set-phase phase_2_crm_delivery --mark-complete phase_1_ai_brain
```

This replaces the legacy Manus coordination stack; the best ideas from MACCS
now live inside the GODMODE Brain principles.

## Repository Layout

- `ai-gods/` – Automation brain, project manager, and resilience helpers.
- `backend/`, `frontend/`, `python-worker/` – Core FlowState-AI services.
- `docs/godmode/` – Canonical GODMODE knowledge base and historical plans.
- `docs/operations/` – Runbooks, status reports, and coordination rules.
- `docs/launch/` – Final launch checklist and nine-hour execution aides.
- `docs/windows/` – Pilot setup instructions and packaging guides for Windows.
- `docs/integrations/` – VS Code integration research and setup notes.
- `docs/reference/` – Architecture, API, and quick-start guides.
- `scripts/windows/`, `scripts/unix/` – Platform-specific launch scripts.
- `archive/` – Task history and packaged assets kept for reference only.

## Features

### 🎯 Frazer Pipeline Method
- **7-Stage Pipeline**: Lead → Relationship → Invited → Qualified → Presentation Sent → Follow-up → SIGNED-UP
- **Automated Stage Progression**: Smart recommendations for moving customers through the pipeline
- **Pipeline Analytics**: Visual dashboard showing distribution and conversion rates

### 👤 Customer Card System
- **Complete Customer Profiles**: Contact info, status, notes, and interaction history
- **Enhanced Customer Management**: Advanced filtering, searching, and sorting capabilities for customer data.
- **Interaction Tracking**: Log calls, emails, meetings, and notes with timestamps, with a dedicated UI for adding interactions.
- **Next Step Management**: Define and track next actions with due dates
- **Smart Recommendations**: AI-powered suggestions for next best actions

### 🔔 Intelligent Reminder System
- **Multi-Interval Reminders**: Support for flexible, recurring reminders with various intervals.
- **Automated Escalation**: Progressive reminder sequences based on customer status.
- **Comprehensive Management**: UI for creating, updating, and deleting reminders directly from customer profiles.
- **Smart Processing**: Python worker automatically processes due reminders.

### 🧠 Next Best Action (NBA) Engine
- **AI-Powered Recommendations**: Smart suggestions based on customer data and behavior
- **Priority Scoring**: Weighted recommendations with urgency indicators
- **Global & Customer-Specific**: Both overview and detailed individual recommendations

### 📊 Event Logging & Analytics
- **Comprehensive Event Log**: JSON-based logging of all customer interactions and system events.
- **Advanced Reporting & Analytics**: Dashboard includes customer demographics (by country, language, source), interaction summaries (by type, total, average per customer), and pipeline conversion rates.
- **Performance Tracking**: Monitor pipeline effectiveness and conversion metrics.
- **Data-Driven Insights**: Learn from historical data to improve recommendations.

### 🤖 AI Agent Self-Improvement
- **Iterative Feedback Loops**: Agents continuously refine their internal models and decision-making processes.
- **Self-Evaluation**: Agents assess their own performance against predefined goals, identifying areas for improvement.
- **Adaptive Learning**: Agents adjust strategies and parameters based on feedback and self-evaluation.
- **Automated Issue Creation**: Performance issues can automatically trigger GitHub issues for human or AI intervention.

### 🤝 GitHub Coordination for AI Agents
- **Centralized Task Management**: GitHub Issues serve as the primary mechanism for assigning and tracking tasks for AI agents.
- **Automated Workflows**: GitHub Actions automate repetitive tasks like testing, deployment, and issue triage.
- **Transparent Collaboration**: All agent activities, including code changes and task progress, are visible on GitHub.
- **Version Control**: Git is used for tracking changes to code, documentation, and configurations.

### 🤖 Autonomous Project Steward
- **Continuous Improvement**: Autonomous system that continuously improves the repository without user intervention
- **DISCOVER → PLAN → EXECUTE Loop**: Automated discovery of issues, prioritization, and fixes
- **Safety Rules**: Built-in safety checks prevent destructive operations, secret leaks, and resource abuse
- **Progress Tracking**: All changes documented in PROGRESS.md with rationale and impact
- **Smart Prioritization**: Tasks ranked by Impact ↑, Effort ↓, Risk ↓, Time ↓
- **Default Backlog**: Always has work to do - formatting, linting, testing, docs, dependencies

## Technology Stack

- **Frontend**: React 18 + TypeScript + Tailwind CSS + Vite
- **Backend**: Node.js + Express + TypeScript + SQLite (dev) / PostgreSQL (prod)
- **AI Worker**: Python + FastAPI for reminders and NBA processing
- **Monitoring Dashboard**: Python + Flask + Flask-SocketIO + SQLite
- **Database**: SQLite for development, PostgreSQL for production
- **Containerization**: Docker + Docker Compose
- **CI/CD**: GitHub Actions

## Quick Start

### Prerequisites
- Node.js 18+ 
- Python 3.11+
- Docker & Docker Compose (optional)
- Git
- GitHub CLI (for GitHub integration features)

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
   
   # For GitHub Integration, set your GitHub Token
   export GITHUB_TOKEN="<YOUR_GITHUB_TOKEN>" # Replace with your actual GitHub token or personal access token
   # On Windows, use: set GITHUB_TOKEN="<YOUR_GITHUB_TOKEN>" # Replace with your actual GitHub token or personal access token
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
   
   # Terminal 4 - Godmode Monitoring Dashboard (from Flowstate-AI/godmode-dashboard)
   cd godmode-dashboard && python app_enhanced.py
   ```

5. **Access Application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:3001/api
   - Python Worker: http://localhost:8000
   - Godmode Dashboard: http://localhost:3333
   - API Health: http://localhost:3001/api/health

6. **Optional: Start Autonomous Steward**
   ```bash
   # For continuous autonomous improvements
   ./START_AUTONOMOUS_STEWARD.sh
   
   # On Windows:
   START_AUTONOMOUS_STEWARD.bat
   
   # Monitor progress:
   tail -f PROGRESS.md
   ```

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

### Godmode Monitoring Dashboard
- `GET /` - Main dashboard page
- `GET /api/status` - API endpoint for current status
- `GET /api/ai/<ai_id>` - Get detailed info for specific AI

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
├── godmode-dashboard/       # AI Monitoring Dashboard (Python Flask)
│   ├── app_enhanced.py      # Main Flask application with SocketIO
│   ├── database.py          # SQLite database interactions
│   ├── self_improvement.py  # AI agent self-improvement logic
│   ├── github_integration.py# GitHub API integration for coordination
│   ├── static/              # CSS, JS, profile pictures
│   └── templates/           # HTML templates (dashboard.html)
├── .github/workflows/       # CI/CD pipelines
├── github_integration.py    # GitHub API integration (shared utility)
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
cd godmode-dashboard && python -m pytest # (if tests are implemented)
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
   - Set `GITHUB_TOKEN` for GitHub integration

2. **Database Migration**
   ```bash
   npm run db:migrate
   ```

3. **Docker Production Build**
   ```bash
   docker-compose -f docker-compose.yml up -d --profile production
   ```

## Cost-Free Operation and Windows Compatibility

The Flowstate-AI system is designed for cost-free operation, leveraging open-source technologies like Python, Flask, Flask-SocketIO, and SQLite. It is also fully compatible with Windows operating systems, with specific considerations for setup and environment configuration detailed in the `cost_free_windows_compatibility.md` document.

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run linting and tests: `npm run lint && npm test`
5. Commit your changes: `git commit -m 'Add feature'`
6. Push to branch: `git push origin feature-name`
7. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support, please open an issue on GitHub or contact [support@flowstate-ai.com](mailto:support@flowstate-ai.com).

---

Built with ❤️ for network marketers and solo founders who want to scale their relationships systematically.

