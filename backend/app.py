from fastapi import FastAPI
from backend.schemas import QueryRequest
from backend.rag_service import ask_question

app = FastAPI(title="Emergency AI Assistant")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/agent/query")
def query_agent(request: QueryRequest):

    question = request.question.lower()

    emergency_keywords = [
        "cpr", "bleeding", "burn", "fracture", "shock",
        "choking", "emergency", "injury", "first aid",
        "not breathing", "unconscious"
    ]

    # Check if question is domain-related
    if not any(keyword in question for keyword in emergency_keywords):
        return {
            "response": "👋 Hello! I’m your emergency response assistant. Please ask a first-aid or emergency-related question."
        }

    response = ask_question(request.question)
    return {"response": response}