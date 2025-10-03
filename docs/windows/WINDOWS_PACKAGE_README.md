# FlowState-AI Windows Package

**Complete Windows-optimized startup package for FlowState-AI CRM**

---

## 📦 Package Contents

This package contains everything you need to run FlowState-AI on Windows with zero manual configuration.

### Installation & Setup Scripts

| File | Purpose | When to Use |
|------|---------|-------------|
| **INSTALL_WINDOWS.bat** | Complete automated installer | Run this FIRST before anything else |
| **CHECK_SYSTEM_WINDOWS.bat** | System health checker | When something isn't working right |
| **FIX_EVERYTHING_WINDOWS.bat** | Automatic repair tool | When you need to fix issues automatically |

### Startup & Shutdown Scripts

| File | Purpose | When to Use |
|------|---------|-------------|
| **START_FLOWSTATE_WINDOWS.bat** | One-click startup (Batch) | Daily use - easiest method |
| **START_FLOWSTATE_WINDOWS.ps1** | One-click startup (PowerShell) | Alternative if .bat doesn't work |
| **STOP_FLOWSTATE_WINDOWS.bat** | One-click shutdown | When you're done for the day |
| **STATUS_DASHBOARD_WINDOWS.bat** | Live status monitor | To see what's running in real-time |

### Documentation

| File | Purpose | When to Read |
|------|---------|--------------|
| **README_WINDOWS.md** | Main Windows guide | Start here! |
| **WINDOWS_SETUP_GUIDE.md** | Detailed setup with troubleshooting | If you have problems |
| **WINDOWS_PACKAGE_README.md** | This file - package overview | To understand what's included |
| **QUICK_START_GUIDE.md** | User guide for the CRM | After system is running |
| **SYSTEM_STATUS_REPORT.md** | Technical system information | For advanced users |

---

## 🚀 Getting Started (3 Steps)

### Step 1: Prerequisites

Install these if you don't have them:

- **Python 3.11+** from https://www.python.org/downloads/
  - ⚠️ CHECK "Add Python to PATH" during installation!
  
- **Node.js LTS** from https://nodejs.org/
  - Just use default settings

### Step 2: Run the Installer

1. Double-click **`INSTALL_WINDOWS.bat`**
2. Wait 2-5 minutes for it to complete
3. Desktop shortcuts will be created automatically

### Step 3: Start the System

1. Double-click **"Start FlowState-AI"** on your desktop
   - OR run **`START_FLOWSTATE_WINDOWS.bat`**
2. Wait 10-15 seconds for services to start
3. Your browser will open automatically

**Done!** You're now running FlowState-AI.

---

## 🎯 Daily Workflow

### Starting Your Day
1. Double-click "Start FlowState-AI" on your desktop
2. Wait for browser to open to dashboard
3. Start managing your network marketing business

### During the Day
- Access Frontend: http://localhost:3000
- Access Dashboard: http://localhost:3333
- Access API: http://localhost:3001/api

### Ending Your Day
1. Double-click "Stop FlowState-AI" on your desktop
2. All services will shut down cleanly

---

## 🔧 Troubleshooting Workflow

### Something Not Working?

**Level 1: Quick Check**
- Run **`CHECK_SYSTEM_WINDOWS.bat`**
- This diagnoses the problem

**Level 2: Automatic Fix**
- Run **`FIX_EVERYTHING_WINDOWS.bat`**
- This fixes 90% of issues

**Level 3: Manual Fix**
- Read **`WINDOWS_SETUP_GUIDE.md`**
- Find your specific issue and solution

**Level 4: Clean Reinstall**
1. Run **`FIX_EVERYTHING_WINDOWS.bat`**
2. Choose "Yes" to reset database
3. Restart computer
4. Run **`INSTALL_WINDOWS.bat`** again

---

## 📊 What Each Script Does

### INSTALL_WINDOWS.bat
**Purpose:** Complete system installation

**What it does:**
- Checks if Python and Node.js are installed
- Installs all Python packages (Flask, FastAPI, etc.)
- Installs all Node.js packages (backend & frontend)
- Builds the frontend for production
- Creates necessary directories
- Creates desktop shortcuts
- Offers to start the system

**When to run:**
- First time setup
- After updating from GitHub
- After major changes

### START_FLOWSTATE_WINDOWS.bat
**Purpose:** Start all system services

**What it does:**
- Checks prerequisites
- Installs missing dependencies
- Builds frontend if needed
- Starts Manus Sync Engine
- Starts Godmode Dashboard
- Starts Backend API
- Starts Frontend Server
- Opens dashboard in browser

**When to run:**
- Every time you want to use the system
- Daily startup

### STOP_FLOWSTATE_WINDOWS.bat
**Purpose:** Stop all system services

**What it does:**
- Kills all Python processes (Sync Engine, Dashboard, Frontend Server)
- Kills all Node.js processes (Backend API)
- Cleans up processes on ports 3000, 3001, 3333

**When to run:**
- When you're done using the system
- Before shutting down your computer
- Before running updates

### CHECK_SYSTEM_WINDOWS.bat
**Purpose:** Diagnose system health

