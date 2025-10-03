# FlowState-AI Windows Setup Guide

**Stop fighting with Copilot. This guide will get you running in 5 minutes.**

---

## 🎯 Quick Setup (For Impatient People)

1. **Install Prerequisites** (if you haven't already):
   - Python 3.11+: https://www.python.org/downloads/ (CHECK "Add Python to PATH")
   - Node.js LTS: https://nodejs.org/ (Just click Next, Next, Next)

2. **Clone the Repository** (if you haven't already):
   ```bash
   git clone https://github.com/benjidanielsen/Flowstate-AI.git
   cd Flowstate-AI
   ```

3. **Double-click this file:**
   - `START_FLOWSTATE_WINDOWS.bat`

4. **Done!** Your system will open in your browser automatically.

---

## 🚀 Detailed Setup (If Something Goes Wrong)

### Step 1: Install Python

1. Go to https://www.python.org/downloads/
2. Download Python 3.11 or newer
3. **IMPORTANT:** During installation, CHECK the box that says "Add Python to PATH"
4. Click "Install Now"
5. Wait for it to finish

**Verify Python is installed:**
Open Command Prompt (Win + R, type `cmd`, press Enter) and type:
```bash
python --version
```

You should see something like `Python 3.11.x`. If you get an error, Python is not in your PATH.

### Step 2: Install Node.js

1. Go to https://nodejs.org/
2. Download the LTS (Long Term Support) version
3. Run the installer
4. Just click "Next" through everything (default options are fine)
5. Wait for it to finish

**Verify Node.js is installed:**
In Command Prompt, type:
```bash
node --version
npm --version
```

You should see version numbers for both. If you get errors, restart your computer and try again.

### Step 3: Clone the Repository

If you haven't cloned the repository yet:

1. Open Command Prompt
2. Navigate to where you want the project (e.g., `cd C:\Users\YourName\Documents`)
3. Clone the repository:
   ```bash
   git clone https://github.com/benjidanielsen/Flowstate-AI.git
   cd Flowstate-AI
   ```

### Step 4: Run the Startup Script

**Option A: Using Batch File (Easiest)**
1. Navigate to the `Flowstate-AI` folder in File Explorer
2. Double-click `START_FLOWSTATE_WINDOWS.bat`
3. Wait 10-15 seconds
4. Your browser will open automatically to the dashboard

**Option B: Using PowerShell (Alternative)**
1. Right-click `START_FLOWSTATE_WINDOWS.ps1`
2. Select "Run with PowerShell"
3. If you get a security warning, type `Y` and press Enter
4. Wait 10-15 seconds
5. Your browser will open automatically to the dashboard

**Option C: Manual Command Line**
If both scripts fail, open Command Prompt in the `Flowstate-AI` folder and run:
```bash
START_FLOWSTATE_WINDOWS.bat
```

---

## 🛑 Stopping the System

**Option 1: Double-click this file:**
- `STOP_FLOWSTATE_WINDOWS.bat`

**Option 2: Close the windows manually:**
- Look for minimized windows titled "Manus Sync Engine", "Godmode Dashboard", "Backend API", and "Frontend Server"
- Close each one

**Option 3: Task Manager:**
1. Press Ctrl + Shift + Esc
2. Find Python and Node processes
3. Right-click → End Task

---

## 🔧 Troubleshooting

### "Python is not recognized as an internal or external command"

**Problem:** Python is not in your PATH.

**Solution:**
1. Uninstall Python
2. Reinstall Python from https://www.python.org/downloads/
3. **CHECK THE BOX** that says "Add Python to PATH" during installation
4. Restart your computer

### "Node is not recognized as an internal or external command"

**Problem:** Node.js is not in your PATH.

**Solution:**
1. Reinstall Node.js from https://nodejs.org/
2. Use the default installation options
3. Restart your computer

### "Port 3000 is already in use"

**Problem:** Another program is using port 3000, 3001, or 3333.

**Solution:**
1. Run `STOP_FLOWSTATE_WINDOWS.bat` to stop any existing services
2. Restart your computer
3. Try starting again

### "Frontend build failed"

**Problem:** Frontend dependencies are not installed or there's a build error.

**Solution:**
1. Open Command Prompt in the `Flowstate-AI` folder
2. Run these commands:
   ```bash
   cd frontend
   npm install
   npm run build
   cd ..
   ```
3. Try starting the system again

### "Backend won't start"

**Problem:** Backend dependencies are missing or there's a TypeScript error.

**Solution:**
1. Open Command Prompt in the `Flowstate-AI` folder
2. Run these commands:
   ```bash
   cd backend
   npm install
   cd ..
   ```
3. Try starting the system again

### "Nothing happens when I double-click the .bat file"

**Problem:** Windows security or antivirus is blocking the script.

**Solution:**
1. Right-click the .bat file
2. Select "Run as administrator"
3. If that doesn't work, open Command Prompt as administrator and run:
   ```bash
   cd C:\Path\To\Flowstate-AI
   START_FLOWSTATE_WINDOWS.bat
   ```

### "PowerShell script won't run"

**Problem:** PowerShell execution policy is blocking scripts.

**Solution:**
1. Open PowerShell as Administrator
2. Run this command:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```
3. Type `Y` and press Enter
4. Try running the script again

---

## 📍 Accessing Your System

Once the system is running, open your browser and go to:

- **Main Dashboard:** http://localhost:3333
- **CRM Frontend:** http://localhost:3000
- **API Backend:** http://localhost:3001/api

The dashboard (port 3333) is the best place to start. It shows you what all the AI agents are doing in real-time.

---

## 🎓 Using VSCode (Optional)

If you want to use VSCode to view or edit the code:

1. Install VSCode: https://code.visualstudio.com/
2. Open VSCode
3. File → Open Folder → Select the `Flowstate-AI` folder
4. Install recommended extensions (VSCode will prompt you)

**You don't need VSCode to run the system.** The startup scripts work without it.

---

## 💡 What Each Component Does

**Manus Sync Engine** - Coordinates multiple AI agents working together  
**Godmode Dashboard** - Shows you what AI agents are doing in real-time  
**Backend API** - Handles all the business logic and database  
**Frontend Server** - The web interface you interact with

All four components need to be running for the system to work properly.

---

## 🆘 Still Having Issues?

If you're still stuck after trying the troubleshooting steps:

1. **Check the logs:**
   - Look in the `logs` folder for error messages
   - Check `manus_sync_engine.log`
   - Check `godmode-dashboard/dashboard.log`
   - Check `backend/backend.log`

2. **Take a screenshot of the error message** and describe what you were trying to do

3. **Tell me:**
   - What version of Windows you're using
   - What version of Python you have (`python --version`)
   - What version of Node.js you have (`node --version`)
   - What error message you're seeing

I'll help you fix it. Unlike Copilot, I actually understand this system because I built it.

---

## 🎉 Success!

Once you see the Godmode Dashboard open in your browser, you're all set! The system is running and the AI agents are coordinating to improve it continuously.

**No more Copilot frustration. No more manual configuration. Just one click and you're running.**

---

*Created by Manus AI - The assistant that actually gets things done*
