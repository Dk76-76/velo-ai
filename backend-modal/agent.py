import re
import time
from models import generate_ai_response
from tools import search_uploaded_chunks, search_live_web, has_uploaded_file

GREETINGS = {
    "hi", "hello", "hey", "hii", "helo", "hola", "namaste", "good morning",
    "good evening", "good afternoon", "thanks", "thank you", "ok", "okay",
    "bye", "who are you", "what can you do", "kaise ho", "kya haal hai"
}

DOC_KEYWORDS = [
    "pdf", "doc", "document", "file", "resume", "cv", "upload", "uploaded",
    "page", "summary", "summarize", "extract", "explain this", "according to",
    "is file", "is pdf", "isme", "iss pdf", "notes", "report", "table", "data",
    "projects", "skills", "experience", "education", "contact", "details"
]

WEB_KEYWORDS = [
    "link", "links", "url", "website", "websites", "official", "documentation",
    "search", "latest", "news", "current", "online", "tutorial", "course",
    "youtube", "github", "download", "where can i find", "resource", "resources",
    "2025", "2026", "price", "live", "today"
]


def is_simple_greeting(query: str) -> bool:
    clean = re.sub(r"[^\w\s]", "", query.lower()).strip()
    return clean in GREETINGS or (len(clean.split()) <= 2 and clean in GREETINGS)


def is_asking_about_doc(query: str) -> bool:
    q_lower = query.lower()
    return any(k in q_lower for k in DOC_KEYWORDS)


def needs_web_search(query: str) -> bool:
    q_lower = query.lower()
    return any(k in q_lower for k in WEB_KEYWORDS)


def run_velo_agent(session_id: str, query: str, chat_history: str = "[]", project_id: str = "portfolio-main") -> dict:
    start_time = time.time()
    thinking_steps = []
    context_blocks = []
    sources_used = []

    # Check if user toggled "[WEB_SEARCH]" from UI
    force_web = False
    clean_query = query.strip()
    if clean_query.startswith("[WEB_SEARCH]"):
        force_web = True
        clean_query = clean_query.replace("[WEB_SEARCH]", "").strip()

    file_present = has_uploaded_file(session_id)
    greeting = is_simple_greeting(clean_query)

    # 1. SMART DOCUMENT ROUTING: Only read PDF if NOT a greeting AND (explicitly asked OR keyword matches PDF)
    if file_present and not greeting:
        explicit_doc = is_asking_about_doc(clean_query)
        doc_res = search_uploaded_chunks(session_id, clean_query, top_k=4, force_include=explicit_doc)
        if doc_res["context"]:
            thinking_steps.append("📄 Analyzed uploaded document & matched relevant sections")
            context_blocks.append("=== UPLOADED DOCUMENT CONTENT ===\n" + doc_res["context"])
            sources_used.extend(doc_res["sources"])

    # 2. SMART WEB SEARCH ROUTING: Run if user requested links/latest info or toggled Web Search button
    if not greeting and (force_web or needs_web_search(clean_query)):
        thinking_steps.append("🌐 Searched live web for verified links & up-to-date info")
        web_res = search_live_web(clean_query, max_results=4)
        if web_res["context"]:
            context_blocks.append("=== LIVE WEB SEARCH RESULTS ===\n" + web_res["context"])
            sources_used.extend(web_res["sources"])

    # Only add AI Brain step to thinking box if external tools (PDF or Web) were actually used!
    if thinking_steps:
        thinking_steps.append("🧠 Synthesized verified answer from matched sources")

    system_prompt = (
        "You are Velo AI, a world-class, ultra-fast AI workspace assistant.\n"
        "Rules:\n"
        "1. If UPLOADED DOCUMENT CONTENT is provided, answer accurately from it and mention the source/page naturally.\n"
        "2. If LIVE WEB SEARCH RESULTS are provided, include clickable Markdown links: [Title](https://...).\n"
        "3. If no external context is provided (e.g., greetings or general questions), answer naturally and concisely.\n"
        "4. Reply in the exact language/style the user uses (English, Hindi, or Hinglish).\n"
        "5. At the very end of your response, ALWAYS add a new line with 'SUGGESTIONS:' followed by 3 short, smart follow-up questions separated by '|' (Example: SUGGESTIONS: Summarize key skills | Find GitHub links | Ask interview questions)."
    )

    combined_context = "\n\n".join(context_blocks) if context_blocks else "Direct conversation (No external document/web tools needed)."

    user_prompt = (
        f"Previous Chat History:\n{chat_history}\n\n"
        f"Context Data:\n{combined_context}\n\n"
        f"User Message: {clean_query}"
    )

    ai_result = generate_ai_response(system_prompt, user_prompt)
    raw_text = ai_result["text"]

    # Extract 3 Follow-Up Suggestion Chips cleanly
    suggestions = []
    reply_text = raw_text
    if "SUGGESTIONS:" in raw_text:
        parts = raw_text.split("SUGGESTIONS:")
        reply_text = parts[0].strip()
        raw_suggs = parts[-1].strip().split("|")
        suggestions = [s.strip().strip("-*•123. ") for s in raw_suggs if s.strip()][:3]

    elapsed = round(time.time() - start_time, 2)

    return {
        "reply": reply_text,
        "model_used": ai_result["model_used"],
        "response_time": f"{elapsed}s",
        "thinking_steps": thinking_steps,  # Empty [] on normal 'Hello' -> No ugly box!
        "sources": sources_used,
        "suggestions": suggestions,
        "has_document": file_present,
        "project_id": project_id
    }