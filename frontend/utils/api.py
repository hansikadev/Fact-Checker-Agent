import httpx
import os
import streamlit as st

try:
    BACKEND_URL = st.secrets.get("BACKEND_URL", os.environ.get("BACKEND_URL", "http://localhost:8000"))
except Exception:
    BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")

def upload_document(file_bytes, filename):
    with httpx.Client(timeout=30.0) as client:
        files = {'file': (filename, file_bytes, 'application/pdf')}
        response = client.post(f"{BACKEND_URL}/upload", files=files)
        response.raise_for_status()
        return response.json()

def get_status(job_id):
    with httpx.Client() as client:
        response = client.get(f"{BACKEND_URL}/status/{job_id}")
        response.raise_for_status()
        return response.json()

def get_report(job_id):
    with httpx.Client() as client:
        response = client.get(f"{BACKEND_URL}/report/{job_id}")
        response.raise_for_status()
        return response.json()
