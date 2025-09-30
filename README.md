# FlowState-AI with GODMODE System

FlowState-AI is an AI-first, self-improving CRM-OS for network marketers and solo founders that enforces the Frazer Method with a strict pipeline, automates follow-ups, tracks no-show and inactivity, and surfaces Next Best Actions (NBA). Built with React/Tailwind + Node/TypeScript and a Python AI worker, it learns from logs to get smarter with each iteration.

**NEW:** The GODMODE System is a fully autonomous AI-driven development environment that handles the complete development lifecycle without human intervention, featuring 12 specialized AI agents working collaboratively.

## 🚀 Quick Start

### Prerequisites

Before running the system, ensure you have the following installed:

- **Python 3.11+** (with pip)
- **Node.js LTS** (with npm)
- **Git**

### GODMODE System Startup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/benjidanielsen/Flowstate-AI.git
   cd Flowstate-AI
   ```

2. **Start the GODMODE system:**

   **On Windows:**
   ```cmd
   # Using Command Prompt
   godmode_start.bat
   
   # Or using PowerShell
   .\godmode_start.ps1
   ```

   **On Linux/macOS:**
   ```bash
   python3 godmode_start.py
   ```

   **Note:** The `godmode_start.py` script now includes **pre-startup checks and automatic fixes** for common local environment issues, such as missing Python dependencies (psutil) and Node.js `node_modules`, and also runs database migrations. This ensures a smoother startup experience.

3. **Access the system:**
   - **GODMODE Dashboard:** http://localhost:3333
   - **Frontend:** http://localhost:3000
   - **Backend API:** http://localhost:3001
   - **AI Chat:** http://localhost:3333/chat

### Traditional Development Setup

For manual development without the GODMODE system:

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

## 🤖 GODMODE AI Agents

The GODMODE system includes 12 autonomous AI agents that work collaboratively:

| Agent | Responsibilities |
|-------|------------------|
| **Project Manager** | Orchestrates all development activities and coordinates AI agents |
| **Backend Developer** | TypeScript/Node.js backend development and API design |
| **Frontend Developer** | React/TypeScript frontend development and UI/UX |
| **Database AI** | Database design, optimization, and migration management |
| **Tester AI** | Automated testing, quality assurance, and performance validation |
| **Fixer AI** | Bug detection, code refactoring, and error resolution |
| **DevOps AI** | CI/CD, deployment, and GitHub automation |
| **Documentation AI** | Technical writing, API documentation, and knowledge base |
| **Support AI** | User support, troubleshooting, and feedback collection |
| **Innovation AI** | Idea generation, problem prediction, and strategic planning |
| **Communication Hub** | Inter-AI communication, voting, and conflict resolution |
| **Collective Memory** | Knowledge storage, retrieval, and cross-domain learning |

### AI Agent Features

- **Self-Naming:** Each AI agent assigns itself a human name for personality
- **First Week Learning:** Deep system analysis and optimization identification
- **Democratic Voting:** AI agents vote on major decisions and changes
- **GitHub Automation:** Automatic commits, branch management, and code reviews
- **Cross-Platform:** Works on Windows, Linux, and macOS
- **Real-Time Monitoring:** Live dashboard showing agent status and progress

## 🎯 FlowState-AI CRM Features

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

## 📊 GODMODE Dashboard Features

The GODMODE Dashboard provides real-time monitoring of:
- **Agent Status:** Current activity and progress for each AI agent
- **Task Progress:** Real-time progress bars (1-100%)
- **24-Hour Metrics:** Tasks completed and longest task durations
- **Learning Objectives:** First-week learning progress tracking
- **System Health:** Overall system status and performance
- **AI Chat Interface:** Direct communication with AI agents

## 🛠️ Technology Stack

### Core CRM System
- **Frontend**: React 18 + TypeScript + Tailwind CSS + Vite
- **Backend**: Node.js + Express + TypeScript + SQLite (dev) / PostgreSQL (prod)
- **AI Worker**: Python + FastAPI for reminders and NBA processing
- **Database**: SQLite for development, PostgreSQL for production

### GODMODE System
- **AI Agents**: Python 3.11+ with inter-process communication
- **Dashboard**: Flask + HTML/CSS/JavaScript
- **Process Management**: psutil for cross-platform compatibility
- **Communication**: JSON-based inter-agent messaging
- **Logging**: Comprehensive logging and reporting system

## API Endpoints

### CRM Endpoints
- `GET /api/customers` - List all customers
- `GET /api/customers/:id` - Get customer details
- `POST /api/customers` - Create new customer
- `PUT /api/customers/:id` - Update customer
- `DELETE /api/customers/:id` - Delete customer
- `POST /api/customers/:id/next-stage` - Move to next pipeline stage
- `GET /api/customers/stats` - Get pipeline statistics

### GODMODE Endpoints
- `GET /api/agent_status` - Get all AI agent statuses
- `POST /api/update_agent_status` - Update agent status (used by AI agents)
- `GET /chat` - AI chat interface

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
├── ai-gods/                 # GODMODE AI agent scripts
├── backend/                 # Node.js/Express API
│   ├── src/
│   │   ├── controllers/     # Request handlers
│   │   ├── services/        # Business logic
│   │   ├── database/        # Database setup and migrations
│   │   ├── routes/          # API routes
│   │   ├── types/           # TypeScript types
│   └── └── tests/           # Unit tests
├── frontend/                # React application
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   ├── services/        # API client
│   └── └── types/           # TypeScript types
├── godmode-dashboard/       # GODMODE monitoring dashboard
├── godmode-logs/           # AI agent logs and reports
├── python-worker/           # AI worker service
│   ├── src/                 # FastAPI application
│   └── services/            # NBA and reminder services
├── godmode_start.py        # Cross-platform startup script
├── godmode_start.bat       # Windows batch script
├── godmode_start.ps1       # Windows PowerShell script
├── .github/workflows/       # CI/CD pipelines
└── docker-compose.yml       # Container orchestration
```

