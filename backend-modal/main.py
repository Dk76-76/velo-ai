from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from tools import process_and_save_file, clear_user_session, STORAGE_DIR
from agent import run_velo_agent

app = FastAPI(title="Velo AI Engine", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"


@app.get("/health")
async def health():
    return {
        "status": "online",
        "engine": "Velo AI v2.0 (Modular Pipeline)",
        "features": ["Multi-Format File Reader", "Live Web Links", "Groq Brain", "24h Auto-Delete"]
    }


@app.post("/upload")
async def upload_file(
    session_id: str = Form(...),
    file: UploadFile = File(...)
):
    content = await file.read()
    if len(content) > 15 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size exceeds 15MB limit.")

    temp_path = STORAGE_DIR / f"temp_{session_id}_{file.filename}"
    try:
        with open(temp_path, "wb") as f:
            f.write(content)

        chunks_count = process_and_save_file(session_id, str(temp_path), file.filename)
        if chunks_count == 0:
            raise HTTPException(status_code=400, detail="No readable text found in file.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        if temp_path.exists():
            temp_path.unlink()

    return {
        "status": "success",
        "filename": file.filename,
        "chunks_indexed": chunks_count,
        "expires_in": "24 hours"
    }


@app.post("/chat")
async def chat_endpoint(
    session_id: str = Form(...),
    query: str = Form(...),
    chat_history: str = Form("[]"),
    project_id: str = Form("portfolio-main")
):
    try:
        return run_velo_agent(
            session_id=session_id,
            query=query,
            chat_history=chat_history,
            project_id=project_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    clear_user_session(session_id)
    return {"status": "cleared", "session_id": session_id}


# Serve Frontend UI locally if frontend folder exists, otherwise return API status on Cloud
@app.get("/")
async def serve_ui():
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"status": "online", "engine": "Velo AI Cloud API Ready"}

if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR)), name="frontend")