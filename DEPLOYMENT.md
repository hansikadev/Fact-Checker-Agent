# Fact-Check Agent Deployment Guide

This guide outlines how to deploy the Fact-Check Agent Web App to production.

## 1. Backend Deployment (Render)

Render is perfect for hosting FastAPI applications.

1. Create an account on [Render](https://render.com/).
2. Click "New Web Service" and link your GitHub repository.
3. Configure the service:
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
4. Add Environment Variables:
   - `GEMINI_API_KEY`
   - `TAVILY_API_KEY`
   - `DATABASE_URL` (You can attach a free PostgreSQL database natively in Render and use its URL here).
5. Deploy. Once deployed, note your Render URL (e.g., `https://fact-check-api.onrender.com`).

## 2. Frontend Deployment (Streamlit Cloud)

Streamlit Community Cloud is the fastest way to deploy the UI.

1. Go to [share.streamlit.io](https://share.streamlit.io/) and connect your GitHub account.
2. Click "New app".
3. Select your repository, branch, and specify the main file path: `frontend/app.py`.
4. Click on "Advanced settings" before deploying.
5. In the "Secrets" section, add your backend URL:
   ```toml
   BACKEND_URL = "https://fact-check-api.onrender.com"
   ```
   *(Note: Ensure `frontend/utils/api.py` checks `st.secrets` or `os.environ` for this URL).*
6. Click Deploy.

## Production Considerations

- **Database**: The current codebase uses SQLite for easy local setup. For production on Render, you MUST switch to PostgreSQL, as Render's local disk is ephemeral. Update your `.env` `DATABASE_URL` to the Postgres connection string provided by Render.
- **Worker Queues**: Currently, background tasks run directly in FastAPI's memory via `BackgroundTasks`. For heavy production workloads with large PDFs, migrate this to a Celery + Redis worker queue.
