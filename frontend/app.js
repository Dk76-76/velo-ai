document.addEventListener("DOMContentLoaded", () => {
    const API_URL = "https://dk76-76--velo-ai-engine-serve-cloud.us-east.modal.run";

    const sessionIdInput = document.getElementById("sessionIdInput");
    const newSessionBtn = document.getElementById("newSessionBtn");
    const fileInput = document.getElementById("fileInput");
    const dropZone = document.getElementById("dropZone");
    const uploadIcon = document.getElementById("uploadIcon");
    const uploadTitle = document.getElementById("uploadTitle");
    const fileNameDisplay = document.getElementById("fileNameDisplay");
    const activeDocBadge = document.getElementById("activeDocBadge");
    const activeDocName = document.getElementById("activeDocName");
    const removeDocBtn = document.getElementById("removeDocBtn");
    const quickAttachBtn = document.getElementById("quickAttachBtn");
    const webSearchToggle = document.getElementById("webSearchToggle");
    const voiceBtn = document.getElementById("voiceBtn");
    const exportChatBtn = document.getElementById("exportChatBtn");
    const chatMessages = document.getElementById("chatMessages");
    const userInput = document.getElementById("userInput");
    const sendBtn = document.getElementById("sendBtn");
    const clearChatBtn = document.getElementById("clearChatBtn");
    const jsStatusText = document.getElementById("jsStatusText");

    if (jsStatusText) {
        jsStatusText.textContent = "Engine Online (v5 Pro)";
    }

    let chatHistory = [];
    let webSearchActive = false;

    function renderMarkdown(text) {
        if (!text) return "";
        let html = "";
        if (typeof marked !== "undefined" && typeof marked.parse === "function") {
            try { html = marked.parse(String(text)); } catch (e) { html = String(text); }
        } else {
            html = String(text)
                .replace(/\[([^\]]+)\]\((https?:\/\/[^\)]+)\)/g, '<a href="$2" target="_blank">$1</a>')
                .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
                .replace(/\n/g, "<br>");
        }
        return html.replace(/<a /g, '<a target="_blank" rel="noopener noreferrer" ');
    }

    function appendMessage(text, className, isRawHTML = false) {
        const msgDiv = document.createElement("div");
        msgDiv.className = "message " + className;
        const icon = className === "user-message"
            ? '<i class="fa-solid fa-user"></i>'
            : '<i class="fa-solid fa-bolt"></i>';

        const bodyHTML = isRawHTML ? text : renderMarkdown(text);
        msgDiv.innerHTML = `
            <div class="avatar">${icon}</div>
            <div class="msg-body">
                <div class="content">${bodyHTML}</div>
            </div>
        `;
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return msgDiv;
    }

    // Toggle Force Web Search Mode
    webSearchToggle.addEventListener("click", () => {
        webSearchActive = !webSearchActive;
        webSearchToggle.classList.toggle("active", webSearchActive);
    });

    // Auto-Resize Textarea
    userInput.addEventListener("input", () => {
        userInput.style.height = "auto";
        userInput.style.height = Math.min(userInput.scrollHeight, 130) + "px";
    });

    // Quick Attach Button
    quickAttachBtn.addEventListener("click", () => fileInput.click());

    // Sidebar One-Click Starter Chips
    document.querySelectorAll(".quick-chip").forEach(btn => {
        btn.addEventListener("click", () => {
            userInput.value = btn.getAttribute("data-prompt");
            handleSendMessage();
        });
    });

    // Remove / Clear Uploaded Document from Session
    removeDocBtn.addEventListener("click", async () => {
        const sessionId = sessionIdInput.value.trim();
        await fetch(`${API_URL}/session/${sessionId}`, { method: "DELETE" });
        activeDocBadge.classList.add("hidden");
        uploadTitle.textContent = "Click or Drop Document";
        fileNameDisplay.textContent = "PDF, DOCX, TXT, CSV (Auto-uploads)";
        appendMessage("🗑️ Removed uploaded document from current session.", "ai-message");
    });

    // New Workspace Session
    newSessionBtn.addEventListener("click", () => {
        const randomId = "velo-" + Math.floor(100000 + Math.random() * 900000);
        sessionIdInput.value = randomId;
        activeDocBadge.classList.add("hidden");
        uploadTitle.textContent = "Click or Drop Document";
        fileNameDisplay.textContent = "PDF, DOCX, TXT, CSV (Auto-uploads)";
        chatMessages.innerHTML = "";
        appendMessage(`Started new workspace (**${randomId}**). Drop a document or ask anything!`, "ai-message");
        chatHistory = [];
    });

    // Instant Auto-Upload Function
    async function autoUploadFile(file) {
        if (!file) return;
        const sessionId = sessionIdInput.value.trim() || "velo-user-001";
        const formData = new FormData();
        formData.append("session_id", sessionId);
        formData.append("file", file);

        uploadIcon.className = "fa-solid fa-spinner fa-spin";
        uploadTitle.textContent = "Indexing Document...";
        fileNameDisplay.textContent = file.name;

        const statusMsg = appendMessage(
            `<i class="fa-solid fa-spinner fa-spin"></i> Auto-indexing <strong>${file.name}</strong> into session memory...`,
            "ai-message",
            true
        );

        try {
            const response = await fetch(`${API_URL}/upload`, { method: "POST", body: formData });
            const data = await response.json();
            if (response.ok) {
                uploadIcon.className = "fa-solid fa-cloud-arrow-up";
                uploadTitle.textContent = "Add Another Document";
                fileNameDisplay.textContent = "Indexed & Ready";

                activeDocBadge.classList.remove("hidden");
                activeDocName.textContent = `${data.filename} (${data.chunks_indexed} chunks)`;

                statusMsg.querySelector(".content").innerHTML =
                    `<p style="color:#34d399;"><i class="fa-solid fa-circle-check"></i> <strong>${data.filename}</strong> indexed (${data.chunks_indexed} sections). Ask me anything about it!</p>`;
            } else {
                uploadIcon.className = "fa-solid fa-triangle-exclamation";
                uploadTitle.textContent = "Upload Failed";
                statusMsg.querySelector(".content").innerHTML =
                    `<p style="color:#f87171;">❌ Upload failed: ${data.detail || "Unsupported file"}</p>`;
            }
        } catch (err) {
            uploadIcon.className = "fa-solid fa-triangle-exclamation";
            uploadTitle.textContent = "Connection Error";
            statusMsg.querySelector(".content").innerHTML =
                `<p style="color:#f87171;">❌ Network Error: Ensure FastAPI is running on port 8000.</p>`;
        } finally {
            fileInput.value = "";
        }
    }

    fileInput.addEventListener("change", (e) => {
        if (e.target.files && e.target.files.length > 0) autoUploadFile(e.target.files[0]);
    });

    dropZone.addEventListener("dragover", (e) => { e.preventDefault(); dropZone.classList.add("drag-active"); });
    dropZone.addEventListener("dragleave", () => dropZone.classList.remove("drag-active"));
    dropZone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropZone.classList.remove("drag-active");
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) autoUploadFile(e.dataTransfer.files[0]);
    });

    // Main Send Chat Handler
    async function handleSendMessage(customQuery = null) {
        const text = (typeof customQuery === "string" ? customQuery : userInput.value).trim();
        if (!text) return;

        const sessionId = sessionIdInput.value.trim() || "velo-user-001";
        userInput.value = "";
        userInput.style.height = "auto";

        appendMessage(text, "user-message");
        chatHistory.push({ role: "user", content: text });

        const aiMsgDiv = appendMessage(
            `<span style="color:#94a3b8;"><i class="fa-solid fa-circle-notch fa-spin"></i> Thinking...</span>`,
            "ai-message",
            true
        );
        const msgBody = aiMsgDiv.querySelector(".msg-body");
        const contentDiv = aiMsgDiv.querySelector(".content");

        const queryPayload = webSearchActive ? `[WEB_SEARCH] ${text}` : text;

        try {
            const formData = new URLSearchParams();
            formData.append("session_id", sessionId);
            formData.append("query", queryPayload);
            formData.append("chat_history", JSON.stringify(chatHistory.slice(-6)));

            const response = await fetch(`${API_URL}/chat`, {
                method: "POST",
                headers: { "Content-Type": "application/x-www-form-urlencoded" },
                body: formData
            });

            const data = await response.json();
            if (response.ok) {
                let htmlContent = "";

                // 1. ONLY show Collapsible Thought Accordion if tools (PDF/Web) were actually used!
                if (data.thinking_steps && data.thinking_steps.length > 0) {
                    htmlContent += `
                        <details class="thought-details">
                            <summary><i class="fa-solid fa-microchip"></i> Used ${data.thinking_steps.length} Intelligence Steps (Click to view)</summary>
                            <div class="thought-steps-list">
                                ${data.thinking_steps.map(s => `<div>✓ ${s}</div>`).join("")}
                            </div>
                        </details>
                    `;
                }

                // 2. Main Markdown Answer
                htmlContent += renderMarkdown(data.reply);

                // 3. Source Citation Pills (PDF Pages or Web Links)
                if (data.sources && data.sources.length > 0) {
                    htmlContent += `<div class="sources-row">`;
                    data.sources.forEach(src => {
                        if (src.type === "web" && src.url) {
                            htmlContent += `<a href="${src.url}" target="_blank" class="source-pill web-pill"><i class="fa-solid fa-link"></i> ${src.title}</a>`;
                        } else {
                            htmlContent += `<span class="source-pill"><i class="fa-solid fa-file-pdf"></i> ${src.title}</span>`;
                        }
                    });
                    htmlContent += `</div>`;
                }

                contentDiv.innerHTML = htmlContent;

                // 4. Footer Bar: Copy Button + Model Used + Response Time
                const footerDiv = document.createElement("div");
                footerDiv.className = "msg-footer";
                footerDiv.innerHTML = `
                    <button type="button" class="msg-action-btn copy-btn"><i class="fa-regular fa-copy"></i> Copy</button>
                    <span>• ${data.model_used || "Groq AI"}</span>
                    <span>• ⚡ ${data.response_time || "0.5s"}</span>
                `;
                footerDiv.querySelector(".copy-btn").addEventListener("click", (e) => {
                    navigator.clipboard.writeText(data.reply);
                    e.currentTarget.innerHTML = `<i class="fa-solid fa-check" style="color:#34d399;"></i> Copied!`;
                });
                msgBody.appendChild(footerDiv);

                // 5. Dynamic Follow-Up Suggestion Chips
                if (data.suggestions && data.suggestions.length > 0) {
                    const suggRow = document.createElement("div");
                    suggRow.className = "suggestions-row";
                    data.suggestions.forEach(sugg => {
                        const chip = document.createElement("button");
                        chip.type = "button";
                        chip.className = "suggestion-chip";
                        chip.innerHTML = `<i class="fa-solid fa-sparkles"></i> ${sugg}`;
                        chip.addEventListener("click", () => handleSendMessage(sugg));
                        suggRow.appendChild(chip);
                    });
                    msgBody.appendChild(suggRow);
                }

                chatHistory.push({ role: "assistant", content: data.reply });
            } else {
                contentDiv.innerHTML = `<p style="color:#f87171;">❌ Error: ${data.detail || "Failed to get response"}</p>`;
            }
        } catch (err) {
            contentDiv.innerHTML = `<p style="color:#f87171;">❌ Connection Error: ${err.message}</p>`;
        }
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    sendBtn.addEventListener("click", () => handleSendMessage());
    userInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    });

    // Voice Input (Web Speech API)
    if ("webkitSpeechRecognition" in window || "SpeechRecognition" in window) {
        const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRec();
        recognition.lang = "en-IN";
        recognition.interimResults = false;

        voiceBtn.addEventListener("click", () => {
            voiceBtn.classList.add("recording");
            recognition.start();
        });
        recognition.onresult = (e) => {
            userInput.value = e.results[0][0].transcript;
            voiceBtn.classList.remove("recording");
        };
        recognition.onerror = () => voiceBtn.classList.remove("recording");
        recognition.onend = () => voiceBtn.classList.remove("recording");
    } else {
        voiceBtn.style.display = "none";
    }

    // Export Chat as Markdown (.md)
    exportChatBtn.addEventListener("click", () => {
        if (chatHistory.length === 0) return;
        let md = `# Velo AI Chat Export (${sessionIdInput.value})\n\n`;
        chatHistory.forEach(m => {
            md += `### ${m.role === "user" ? "🧑 You" : "⚡ Velo AI"}\n${m.content}\n\n---\n\n`;
        });
        const blob = new Blob([md], { type: "text/markdown" });
        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = `${sessionIdInput.value}-chat.md`;
        a.click();
    });

    clearChatBtn.addEventListener("click", () => {
        chatMessages.innerHTML = "";
        appendMessage("Conversation cleared. How can I help you next?", "ai-message");
        chatHistory = [];
    });
});