**What it checks:**
- Python installation
- Node.js installation
- npm installation
- Python packages
- Node.js packages (root, backend, frontend)
- Frontend build status
- Running services

**When to run:**
- When something isn't working
- Before asking for help
- After making changes

### FIX_EVERYTHING_WINDOWS.bat
**Purpose:** Automatic repair

**What it does:**
- Stops all services
- Clears temporary files and caches
- Reinstalls all Python packages
- Reinstalls all Node.js packages
- Rebuilds frontend from scratch
- Optionally resets database
- Offers to start the system

**When to run:**
- When CHECK_SYSTEM finds issues
- After failed updates
- When services won't start
- When you get weird errors

### STATUS_DASHBOARD_WINDOWS.bat
**Purpose:** Real-time status monitoring

**What it shows:**
- Python and Node.js installation status
- Which services are running
- Process IDs for each service
- Quick action menu

**Features:**
- Auto-refreshes every 5 seconds
- Quick start/stop buttons
- Opens browser to frontend/dashboard
- Runs health check

**When to run:**
- To monitor system status
- To see if services are running
- For quick access to common actions

---

## 🎓 Understanding the System

### The Four Components

**1. Manus Sync Engine** (Background Process)
- Coordinates multiple AI agents
- Handles task assignment
- Manages conflict resolution
- Monitors system health

**2. Godmode Dashboard** (Port 3333)
- Real-time AI agent monitoring
- Shows what each agent is doing
- Progress bars and metrics
- WebSocket live updates

**3. Backend API** (Port 3001)
- TypeScript/Express server
- Handles business logic
- Manages database (SQLite)
- Provides REST API

**4. Frontend** (Port 3000)
- React web interface
- Customer management
- Frazer Method pipeline
- Interaction tracking

### How They Work Together

```
Frontend (3000) → Backend API (3001) → Database
                       ↑
                       |
Godmode Dashboard (3333) monitors AI Agents
                       ↑
                       |
Manus Sync Engine coordinates everything
```

All four components need to be running for the system to work properly.

---

## 💡 Pro Tips

### For Best Performance
- Close other programs using ports 3000, 3001, or 3333
- Have at least 2GB free RAM
- Use Chrome or Microsoft Edge browser
- Don't close the background service windows

### For Reliability
- Always use STOP script before shutting down Windows
- Run CHECK_SYSTEM after Windows updates
- Keep Python and Node.js updated
- Pull from GitHub regularly for updates

### For Troubleshooting
- Check logs first (in `logs/` folder)
- Run CHECK_SYSTEM before asking for help
- Try FIX_EVERYTHING before manual fixes
- Take screenshots of error messages

### For Development
- Use VSCode for editing code
- Backend changes require restart
- Frontend changes require rebuild
- Database changes may require reset

---

## 🆘 Common Issues & Solutions

### "Python is not recognized"
**Solution:** Reinstall Python, CHECK "Add Python to PATH", restart computer

### "Node is not recognized"
**Solution:** Reinstall Node.js with defaults, restart computer

### "Port already in use"
**Solution:** Run STOP script, restart computer, try again

### "Services start but nothing loads"
**Solution:** Wait 15-20 seconds, check Windows Firewall, try 127.0.0.1 instead of localhost

### "Frontend build failed"
**Solution:** Run FIX_EVERYTHING script

### "Backend won't start"
**Solution:** Run FIX_EVERYTHING script

### "Dashboard shows no agents"
**Solution:** Wait 30 seconds for agents to register, refresh browser

---

## 📚 Additional Resources

### In This Package
- All scripts have built-in help and error messages
- All documentation files are in Markdown format
- Logs are stored in `logs/` and component directories

### Online Resources
- GitHub Repository: https://github.com/benjidanielsen/Flowstate-AI
- Issues: Report problems on GitHub Issues
- Updates: Pull from GitHub regularly

---

## 🎉 You're All Set!

This Windows package makes FlowState-AI setup completely painless:

✅ **One-click installation** - INSTALL_WINDOWS.bat does everything  
✅ **One-click startup** - Desktop shortcut or START script  
✅ **One-click shutdown** - Desktop shortcut or STOP script  
✅ **Automatic diagnostics** - CHECK_SYSTEM finds problems  
✅ **Automatic repair** - FIX_EVERYTHING fixes problems  
✅ **Live monitoring** - STATUS_DASHBOARD shows real-time status  
✅ **Complete documentation** - Guides for every scenario  

**No Copilot needed. No manual configuration. Just working software.**

---

## 📝 Version Information

**Package Version:** 1.0  
**Created:** October 2025  
**Platform:** Windows 10/11  
**Python Required:** 3.11+  
**Node.js Required:** 18+ LTS  

---

**Built by Manus AI**

*The AI assistant that builds complete, working systems - not just code snippets.*

---

## 🔄 Updating This Package

To get the latest version:

```bash
cd C:\Path\To\Flowstate-AI
git pull
```

Then run `INSTALL_WINDOWS.bat` to update dependencies.

---

**Questions? Issues? Need help?**

Check `WINDOWS_SETUP_GUIDE.md` for detailed troubleshooting, or run `CHECK_SYSTEM_WINDOWS.bat` to diagnose problems automatically.
