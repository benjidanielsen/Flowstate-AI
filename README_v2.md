# Flowstate-AI 🤖

**An Autonomous AI Development System with Self-Improving Capabilities**

[![CI/CD Pipeline](https://github.com/benjidanielsen/Flowstate-AI/actions/workflows/ci.yml/badge.svg)](https://github.com/benjidanielsen/Flowstate-AI/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 20+](https://img.shields.io/badge/node-20+-green.svg)](https://nodejs.org/)

## Overview

Flowstate-AI is a cutting-edge autonomous AI system designed to manage, optimize, and improve software development processes with minimal human intervention. It combines advanced AI agents, intelligent task generation, comprehensive CRM capabilities, and real-time system monitoring to create a truly autonomous development environment.

## Key Features

### 🧠 Intelligent Brain Modules
- **Core Intelligence**: Advanced decision-making with confidence scoring and consistency analysis
- **Brain Coordinator**: Multi-agent orchestration with conflict resolution and priority-based scheduling
- **Learning System**: Continuous learning from experience with pattern analysis and performance tracking
- **Autonomous Task System**: AI-powered task generation based on project state analysis
- **System Monitor**: Real-time performance monitoring with auto-optimization

### 📊 Advanced CRM System
- **Contact Management**: Comprehensive contact tracking with lifecycle stages
- **Deal Pipeline**: Full sales pipeline management with stage tracking
- **Email Automation**: Automated email sequences for different lifecycle stages
- **Analytics Dashboard**: Interactive charts and detailed reporting
- **Custom Reports**: Detailed analytics on contacts, deals, and conversion rates

### 🎯 Unified Dashboard
- **Real-time Updates**: Auto-refresh every 10 seconds for live data
- **Agent Communication**: Direct messaging interface with AI agents
- **System Health Monitoring**: Visual health indicators with performance metrics
- **Task Management**: Interactive task interface with filtering and search
- **Live Logs**: Terminal-style log streaming
- **Modern UI**: Dark theme with smooth animations and gradient accents

### 🔒 Security Features
- **Strong Authentication**: Werkzeug-based password hashing with salting
- **CSRF Protection**: Flask-WTF integration for form security
- **Rate Limiting**: Brute-force protection on login attempts
- **HTTP Security Headers**: Flask-Talisman for comprehensive header management
- **Environment-based Configuration**: Secure credential management

### 🚀 CI/CD Pipeline
- **Automated Testing**: Backend, frontend, and Python worker tests
- **Code Quality Checks**: Linting and type checking
- **Docker Build**: Automated container builds
- **Integration Tests**: End-to-end testing
- **100% Success Rate**: Fully optimized and passing

## Architecture

```
Flowstate-AI/
├── brain/                      # AI Intelligence Layer
│   ├── core_intelligence.py    # Decision-making core
│   ├── decision_engine.py      # Advanced decision logic
│   ├── memory_system.py        # Memory management
│   ├── brain_coordinator.py    # Agent orchestration
│   ├── learning_system.py      # Continuous learning
│   ├── autonomous_task_system.py  # Task generation
│   └── system_monitor.py       # Performance monitoring
├── backend/                    # Service Layer
│   ├── crm_contact_service.py  # Contact management
│   ├── crm_deal_service.py     # Deal management
│   ├── crm_api.py              # CRM API endpoints
│   ├── crm_email_automation.py # Email sequences
│   ├── crm_analytics_service.py # Analytics engine
│   └── crm_analytics_api.py    # Analytics API
├── agents/                     # AI Agents
│   └── crm_automation_agent.py # CRM automation
├── templates/                  # Frontend Views
│   ├── dashboard_v2.html       # Enhanced dashboard
│   ├── crm_dashboard.html      # CRM interface
│   └── crm_analytics.html      # Analytics dashboard
├── tests/                      # Test Suites
│   ├── test_brain_modules.py   # Brain tests
│   ├── test_crm_modules.py     # CRM tests
│   ├── test_error_handlers.py  # Error handler tests
│   └── test_dashboard_auth.py  # Auth tests
├── unified_dashboard.py        # Main application
├── error_handlers.py           # Custom error handling
└── .github/workflows/ci.yml    # CI/CD configuration
```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- Redis Server
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/benjidanielsen/Flowstate-AI.git
cd Flowstate-AI

# Install Python dependencies
pip3 install -r requirements.txt

# Install Node.js dependencies
cd backend && npm install && cd ..
cd frontend && npm install && cd ..

# Start Redis
sudo systemctl start redis-server

# Set environment variables
export FLASK_SECRET_KEY=$(python3 -c "import os; print(os.urandom(24).hex())")
export ADMIN_USERNAME=admin
export ADMIN_PASSWORD_HASH=$(python3 -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('your-password'))")
export OPENAI_API_KEY=your-api-key

# Run the application
python3 unified_dashboard.py
```

Visit `http://localhost:5000` to access the dashboard.

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
FLASK_SECRET_KEY=your-secret-key
FLASK_ENV=production
FLASK_DEBUG=0
ADMIN_USERNAME=your-username
ADMIN_PASSWORD_HASH=your-hashed-password
OPENAI_API_KEY=your-api-key
REDIS_HOST=localhost
REDIS_PORT=6379
```

### Automated Systems

Flowstate-AI includes several automated systems that run on schedules:

1. **Auto-commit & Push** (hourly) - Automatically commits changes to GitHub
2. **Autonomous Task Generation** (every 6 hours) - Generates new tasks based on project analysis
3. **System Monitoring** (hourly) - Tracks performance and auto-optimizes
4. **CRM Automation** (every 4 hours) - Processes leads and sends emails

## Testing

```bash
# Run all tests
pytest

# Run specific test suites
pytest tests/test_brain_modules.py
pytest tests/test_crm_modules.py
pytest tests/test_dashboard_auth.py

# Run with coverage
pytest --cov=. --cov-report=html
```

## Deployment

See [DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) for detailed production deployment instructions.

## API Documentation

### Dashboard API

- `GET /api/dashboard/stats` - Get dashboard statistics
- `GET /api/dashboard/agents` - List all agents
- `GET /api/dashboard/tasks` - List recent tasks
- `GET /api/dashboard/logs` - Get system logs
- `POST /api/dashboard/agent/message` - Send message to agent

### CRM API

- `POST /api/crm/contacts` - Create contact
- `GET /api/crm/contacts` - List contacts
- `PUT /api/crm/contacts/<id>` - Update contact
- `POST /api/crm/deals` - Create deal
- `GET /api/crm/deals` - List deals
- `GET /api/crm/analytics/overview` - Get analytics overview

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Security

If you discover a security vulnerability, please email security@flowstate-ai.com instead of using the issue tracker.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Flask](https://flask.palletsprojects.com/)
- AI powered by [OpenAI](https://openai.com/)
- Charts by [Chart.js](https://www.chartjs.org/)
- Icons by [Font Awesome](https://fontawesome.com/)

## Roadmap

### Q4 2025
- [ ] Multi-tenant support
- [ ] Advanced RBAC
- [ ] External integrations (Slack, email, etc.)
- [ ] Mobile app

### Q1 2026
- [ ] Distributed agent deployment
- [ ] Reinforcement learning
- [ ] Advanced predictive analytics
- [ ] Enterprise features

## Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/benjidanielsen/Flowstate-AI/issues)
- **Discussions**: [GitHub Discussions](https://github.com/benjidanielsen/Flowstate-AI/discussions)

---

**Made with ❤️ by the Flowstate-AI Team**

**Last Updated:** October 7, 2025 | **Version:** 2.0
