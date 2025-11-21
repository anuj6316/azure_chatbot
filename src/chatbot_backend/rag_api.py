from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from uuid import uuid4

from ..core import chat_manager, retriver
from ..core.config import get_config, get_vectorstore

app = FastAPI()

# Configure CORS with settings from config
config = get_config()
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_allow_origins,
    allow_credentials=config.cors_allow_credentials,
    allow_methods=config.cors_allow_methods,
    allow_headers=config.cors_allow_headers,
)
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os


# Serve frontend build
# Mount the assets folder specifically to let StaticFiles handle caching/headers for assets
if os.path.exists("static/assets"):
    app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")

# Catch-all route moved to the end of the file to avoid blocking API routes


# API PREFIX
# api_router = APIRouter(prefix="/api")



class ChatRequest(BaseModel):
    query: str
    session_id: str


class ChatResponse(BaseModel):
    answer: str


# router = APIRouter(prefix="/api")

# @router.get("/")
# async def root():
#     return {"message": "API running"}

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
        import logging
        logging.error(f"Error generating response: {exc}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to generate response: {exc}"
        )


@app.get("/chat_history/{session_id}")
async def get_history(session_id: str):
    try:
        messages = chat_manager.get_chat_history_messages(session_id)
        # Convert to simple format for frontend
        formatted_messages = []
        for msg in messages:
            sender = "user" if msg.type == "human" else "bot"
            formatted_messages.append({
                "id": str(uuid4()), # Generate a temp ID as it's not stored in DB
                "text": msg.content,
                "sender": sender
            })
        return {"messages": formatted_messages}
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch history: {exc}"
        )




# Serve the root index.html specifically
@app.get("/")
async def serve_root():
    if os.path.exists("static/index.html"):
        return FileResponse("static/index.html")
    return {"message": "Frontend index.html not found."}

# Catch-all route to serve index.html for client-side routing (SPA)
# This must be defined AFTER all specific API routes
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    # If the file exists in static (e.g., favicon.ico, manifest.json), serve it
    static_file_path = os.path.join("static", full_path)
    if os.path.exists(static_file_path) and os.path.isfile(static_file_path):
        return FileResponse(static_file_path)
    
    # Otherwise, serve index.html for any other route (SPA fallback)
    if os.path.exists("static/index.html"):
        return FileResponse("static/index.html")
    
    # Fallback if static files are missing (e.g., during local backend-only dev)
    return {"message": "Frontend not found. Ensure the Docker image is built correctly or 'static' directory exists."}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
