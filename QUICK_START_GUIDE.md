# FlowState-AI Quick Start Guide

Welcome to your FlowState-AI CRM system! This guide will help you get started with the system that is now running in the Manus sandbox.

---

## 🚀 System is Live!

Your FlowState-AI system is currently operational with all core components running successfully. The system includes an enhanced AI coordination engine, a real-time monitoring dashboard, and a complete CRM backend with frontend interface.

---

## 📍 Access Points

### In Manus Sandbox (Current Environment)

The system is currently accessible at these URLs within the Manus sandbox:

- **Frontend Application:** http://169.254.0.21:3000
- **Backend API:** http://169.254.0.21:3001/api
- **Godmode AI Dashboard:** http://169.254.0.21:3333

### When Running Locally (Your Windows Machine)

Once you set this up on your local Windows machine, you'll access it at:

- **Frontend Application:** http://localhost:3000
- **Backend API:** http://localhost:3001/api
- **Godmode AI Dashboard:** http://localhost:3333

---

## 🎯 What's Running

The system consists of four main components working together:

### 1. Frontend (Port 3000)
The user interface built with React and Vite. This is where you'll interact with your CRM system, manage customers, track the Frazer Method pipeline, and view your network marketing activities.

### 2. Backend API (Port 3001)
The TypeScript/Express server that handles all business logic, database operations, and API endpoints. It manages customer data, interactions, events, reminders, and the Next Best Action recommendations.

### 3. Godmode Dashboard (Port 3333)
The AI monitoring dashboard that shows real-time activity of all AI agents working on your system. This dashboard displays which AI agents are active, what tasks they're performing, and their progress percentages.

### 4. Manus Sync Engine (Background)
The coordination system that enables multiple Manus AI instances to work together seamlessly. It handles task assignment, conflict resolution, and ensures all AI agents are synchronized.

---

## 🔧 How to Use the System

### Accessing the CRM

Navigate to the frontend URL (port 3000) in your web browser. You'll see the FlowState-AI CRM interface where you can:

- Add new leads and prospects
- Move contacts through the Frazer Method pipeline stages
- Track interactions and follow-ups
- View customer profiles and history
- Manage your network marketing activities

### Monitoring AI Agents

Open the Godmode Dashboard (port 3333) to see real-time AI activity. The dashboard displays:

- Number of active AI agents
- Current tasks each agent is performing
- Progress bars showing completion percentages
- System statistics and health metrics
- Real-time updates via WebSocket connections

### Using the API

The backend API is accessible at port 3001 with the following endpoints:

- `GET /api/customers` - List all customers
- `POST /api/customers` - Create a new customer
- `GET /api/customers/:id` - Get customer details
- `PUT /api/customers/:id` - Update customer information
- `DELETE /api/customers/:id` - Delete a customer
- `GET /api/interactions` - List interactions
- `GET /api/events` - List events
- `GET /api/reminders` - List reminders
- `GET /api/nba` - Get Next Best Action recommendations

---

## 📋 Next Steps

### Immediate Actions

**Test the System:** Open the frontend and explore the interface. Try adding a test customer and moving them through the pipeline stages.

**Monitor AI Activity:** Check the Godmode Dashboard to see which AI agents are active and what they're working on.

**Review the Database:** The SQLite database is located in `/home/ubuntu/Flowstate-AI/backend/data/` and contains all your CRM data.

### Development Priorities

**Implement Frazer Method Pipeline:** The system needs the complete Frazer Method pipeline stages implemented with proper workflow transitions. The stages should include New Lead, Warming Up, Invited, Qualified, Presentation Sent, Follow-up, Closed-Won, Not Now, and Long-term Nurture.

**Add Qualification Steps:** Implement mandatory qualification questions like "Prospect's WHY" to ensure proper lead qualification before moving to presentation stages.

**Enhance AI Agents:** Activate additional AI agents (Backend Developer, Frontend Developer, Database AI, etc.) to work autonomously on system improvements.

**Windows Optimization:** Create Windows-specific startup scripts and test the system on your Windows machine to ensure full compatibility.

---

## 🛠️ Stopping and Starting Services

### To Stop All Services

If you need to stop the system, you can terminate the processes:

```bash
# Find and stop processes
ps aux | grep -E "python3.11.*app_enhanced|python3.11.*MANUS_SYNC|python3.11.*http.server|node.*ts-node"

# Kill specific process by PID
kill <PID>
```

### To Start Services Again

**Start Manus Sync Engine:**
```bash
cd /home/ubuntu/Flowstate-AI
nohup python3.11 MANUS_SYNC_ENGINE_ENHANCED.py > manus_sync_engine.log 2>&1 &
```

**Start Godmode Dashboard:**
```bash
cd /home/ubuntu/Flowstate-AI/godmode-dashboard
nohup python3.11 app_enhanced.py > dashboard.log 2>&1 &
```

**Start Backend:**
```bash
cd /home/ubuntu/Flowstate-AI/backend
nohup npx ts-node src/index.ts > backend.log 2>&1 &
```

**Start Frontend:**
```bash
cd /home/ubuntu/Flowstate-AI/frontend/dist
nohup python3.11 -m http.server 3000 > frontend_server.log 2>&1 &
```

---

## 📊 Monitoring and Logs

All system logs are stored in their respective directories:

- **Sync Engine:** `/home/ubuntu/Flowstate-AI/manus_sync_engine.log`
- **Dashboard:** `/home/ubuntu/Flowstate-AI/godmode-dashboard/dashboard.log`
- **Backend:** `/home/ubuntu/Flowstate-AI/backend/backend.log`
- **Frontend:** `/home/ubuntu/Flowstate-AI/frontend/dist/frontend_server.log`

You can monitor logs in real-time using:

```bash
tail -f /home/ubuntu/Flowstate-AI/manus_sync_engine.log
```

---

## 🎓 Understanding the Frazer Method

The Frazer Method is a systematic approach to network marketing that focuses on relationship building and proper qualification. The pipeline stages are:

**New Lead:** Initial contact or referral received  
**Warming Up:** Building rapport and establishing trust  
**Invited:** Prospect invited to learn about the opportunity  
**Qualified:** Prospect has been properly qualified (WHY identified)  
**Presentation Sent:** Business presentation or materials shared  
**Follow-up:** Active follow-up and answering questions  
**Closed-Won:** Prospect has joined your team  
**Not Now:** Prospect not ready but interested for future  
**Long-term Nurture:** Maintaining relationship for future opportunities

Each stage requires specific actions and proper qualification before moving forward. The system is designed to enforce these best practices and ensure no shortcuts are taken in the relationship-building process.

---

## 🤝 Getting Help

If you encounter any issues or have questions:

**Check the System Status Report:** Review `SYSTEM_STATUS_REPORT.md` for detailed information about all running components.

**Review Logs:** Check the log files for error messages or warnings that might indicate issues.

**Monitor the Dashboard:** The Godmode Dashboard provides real-time system health information and AI agent activity.

**Consult Documentation:** Review the comprehensive documentation in the `docs/` directory for detailed information about system architecture and features.

---

## 🎉 You're Ready!

Your FlowState-AI system is operational and ready for use. The AI agents are coordinated and working together to continuously improve the system. Start by exploring the frontend interface and monitoring the AI dashboard to see the system in action.

Remember, this is a hands-free, AI-driven system designed to handle most development and operational tasks autonomously. Your role is primarily to provide strategic direction and make key decisions while the AI agents handle the implementation details.

**Happy networking!** 🚀

---

*Generated by Manus AI Assistant - October 1, 2025*
