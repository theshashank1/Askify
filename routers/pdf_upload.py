from pydantic import BaseModel
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, Document
from utils.pdf_processor import load_pdf  # Assuming this function is correctly implemented to read PDFs
import uuid  # Import the uuid module
import os

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/upload_pdf", response_model=dict)
async def upload_pdf(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Invalid file type")

    # Read the content of the uploaded PDF file
    content = await file.read()

    # Generate a random UUID for the PDF
    pdf_id = str(uuid.uuid4())  # Generate a UUID as a string

    # Create the upload directory if it doesn't exist
    upload_dir = "upload"
    os.makedirs(upload_dir, exist_ok=True)

    # Save the PDF file to the upload folder
    pdf_path = os.path.join(upload_dir, f"{pdf_id}.pdf")
    with open(pdf_path, "wb") as pdf_file:
        pdf_file.write(content)

    # Now, load the content from the saved PDF file
    extracted_text = load_pdf(pdf_path)[0].page_content

    # Create a new document instance
    new_doc = Document(filename=file.filename, content=extracted_text, pdf_id=pdf_id)  # Ensure pdf_id is correctly used

    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)

    return {
        "filename": file.filename,
        "message": "PDF uploaded and processed",
        "id": pdf_id  # Return the UUID in the response
    }
