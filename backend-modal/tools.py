import os
import re
import json
import math
import time
import shutil
from pathlib import Path
from collections import Counter
from pypdf import PdfReader
import docx
from ddgs import DDGS

STORAGE_DIR = Path(os.getenv("VELO_STORAGE_DIR", Path(__file__).parent / "storage_data"))
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

STOPWORDS = {
    "the", "is", "in", "at", "of", "on", "and", "a", "to", "for", "with", "what",
    "how", "who", "why", "when", "where", "tell", "me", "about", "can", "you",
    "please", "give", "kya", "hai", "aur", "mein", "ka", "ki", "ke", "se", "ko",
    "ye", "wo", "batao", "mujhe", "hello", "hi", "hey", "thanks", "thank", "ok"
}


def cleanup_old_sessions(expiry_hours: int = 24):
    if not STORAGE_DIR.exists():
        return 0
    now = time.time()
    deleted = 0
    for folder in STORAGE_DIR.iterdir():
        if folder.is_dir():
            if now - folder.stat().st_mtime > (expiry_hours * 3600):
                shutil.rmtree(folder, ignore_errors=True)
                deleted += 1
    return deleted


def process_and_save_file(session_id: str, file_path: str, filename: str) -> int:
    cleanup_old_sessions()
    ext = Path(filename).suffix.lower()
    pages_data = []

    if ext == ".pdf":
        reader = PdfReader(file_path)
        for idx, page in enumerate(reader.pages):
            text = (page.extract_text() or "").strip()
            if text:
                pages_data.append({"text": text, "page": idx + 1, "source": filename})
    elif ext == ".docx":
        doc = docx.Document(file_path)
        full_text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        if full_text:
            pages_data.append({"text": full_text, "page": 1, "source": filename})
    elif ext in [".txt", ".csv", ".md"]:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read().strip()
            if content:
                pages_data.append({"text": content, "page": 1, "source": filename})
    else:
        raise ValueError("Unsupported file format: " + ext)

    chunks = []
    chunk_size = 900
    overlap = 150

    for item in pages_data:
        text = item["text"]
        start = 0
        while start < len(text):
            piece = text[start : start + chunk_size].strip()
            if piece:
                chunks.append({
                    "content": piece,
                    "source": item["source"],
                    "page": item["page"]
                })
            start += chunk_size - overlap

    session_dir = STORAGE_DIR / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    db_file = session_dir / "chunks.json"

    existing = []
    if db_file.exists():
        try:
            existing = json.loads(db_file.read_text(encoding="utf-8"))
        except Exception:
            existing = []

    existing.extend(chunks)
    db_file.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")
    return len(chunks)


def tokenize(text: str) -> list:
    return [w for w in re.findall(r"\w+", text.lower()) if w not in STOPWORDS and len(w) > 1]


def format_chunk(c: dict) -> str:
    src = str(c.get("source", "Document"))
    pg = str(c.get("page", 1))
    txt = str(c.get("content", ""))
    return "Source: " + src + " (Page " + pg + ")\n" + txt


def search_uploaded_chunks(session_id: str, query: str, top_k: int = 4, force_include: bool = False) -> dict:
    """Returns matched text AND structured source badges ONLY if relevant."""
    db_file = STORAGE_DIR / session_id / "chunks.json"
    if not db_file.exists():
        return {"context": "", "sources": []}

    chunks = json.loads(db_file.read_text(encoding="utf-8"))
    if not chunks:
        return {"context": "", "sources": []}

    query_tokens = tokenize(query)
    N = len(chunks)
    doc_tokens = [tokenize(c["content"]) for c in chunks]
    df = Counter()
    for tokens in doc_tokens:
        for t in set(tokens):
            df[t] += 1

    scored_chunks = []
    for idx, tokens in enumerate(doc_tokens):
        tf = Counter(tokens)
        score = 0.0
        for q_word in query_tokens:
            if q_word in tf:
                idf = math.log(1 + (N - df[q_word] + 0.5) / (df[q_word] + 0.5))
                score += (tf[q_word] / (len(tokens) + 1)) * idf
        scored_chunks.append((score, chunks[idx]))

    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    best = [item[1] for item in scored_chunks[:top_k] if item[0] > 0.15]

    # Only fallback to first chunks if user explicitly asked about the document/summary
    if not best and force_include:
        best = chunks[:top_k]

    if not best:
        return {"context": "", "sources": []}

    sources = []
    seen = set()
    for c in best:
        label = str(c.get("source", "Doc")) + " • Page " + str(c.get("page", 1))
        if label not in seen:
            seen.add(label)
            sources.append({"type": "doc", "title": label})

    return {
        "context": "\n\n---\n\n".join([format_chunk(c) for c in best]),
        "sources": sources
    }


def search_live_web(query: str, max_results: int = 4) -> dict:
    try:
        results = list(DDGS().text(query, max_results=max_results))
        if not results:
            return {"context": "", "sources": []}
        formatted = []
        sources = []
        for r in results:
            title = str(r.get("title", "Web Link"))
            url = str(r.get("href", ""))
            body = str(r.get("body", ""))
            formatted.append("Title: " + title + "\nURL: " + url + "\nSummary: " + body)
            if url:
                sources.append({"type": "web", "title": title[:45], "url": url})
        return {"context": "\n\n".join(formatted), "sources": sources}
    except Exception as e:
        return {"context": "Web search error: " + str(e), "sources": []}


def has_uploaded_file(session_id: str) -> bool:
    return (STORAGE_DIR / session_id / "chunks.json").exists()


def clear_user_session(session_id: str):
    session_dir = STORAGE_DIR / session_id
    if session_dir.exists():
        shutil.rmtree(session_dir, ignore_errors=True)