<div align="center">

# ⚡ Velo AI — Intelligent Workspace & Agentic RAG

**Upload documents, search the live web with verified links, and get ultra-fast AI responses powered by Smart Intent Routing.**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Groq](https://img.shields.io/badge/Groq-Llama_3.3-F55036?style=for-the-badge&logo=groq&logoColor=white)](https://groq.com/)
[![Modal](https://img.shields.io/badge/Modal-Serverless_Cloud-00D26A?style=for-the-badge&logo=modal&logoColor=black)](https://modal.com/)
[![Vercel](https://img.shields.io/badge/Vercel-Frontend_Edge-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://velo-ai-zeta.vercel.app/)
[![JavaScript](https://img.shields.io/badge/Vanilla_JS-ES6+-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)

[Live Demo](https://velo-ai-zeta.vercel.app/) • [Features](#-key-features) • [Tech Stack](#-tech-stack) • [Project Structure](#-project-structure) • [Installation](#-getting-started) • [API Reference](#-api-endpoints)

</div>

---

## 📖 Overview

**Velo AI** is a modern, decoupled full-stack AI workspace application that combines **Retrieval-Augmented Generation (RAG)** with **Real-Time Web Search** and **Smart Intent Routing**[cite: 5, 11, 12]. 

Built on an asynchronous **FastAPI** backend hosted on **Modal** and a responsive, zero-dependency **Vanilla JavaScript** frontend deployed on **Vercel**, Velo AI delivers sub-second inference via **Groq (Llama-3.3 / 3.1)**[cite: 2, 6, 7, 8, 12]. Unlike traditional chatbots that blindly query vector databases on every message, Velo AI inspects query intent first—bypassing heavy tools for casual greetings while automatically activating document chunk search or live DuckDuckGo web scraping when required[cite: 5, 10, 12].

---

## ✨ Key Features

### 🧠 Agentic Routing & RAG Intelligence
* **Smart Intent Router:** Uses regex matching and domain keyword detection (`agent.py`) to classify user queries—bypassing external tools for greetings (`Hi`, `Namaste`) and triggering Document RAG or Web Search only when relevant.
* **Multi-Format Document Auto-Indexing:** Supports `.pdf`, `.docx`, `.txt`, `.csv`, and `.md` uploads up to 15MB, splitting text into overlapping 900-character chunks (`150` overlap) for accurate retrieval.
* **TF-IDF Relevance Scoring:** Computes custom term-frequency and inverse-document-frequency scores (`tools.py`) to extract the top matching document pages and generate page-level source citations.
* **Live Web Search Engine:** Integrates `DDGS` (DuckDuckGo Search) to fetch real-time web results and clickable Markdown links, with a dedicated UI toggle (`[WEB_SEARCH]`) to force live lookups[cite: 5, 10, 11].
* **Multi-Model Groq Fallback:** Dynamically queries active Groq chat models and prioritizes `llama-3.3` and `llama-3.1` with automatic failover for uninterrupted reliability.

### ⚡ Cloud Architecture & Storage
* **Decoupled Serverless Deployment:** Frontend hosted on **Vercel Edge Network** (`velo-ai-zeta.vercel.app`) communicating with a serverless **Modal** ASGI container (`modal_app.py`)[cite: 2, 7, 11].
* **24-Hour Persistent Storage:** Uses a Modal persistent `Volume` (`/data/sessions`) with automated cleanup (`cleanup_old_sessions`) that purges inactive workspace files after 24 hours[cite: 7, 10].
* **Session Isolation:** Supports multi-workspace sessions (`velo-user-001`) with instant document removal and session reset endpoints[cite: 6, 11, 12].

### 🎨 Modern Workspace UI
* **Collapsible Thinking Steps:** Displays transparent AI reasoning steps (e.g., document analysis, web search, synthesis) inside an expandable `<details>` accordion only when external tools are triggered[cite: 5, 11].
* **Clickable Citation & Suggestion Chips:** Renders distinct source badges (PDF page tags and external web links) alongside 3 AI-generated follow-up suggestion chips after every response[cite: 5, 11].
* **Voice Input & Markdown Export:** Built-in Web Speech API (`en-IN`) voice-to-text microphone input, one-click response copying, and full conversation export as `.md` files[cite: 11].
* **Drag-and-Drop Knowledge Base:** Instant auto-upload dropzone with live chunk indexing status and one-click starter prompt chips[cite: 11, 12].

---

## 🛠 Tech Stack

| Layer | Technologies Used |
| :--- | :--- |
| **Backend Framework** | Python 3.11, FastAPI, Uvicorn (ASGI), Python-Multipart[cite: 6, 7, 9] |
| **AI & LLM Engine** | Groq API (`Llama-3.3`, `Llama-3.1`), Custom Agentic Intent Router[cite: 5, 8] |
| **Document & Web Tools** | `pypdf`, `python-docx`, `ddgs` (DuckDuckGo Search), Custom TF-IDF Scorer[cite: 9, 10] |
| **Cloud & Deployment** | Modal (`modal.App`, Persistent Volumes, Secrets), Vercel (Frontend Hosting)[cite: 2, 7] |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript (ES6+), `marked.js`, Font Awesome, Web Speech API[cite: 11, 12] |

---

## 📂 Project Structure

```text
velo-ai/
├── frontend/
│   ├── index.html           # Main workspace UI, sidebar dropzone & chat layout
│   ├── style.css            # Responsive workspace styling, animations & badges
│   └── app.js               # State management, auto-upload, voice input & API client
├── backend/
│   ├── main.py              # FastAPI application, CORS & REST endpoints
│   ├── agent.py             # Smart Intent Router, prompt builder & suggestion parser
│   ├── models.py            # Groq multi-model client with dynamic priority fallback
│   ├── tools.py             # Multi-format file chunker, TF-IDF search & DDGS web search
│   ├── modal_app.py         # Modal cloud container, volume & ASGI deployment config
│   ├── requirements.txt     # Python dependencies
│   └── .env                 # Environment variables (GROQ_API_KEY)
└── .gitignore               # Ignored files (.venv, .env, __pycache__)
