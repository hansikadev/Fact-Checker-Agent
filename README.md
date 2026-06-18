# Fact-Check Agent Web App

A full-stack, AI-powered web application that automatically extracts claims from uploaded PDFs and fact-checks them against live web sources. Designed specifically to handle "Trap Documents" containing fabricated claims or outdated statistics.

## Features
- **PDF Parsing**: High-fidelity text extraction using PyMuPDF.
- **Claim Extraction**: Gemini-powered extraction of quantitative claims, dates, and statistics into structured JSON.
- **Live Verification**: Uses Tavily API to search the live web for evidence supporting or refuting each claim.
- **Advanced Evaluation Engine**: Differentiates between `VERIFIED`, `INACCURATE` (outdated/partially true), and `FALSE` (hallucinated) claims.
- **Beautiful UI**: Built with Streamlit, featuring real-time status updates, metric cards, and donut charts.

## Project Structure
```text
fact_check_agent/
├── backend/
│   ├── api/            # API endpoints
│   ├── models/         # Pydantic schemas & SQLAlchemy models
│   ├── services/       # Core logic (PDF extraction, LLM, verification)
│   ├── database.py     # Database configuration
│   └── main.py         # FastAPI application entry point
├── frontend/
│   ├── components/     # UI components
│   ├── utils/          # API communication utils
│   └── app.py          # Main Streamlit application
├── tests/              # Generation scripts for trap doc & presentation
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
└── README.md
```

## Setup Instructions

1. Clone the repository and navigate into it.
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Set up your `.env` file by copying `.env.example`:
   ```bash
   cp .env.example .env
   ```
   Add your `GEMINI_API_KEY` and `TAVILY_API_KEY`.

## Running Locally

1. **Start the FastAPI Backend**:
   ```bash
   uvicorn backend.main:app --reload --port 8000
   ```
2. **Start the Streamlit Frontend**:
   Open a new terminal and run:
   ```bash
   streamlit run frontend/app.py
   ```
3. Open your browser to the URL provided by Streamlit (usually `http://localhost:8501`).

## Testing with Trap Documents
Run the script to generate a test PDF containing intentionally false and outdated claims:
```bash
python tests/generate_trap_doc.py
```
Upload the generated `trap_document.pdf` to the Streamlit app to see the verification engine in action.

## Generate Presentation
To generate the architecture slide deck:
```bash
python tests/generate_presentation.py
```
