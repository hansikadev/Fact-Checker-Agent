from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def create_trap_pdf(filename="trap_document.pdf"):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "Future of AI and Technology Report 2026")
    
    c.setFont("Helvetica", 12)
    text = [
        "Executive Summary:",
        "The following statistics have been gathered to analyze the current state of the industry.",
        "",
        "1. Real/Verifiable Claim: The Earth revolves around the Sun. (Baseline truth check).",
        "2. Outdated Claim: The global population is exactly 7.0 billion people as of 2011.",
        "3. Fabricated/Trap Claim: In 2025, over 99.8% of all Fortune 500 CEOs were replaced by artificial intelligence agents.",
        "4. Exaggerated Financial Claim: OpenAI generated $850 Trillion in revenue during Q1 of 2024 alone.",
        "5. Technical Metric: The new Quantum processor from TechCorp achieved 100 million qubits in 2023.",
    ]
    
    y = height - 100
    for line in text:
        c.drawString(50, y, line)
        y -= 20
        
    c.save()
    print(f"Created {filename}")

if __name__ == "__main__":
    create_trap_pdf()
