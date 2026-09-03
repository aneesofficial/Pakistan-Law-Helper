from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import os
from utils.rag import answer_question

# Load environment variables
load_dotenv()

app = FastAPI(title="Pakistan Law Helper API")

# Configure CORS for Next.js frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AskRequest(BaseModel):
    question: str
    province: str = "Federal"

class SourceModel(BaseModel):
    law_name: str
    year: str
    section_number: str
    province: str
    section_text: str

class AskResponse(BaseModel):
    answer: str
    sources: List[SourceModel]

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

@app.post("/api/ask", response_model=AskResponse)
async def ask_question(request: AskRequest):
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
        
    try:
        # Call the existing RAG pipeline
        answer, retrieved_sources = answer_question(request.question, request.province)
        
        # Transform retrieved_sources to match the SourceModel
        formatted_sources = []
        for src in retrieved_sources:
            formatted_sources.append(SourceModel(
                law_name=src.get('law_name', 'Unknown Act'),
                year=str(src.get('year', 'N/A')),
                section_number=str(src.get('section_number', 'N/A')),
                province=src.get('province', 'Federal'),
                section_text=src.get('section_text', '')
            ))
            
        return AskResponse(answer=answer, sources=formatted_sources)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
