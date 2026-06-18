import requests
import time
import sys

BACKEND_URL = "http://localhost:8000"

def test_fact_checker():
    print("Generating trap document...")
    from generate_trap_doc import create_trap_pdf
    create_trap_pdf("trap_document.pdf")
    
    print("Uploading document to backend...")
    with open("trap_document.pdf", "rb") as f:
        files = {"file": ("trap_document.pdf", f, "application/pdf")}
        response = requests.post(f"{BACKEND_URL}/upload", files=files)
        response.raise_for_status()
        job_id = response.json()["job_id"]
        
    print(f"Job ID: {job_id}")
    
    print("Polling for status...")
    while True:
        status_res = requests.get(f"{BACKEND_URL}/status/{job_id}")
        status_res.raise_for_status()
        status_data = status_res.json()
        print(f"Status: {status_data['status']} | Progress: {status_data['progress']}")
        
        if status_data["status"] == "COMPLETED":
            break
        elif status_data["status"] == "FAILED":
            print("Verification failed!")
            sys.exit(1)
            
        time.sleep(2)
        
    print("\nFetching final report...")
    report_res = requests.get(f"{BACKEND_URL}/report/{job_id}")
    report_res.raise_for_status()
    report = report_res.json()
    
    print("\n" + "="*50)
    print("📊 FINAL REPORT SUMMARY")
    print("="*50)
    print(f"Total Claims: {report['total_claims']}")
    print(f"Verified: {report['verified_count']}")
    print(f"Inaccurate: {report['inaccurate_count']}")
    print(f"False: {report['false_count']}")
    print("-" * 50)
    
    for idx, claim in enumerate(report['claims']):
        orig = claim['original_claim']
        print(f"Claim {idx+1}: {orig['claim_text']}")
        print(f"Status: {claim['status']}")
        print(f"Explanation: {claim['explanation']}")
        print("-" * 50)
        
    print("✅ Test passed successfully.")

if __name__ == "__main__":
    test_fact_checker()
