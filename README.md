# Multi-Agent Business & Startup Strategy Advisor

**Problem Statement 27 (PS-27): Collaborative Multi-Agent Coordination System**

---

## 1. Project Overview

The **Multi-Agent Business & Startup Strategy Advisor** is an autonomous, collaborative multi-agent decision support system designed to assist entrepreneurs and existing business leaders in validating and refining strategies.

The system targets two primary operational modes:
1. **Startup Idea Evaluation**: Feasibility analysis, market opportunity sizing, unit economics, risk assessment, and go-to-market strategy for new ventures.
2. **Existing Business Strategic Decision Support**: Expansion, pivoting, product-market realignment, operational restructuring, and competitive defense for operating businesses.

### Target Agent Architecture (10 Agents Planned)
- **7 Specialist Agents**:
  1. *Market Research Agent* — Industry trends, TAM/SAM/SOM, customer demographics
  2. *Financial Agent* — Financial modeling, burn rate, unit economics, revenue forecasts
  3. *Competition Agent* — Direct/indirect competitor analysis, moat evaluation
  4. *Customer Agent* — ICP profiling, pain points, customer journey analysis
  5. *Marketing & GTM Agent* — Acquisition channels, CAC, messaging, distribution strategy
  6. *Operations Agent* — Supply chain, tech stack, hiring needs, operational bottlenecks
  7. *Risk & Regulatory Agent* — Legal, regulatory compliance, operational risks, failure modes
- **3 Coordination & Governance Agents**:
  1. *Shared Goal & Consistency Agent* — Maintains strategic coherence across all agent outputs
  2. *Conflict Detection & Negotiation Agent* — Resolves conflicting recommendations between specialist agents
  3. *Orchestrator & Synthesis Agent* — Manages execution workflow and synthesizes final executive reports

---

## 2. Current Implementation Status

> **Step 1: Project Foundation (Completed)**
> - Full-stack monorepo scaffolded.
> - Minimal backend service created using FastAPI and Pydantic Settings with health endpoint (`GET /api/health`).
> - Minimal frontend application initialized using Next.js, React, TypeScript, and Tailwind CSS.
> - Strictly foundation only: No agent implementations, mock agents, LangGraph, databases, or vector stores have been added yet, per incremental development roadmap.

---

## 3. Technology Stack

### Backend
- **Language**: Python 3.10+
- **Framework**: FastAPI
- **ASGI Server**: Uvicorn
- **Configuration & Validation**: Pydantic v2, Pydantic Settings, python-dotenv

### Frontend
- **Framework**: Next.js (App Router)
- **Library**: React
- **Language**: TypeScript
- **Styling**: Tailwind CSS

---

## 4. Getting Started & Running Locally

### Prerequisites
- Node.js (v18+) and npm
- Python (3.10+)

---

### Backend Setup

1. Open a terminal and navigate to the `backend` directory:
   ```bash
   cd backend
   ```

2. Create and activate a Python virtual environment:
   - **Windows (PowerShell)**:
     ```powershell
     python -m venv .venv
     .venv\Scripts\Activate.ps1
     ```
   - **Linux / macOS**:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Prepare your local `.env` configuration:
   ```bash
   cp .env.example .env
   ```

5. Start the backend server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

6. Verify backend health:
   - Endpoint: [http://localhost:8000/api/health](http://localhost:8000/api/health)
   - Interactive Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

### Frontend Setup

1. Open a new terminal and navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```

2. Install dependencies (if not already installed):
   ```bash
   npm install
   ```

3. Start the Next.js development server:
   ```bash
   npm run dev
   ```

4. View the frontend:
   - Navigate to [http://localhost:3000](http://localhost:3000)
