"""
Daily Planet AI Desk API — FastAPI application.
Routing layer only: receives requests, delegates to services, returns responses.
Same shape as the Module 0 service - RAG is a new capability, not a new app.
"""
from fastapi import FastAPI
from .models import AskRequest, AskResponse
from .services import ask

app = FastAPI(
    title="Daily Planet AI Desk",
    description="A RAG service that answers questions from the newsroom archive - grounded, cited, or honest",
    version="1.0.0",
)


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/ask", response_model=AskResponse)
def ask_question(req: AskRequest):
    result = ask(req.question, role=req.role)
    return AskResponse(**result)
