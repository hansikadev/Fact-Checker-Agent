import fitz  # PyMuPDF

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extracts all text from a PDF file."""
    text = ""
    try:
        # Open the PDF from bytes
        pdf_document = fitz.open(stream=file_bytes, filetype="pdf")
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            text += page.get_text() + "\n"
        pdf_document.close()
    except Exception as e:
        print(f"Error extracting PDF: {e}")
        
    return text
