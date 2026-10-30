from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.rag_engine import answer_question

app = FastAPI(
    title="PharmaGuide RAG API",
    description=(
        "A pharmaceutical drug-label information assistant "
        "grounded in DailyMed label passages."
    ),
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

class QuestionRequest(BaseModel):
    question: str = Field(
        min_length=3,
        max_length=1000,
        description="A question about information in a drug label.",
    )


class AnswerResponse(BaseModel):
    question: str
    answer: str
    sources: list[dict]


@app.get("/")
def root():
    return {
        "name": "PharmaGuide RAG",
        "status": "running",
        "disclaimer": (
            "Drug-label information only. Not a substitute for "
            "professional medical advice."
        ),
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/ask", response_model=AnswerResponse)
def ask(request: QuestionRequest):
    try:
        answer, documents = answer_question(request.question)

        sources = []
        seen = set()

        for document in documents:
            metadata = document["metadata"]
            key = (
                metadata.get("set_id"),
                metadata.get("section"),
            )

            if key in seen:
                continue

            seen.add(key)

            sources.append({
                "drug_name": metadata.get("drug_name"),
                "section": metadata.get("section"),
                "set_id": metadata.get("set_id"),
                "source_url": metadata.get("source_url"),
            })

        return AnswerResponse(
            question=request.question,
            answer=answer,
            sources=sources,
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="The assistant could not process the question.",
        ) from error