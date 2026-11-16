⚡ Velo AI — Intelligent Workspace & RAG EngineA Lightning-Fast, Context-Aware AI Assistant featuring Multi-Format Document RAG, Live Web Search, and Smart Intent Routing.Explore Features • System Architecture • Installation • Tech Stack📖 OverviewVelo AI is an ultra-fast, production-ready AI workspace designed to seamlessly bridge local document intelligence with real-time web knowledge. Powered by the blistering speed of Groq (Llama-3 models) and deployed serverless on Modal Cloud, Velo AI answers complex queries in under a second.The system features a Smart Intent Router that actively decides whether to read your uploaded documents, search the live web via DuckDuckGo, or answer conversationally. The modern frontend offers drag-and-drop auto-indexing, voice input, collapsible AI thought steps, and verifiable source citations.✨ Key Features🤖 AI Agent & RAG BackendSmart Intent Routing: The agent dynamically analyzes user prompts to detect if it needs to query the uploaded document, search the live web, or just have a normal conversation—saving tokens and computing time.Multi-Format Auto-Indexing: Natively supports and chunks .pdf, .docx, .txt, and .csv files using a custom TF-IDF semantic scoring system.Live Web Integration: Bypasses LLM knowledge cutoffs by actively searching the web using DuckDuckGo and providing clickable source URLs for verified information.Groq Multi-Model Brain: Automatically selects the best available Llama-3 model (Llama-3.3, Llama-3.1) via the Groq API for extreme low-latency inference.Serverless Persistence: Hosted on Modal with 24-hour auto-expiring persistent volumes (velo-ai-storage) ensuring user privacy and zero cold starts.🎨 Interactive Frontend & UXCollapsible "Thought Process" Accordion: Transparently displays the exact steps the AI took (e.g., 📄 Analyzed uploaded document, 🌐 Searched live web).Verifiable Source Citations: Generates UI "Pills" linking directly to the specific document page or live website used to generate the answer.Dynamic Suggestion Chips: The AI automatically generates 3 contextual follow-up questions at the end of every response.Voice Input Ready: Integrated Web Speech API for seamless voice-to-text dictation.Pro Developer Tools: Export entire conversations to Markdown (.md) files, one-click code/text copy buttons, and persistent workspace session IDs.🎛️ Core CapabilitiesCapabilityTrigger MechanismUI ElementAI ActionDocument Q&AKeywords (pdf, summarize) or Auto-Routing📄 Source Pills (Page #)Extracts custom TF-IDF chunks from temporary DBLive Web SearchKeywords (latest, 2026, link) or [WEB] toggle🌐 Clickable Web LinksFetches Top 4 DuckDuckGo results as contextDirect ChatGeneral greetings or logical questions⚡ Groq IconAnswers conversationally with near-zero latencyData ExtractionSidebar Quick-Chips📊 Markdown TablesStructures resume/doc data into clean formats🛠️ Tech StackBackend / API: FastAPI, Uvicorn, Python multipartCloud Infrastructure: Modal Cloud (Serverless GPU/CPU with Volume Storage)AI & LLM: Groq API (llama-3.3-70b-versatile)Document Processing: pypdf, python-docxWeb Search Engine: duckduckgo-search (ddgs)Frontend: HTML5, Modern CSS3 (Glassmorphism, Flexbox), Vanilla JavaScript (ES6+), marked.js🔄 Smart Agent Architecture[User Input (Text / Voice) + Optional Document Upload]
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│ 1. Smart Intent Router (agent.py)                       │
│    • Analyzes query syntax & keywords                   │
│    • Checks for active Session ID & Files               │
└─────────────────────────────────────────────────────────┘
         │
    ┌────┼──────────────────────────┐
    ▼    ▼                          ▼
 [RAG Search]                 [Live Web Search]
 (TF-IDF Match)                (DuckDuckGo API)
    │    │                          │
    └────┼──────────────────────────┘
         ▼
┌─────────────────────────────────────────────────────────┐
│ 2. Context Aggregation & Prompt Synthesis               │
│    • Merges Doc Chunks + Web Summaries + Chat History   │
└─────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│ 3. Groq LLM Inference Engine (models.py)                │
│    • Extremely fast Llama-3 text generation             │
│    • Appends 3 Smart Follow-up Suggestions              │
└─────────────────────────────────────────────────────────┘
         │
         ▼
[Frontend UI: Renders Markdown, Citations & Thought Steps]
