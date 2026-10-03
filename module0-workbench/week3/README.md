# AI Workbench

A multi-task LLM-powered text processing service built progressively across Module 0.

## Prerequisites: Install Docker Desktop (one-time, free)

Week 3 uses Docker to package the service. Install it once — it's **free** for personal and course use.

1. Go to **https://www.docker.com/products/docker-desktop/**
2. Download for your operating system:
   - **Mac:** choose *Apple Silicon* (M1/M2/M3) or *Intel chip* — check  → About This Mac if unsure.
   - **Windows:** download the installer; it may ask you to enable WSL 2 (just click through).
   - **Linux:** follow the linked install docs for your distro.
3. Run the installer, then **launch Docker Desktop**.
4. Wait for the **whale icon** (menu bar on Mac, system tray on Windows) to stop animating — that means Docker is running.
5. Verify in a terminal: `docker --version` should print a version number.

> You already installed Python, VS Code, and Git in Week 1 — Docker is the same kind of one-time setup.

## Quick Start (Docker Compose)

```bash
cp .env.example .env
# Edit .env with your actual API key

docker compose up --build
```

- Backend API: http://localhost:8000
- Frontend UI: http://localhost:8501
- API Docs: http://localhost:8000/docs

## Manual Start (Development)

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env  # Edit with your key
uvicorn app.main:app --reload

# Frontend (separate terminal)
cd frontend
pip install -r requirements.txt
BACKEND_URL=http://localhost:8000 streamlit run streamlit_app.py
```

## Deploy to EC2

```bash
# On a fresh EC2 instance (Amazon Linux 2023):
sudo dnf install -y git          # a fresh server has no git yet
git clone <your-repo-url> && cd ai-workbench
# create .env with your real key, then:
chmod +x setup.sh
./setup.sh
```

> ⚠️ **Cost & shutdown — important.** A running EC2 instance costs money (new AWS accounts get a Free Tier;
> otherwise ~1 cent/hour). **When you're finished, switch it off** in the AWS Console → EC2 → *Instance state*:
> **Stop** pauses billing (you can start it again later); **Terminate** deletes it completely. For this course,
> **terminate** the instance once you've seen it work — so it never keeps charging you.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /health | Service health check |
| POST | /summarize | Summarize text in bullet points |
| POST | /rewrite | Rewrite text professionally |
| POST | /keypoints | Extract key points |
| POST | /explain | Explain in simple terms |

## Architecture

```
Browser → Streamlit (8501) → FastAPI (8000) → LLM API (OpenAI)
```

## Agent Teaser

```bash
python agent_teaser.py
```

Demonstrates the think → act → observe loop using this API as a tool.
