from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from rag import ChatService
from sqlalchemy.orm import Session
from database import SessionLocal, Document
import os

router = APIRouter()


def get_db() :
    db = SessionLocal()
    try :
        yield db
    finally :
        db.close()


@router.websocket("/ws/question_answer/{document_id}")
async def question_answer_ws(websocket: WebSocket, document_id: str, db: Session = Depends(get_db)) :
    await websocket.accept()

    # Build the PDF path dynamically using the document ID
    pdf_path = os.path.join("E:\\FinalProjects\\Cyberbear\\Askify\\upload", f"{document_id}.pdf")

    # Check if the PDF file exists
    if not os.path.exists(pdf_path) :
        await websocket.send_text("Document not found.")
        await websocket.close()
        return

    # Initialize the ChatService with the PDF path
    chat_service = ChatService(pdf_path)

    try :
        while True :
            data = await websocket.receive_text()
            # Get the response from the chat service
            response = chat_service.chat(data)  # Pass the question to the chat service
            await websocket.send_text(response)
    except WebSocketDisconnect :
        print("Client disconnected")
