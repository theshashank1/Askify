# E:\FinalProjects\Cyberbear\Askify\tests\main_test.py
import sys
import os
import pytest
import asyncio
from fastapi.testclient import TestClient

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

client = TestClient(app)

@pytest.mark.asyncio
async def test_question_answer():
    # First, upload a PDF to get a document ID
    file_path = "E:\\FinalProjects\\Cyberbear\\Askify\\upload\\1b57adfd-e24d-4bbe-96d0-53dc791b1a75.pdf"
    with open(file_path, "rb") as file:
        upload_response = client.post("/upload", files={"file": ("sample.pdf", file, "application/pdf")})
    assert upload_response.status_code == 200
    document_id = upload_response.json()["document_id"]

    # Use TestClient's websocket_connect context manager
    async with client.websocket_connect(f"/ws/question_answer/{document_id}") as websocket:
        question = "What is the main topic of this document?"
        await websocket.send_text(question)
        response = await websocket.receive_text()
        assert "answer" in response