from fastapi import FastAPI
from pydantic import BaseModel, Field


from rag_knowledge_assistant.config import validate_config
from rag_knowledge_assistant.rag import RAGChain
from fastapi.middleware.cors import CORSMiddleware

validate_config()

app = FastAPI(
    title="RAG Knowledge Assistant API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag = RAGChain()


class ConversationMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    question: str
    conversation: list[ConversationMessage] = Field(
        default_factory=list
    )
    filters: dict | None = None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat")
def chat(request: ChatRequest):
    conversation_history = [
        message.model_dump()
        for message in request.conversation
    ]

    result = rag.ask(
        question=request.question,
        conversation_history=conversation_history,
        filters=request.filters,
    )

    updated_conversation = conversation_history + [
        {
            "role": "user",
            "content": request.question,
        },
        {
            "role": "assistant",
            "content": result["answer"],
        },
    ]

    sources = []

    for document in result["documents"]:
        sources.append({
            "document": document.metadata.get("document_name"),
            "page": document.metadata.get("page"),
            "chunk": document.metadata.get("chunk_id"),
        })

    return {
        "answer": result["answer"],
        "search_query": result["search_query"],
        "sources": sources,
        "conversation": updated_conversation,
    }