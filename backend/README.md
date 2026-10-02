# Backend — Multi-Agent Business & Startup Strategy Advisor

FastAPI backend foundation for the Collaborative Multi-Agent Coordination System (PS-27).

## Requirements
- Python 3.10+
- Dependencies listed in `requirements.txt`

## Local Setup

1. **Navigate to the backend directory**:
   ```bash
   cd backend
   ```

2. **Create and activate a virtual environment**:
   - On Windows (PowerShell):
     ```powershell
     python -m venv .venv
     .venv\Scripts\Activate.ps1
     ```
   - On macOS/Linux:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Environment Variables**:
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

5. **Run the Development Server**:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

6. **Verify the Health Endpoint**:
   - Open browser or execute:
     ```bash
     curl http://localhost:8000/api/health
     ```
   - Expected response:
     ```json
     {
       "status": "ok",
       "service": "multi-agent-business-advisor"
     }
     ```
   - Interactive API docs: [http://localhost:8000/docs](http://localhost:8000/docs)
