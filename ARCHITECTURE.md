# Architecture & System Design

## Overview
The system is built as a decoupled, multi-tier architecture consisting of a Python/Streamlit frontend and a Python/FastAPI backend, integrated with external LLM and Search services.

## Technology Stack Justification
- **Frontend**: Streamlit. Allows extremely fast iteration for data dashboards and handles file uploads natively.
- **Backend**: FastAPI. Asynchronous, high-performance web framework. Essential for handling concurrent API requests to external services (LLM, Search).
- **Database**: SQLAlchemy ORM. Provides an abstraction layer, allowing development with SQLite and seamless migration to PostgreSQL for production.
- **Search**: Tavily. An AI-optimized search API that returns clean, summarized text from websites rather than raw HTML, drastically reducing parsing overhead and LLM token usage.
- **LLM Engine**: Gemini 1.5 Pro. Chosen for its massive context window (ideal for parsing large PDFs) and strict JSON output capabilities via `response_mime_type`.

## Data Flow
1. User uploads a PDF via Streamlit.
2. Streamlit sends the file as `multipart/form-data` to FastAPI `/upload`.
3. FastAPI saves the initial job state to the Database, spins up a `BackgroundTask`, and immediately returns a Job ID.
4. The background task extracts text (PyMuPDF).
5. The LLM extracts a structured JSON list of claims.
6. For each claim, Tavily searches the web for evidence.
7. The LLM evaluates the claim against the evidence, classifying it as VERIFIED, INACCURATE, or FALSE, and saves to the DB.
8. The frontend polls `/status/{job_id}` until complete, then fetches `/report/{job_id}` to render the dashboard.

## Advanced Evaluation Logic (Trap Documents)
The system is designed to distinguish between varying levels of truth:
- **FALSE**: The claim is entirely hallucinated or contradicts all available evidence.
- **INACCURATE**: The claim is rooted in reality but contains outdated statistics (e.g., population from 2011 presented as current). The LLM is explicitly prompted to consider the `year` entity and compare it against the publication dates returned by Tavily.
