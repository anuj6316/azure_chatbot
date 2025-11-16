from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ..core import chat_manager, retriver
from ..core.config import get_config, get_vectorstore

config = get_config()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_allow_origins,
    allow_credentials=config.cors_allow_credentials,
    allow_methods=config.cors_allow_methods,
    allow_headers=config.cors_allow_headers,
)


class ChatRequest(BaseModel):
    query: str
    session_id: str


class ChatResponse(BaseModel):
    answer: str


@app.get("/")
async def health():
    return {"status": "healthy", "service": "rag-chatbot"}


@app.post("/chat_response")
async def rag_chat(body: ChatRequest):
    try:
        vectorstore = get_vectorstore()
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    try:
        relevant_docs = retriver.get_relevant_docs(vectorstore, body.query)
        llm = chat_manager.get_llm()
        result = chat_manager.generate_response(
            llm, relevant_docs, body.query, body.session_id
        )
        return result
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate response: {exc}"
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