## 🔧 Troubleshooting

### GODMODE System Issues

**Pre-startup checks and fixes:**
- The `godmode_start.py` script now automatically checks for and attempts to fix common environment issues like missing `psutil` (Python) and `node_modules` (Node.js backend/frontend) and runs database migrations. This significantly reduces manual setup and troubleshooting.

**AI Agent Robustness Tests:**
- The Project Manager AI has been tasked with two challenging problems to test the agents' robustness and error-handling:
    1.  **Non-existent Problem:** Investigate and resolve intermittent 'phantom packet loss' on a non-existent endpoint.
    2.  **Unfixable Problem:** Implement a fully sentient, self-aware AI agent.
- The agents are expected to either identify the non-existent nature of the first problem or gracefully handle the unfeasibility of the second, demonstrating their ability to reason and adapt.

**Python not found:**
- Ensure Python 3.11+ is installed and added to PATH
- On Windows, check "Add Python to PATH" during installation

**Node.js not found:**
- Install Node.js LTS from https://nodejs.org/
- Restart your terminal after installation

**Port conflicts:**
- Ensure ports 3000, 3001, and 3333 are available
- Kill any existing processes using these ports

**Permission errors (Windows):**
- Run Command Prompt or PowerShell as Administrator
- Ensure execution policy allows script execution: `Set-ExecutionPolicy RemoteSigned`

### Manual Component Startup

If the automatic scripts fail, you can start components manually:

1. **Start the GODMODE Dashboard:**
   ```bash
   cd godmode-dashboard
   python app.py
   ```

2. **Start the Backend:**
   ```bash
   cd backend
   npm install
   npm run start
   ```

3. **Start the Frontend:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Start AI Agents:**
   ```bash
   cd ai-gods
   python project-manager.py
   # ... start other agents as needed
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

## 🎮 GODMODE Commands

Once the GODMODE system is running, you can interact with it through:

- **View Dashboard:** Navigate to http://localhost:3333
- **Chat with AI:** Navigate to http://localhost:3333/chat
- **Check Logs:** Review files in `godmode-logs/` directory
- **Stop System:** Use Ctrl+C in the terminal running the startup script

## Contributing

This project now features both traditional development and AI-driven development:

### Traditional Contributing
1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run linting and tests: `npm run lint && npm test`
5. Commit your changes: `git commit -m \'Add feature\'`
6. Push to branch: `git push origin feature-name`
7. Submit a pull request

### GODMODE AI Contributing
The AI agents automatically review and potentially integrate contributions. They also continuously develop new features and improvements based on learning objectives and user feedback.

## License

This project is licensed under the MIT License.

## Support

For support:
1. Check the `godmode-logs/` directory for error logs
2. Review this README for troubleshooting steps
3. Use the AI Chat interface at http://localhost:3333/chat
4. Open an issue on GitHub
5. Contact [support@flowstate-ai.com](mailto:support@flowstate-ai.com).

---

**Built with ❤️ for network marketers and solo founders who want to scale their relationships systematically.**

**Enhanced with 🤖 GODMODE AI System for autonomous development and continuous improvement.**

