# 🏫 School Server Deployment Guide

This guide explains how to deploy the Musinsa AI Studio app to your school server.

## 1. Transfer Files
You need to copy the project files to your server.
You can use `scp` (if you have SSH access) or just drag-and-drop if you use VS Code Remote SSH.

**Folders to copy:**
- `backend/`
- `frontend/`
- `deploy/`

*(You can skip `node_modules`, `.next`, `.venv`, and `__pycache__` as they will be recreated).*

## 2. Environment Configuration
Create a `.env` file in the root directory (or export these variables in your shell) before running the script.

**Example `.env` content:**
```bash
# Public URL of your backend (School Server IP + Port 8000)
# If using SSH Tunneling to localhost, you can leave these as default (skip setting them).
export BASE_URL="http://localhost:8000"
export FRONTEND_URL="http://localhost:3000" 
```

## 3. Run Deployment Script
Navigate to the `deploy` folder and run the script:

```bash
cd deploy
bash start_server.sh
```

This script will:
1.  Create a Python virtual environment (`backend/venv`).
2.  Install Python dependencies.
3.  Start the **FastAPI Backend**.
4.  Install Node.js dependencies (`frontend/node_modules`).
5.  Build the **Next.js Frontend**.
6.  Start the **Next.js Server**.

## 4. Accessing the App

### Option A: SSH Tunneling (Recommended)
If your school server ports are blocked, run this on **your local computer**:
```bash
ssh -L 3000:localhost:3000 -L 8000:localhost:8000 <userid>@<school-server-ip>
```
Then open [http://localhost:3000](http://localhost:3000).

### Option B: Direct Access
If ports are open:
Open `http://<school-server-ip>:3000` in your browser.
