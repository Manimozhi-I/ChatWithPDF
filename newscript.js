document.addEventListener("DOMContentLoaded", () => {

    const API_BASE = "http://127.0.0.1:5000";
    const HISTORY_KEY = "docchat_history";

    // OM ELEMENTS
    const uploadBtn = document.getElementById("uploadBtn");
    const docUpload = document.getElementById("docUpload");
    const uploadStatus = document.getElementById("uploadStatus");

    const clearBtn = document.getElementById("clearBtn");

    const chatButton = document.getElementById("chatButton");
    const chatBox = document.getElementById("chatBox");
    const chatMessages = document.getElementById("chatMessages");
    const chatInput = document.getElementById("chatInput");
    const sendButton = document.getElementById("sendMessage");

    if (!chatButton || !chatBox || !chatMessages || !chatInput || !sendButton) {
        console.error("Chat elements missing in DOM.");
        return;
    }

    //HISTORY HELPERS
    function getHistory() {
        const raw = localStorage.getItem(HISTORY_KEY);
        if (!raw) return [];
        try {
            return JSON.parse(raw);
        } catch (e) {
            console.error("Failed to parse history:", e);
            return [];
        }
    }

    function setHistory(history) {
        try {
            localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
        } catch (e) {
            console.error("Failed to save history:", e);
        }
    }

    //MESSAGE RENDERING
    function addMessage(sender, text, type, saveToHistory = true) {
        const row = document.createElement("div");
        row.classList.add("message-row");
        if (type === "user") {
            row.classList.add("user");
        } else {
            row.classList.add("assistant");
        }

        const avatar = document.createElement("div");
        avatar.classList.add("avatar");
        if (type === "user") {
            avatar.classList.add("user-avatar");
            avatar.textContent = "You";
        } else {
            avatar.classList.add("assistant-avatar");
            avatar.textContent = "AI";
        }

        const bubble = document.createElement("div");
        bubble.classList.add("message-bubble");
        if (type === "user") {
            bubble.classList.add("user-bubble");
        } else {
            bubble.classList.add("assistant-bubble");
        }

        const label = document.createElement("div");
        label.classList.add("message-label");
        label.textContent = type === "user" ? "You" : "Assistant";

        const textDiv = document.createElement("div");
        textDiv.classList.add("message-text");
        textDiv.textContent = text;

        bubble.appendChild(label);
        bubble.appendChild(textDiv);

        row.appendChild(avatar);
        row.appendChild(bubble);

        chatMessages.appendChild(row);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        if (saveToHistory) {
            const history = getHistory();
            history.push({ type, text });
            setHistory(history);
        }
    }

    // REBUILD CHAT FROM HISTORY
    const existingHistory = getHistory();
    if (existingHistory.length > 0) {
        // Remove the default hardcoded welcome message from HTML
        chatMessages.innerHTML = "";
        existingHistory.forEach(msg => {
            const who = msg.type === "user" ? "You" : "Assistant";
            addMessage(who, msg.text, msg.type, false); // don't re-save
        });
    }

    //CHAT TOGGLE
    chatButton.addEventListener("click", () => {
        chatBox.style.display = chatBox.style.display === "flex" ? "none" : "flex";
    });

    //CLEAR DOCUMENTS + CHAT 
    if (clearBtn) {
        clearBtn.addEventListener("click", async () => {
            try {
                const res = await fetch(`${API_BASE}/clear-documents`, {
                    method: "POST"
                });

                if (!res.ok) {
                    console.error("clear-documents HTTP error:", res.status);
                    if (uploadStatus) {
                        uploadStatus.textContent =
                            `Server error clearing documents (${res.status}).`;
                        uploadStatus.style.color = "red";
                    }
                    return;
                }

                let data = {};
                try {
                    data = await res.json();
                } catch (e) {
                    console.warn("clear-documents response not JSON.");
                }

                if (uploadStatus) {
                    uploadStatus.textContent = data.message || "All documents cleared!";
                    uploadStatus.style.color = "orange";
                }

                // wipe history + UI
                localStorage.removeItem(HISTORY_KEY);
                chatMessages.innerHTML = "";

                
                addMessage(
                    "Assistant",
                    "All documents and chat history are cleared. Upload new files and start a fresh chat.",
                    "assistant",
                    false
                );

                if (docUpload) {
                    docUpload.value = "";
                }

            } catch (err) {
                console.error("Clear error:", err);
                if (uploadStatus) {
                    uploadStatus.textContent = "Error clearing documents.";
                    uploadStatus.style.color = "red";
                }
            }
        });
    }

    // UPLOAD DOCUMENTS
    if (uploadBtn) {
        uploadBtn.addEventListener("click", async () => {
            const files = Array.from(docUpload.files || []);

            if (!files.length) {
                if (uploadStatus) {
                    uploadStatus.textContent = "Please select at least one document.";
                    uploadStatus.style.color = "red";
                }
                return;
            }

            if (uploadStatus) {
                uploadStatus.textContent = "Uploading...";
                uploadStatus.style.color = "#0d6efd";
            }

            let successCount = 0;

            for (const file of files) {
                const formData = new FormData();
                formData.append("file", file);

                try {
                    const res = await fetch(`${API_BASE}/upload-document`, {
                        method: "POST",
                        body: formData
                    });

                    if (!res.ok) {
                        console.error("upload-document HTTP error:", res.status);
                        continue;
                    }

                    const data = await res.json();
                    if (data.message) successCount += 1;

                } catch (err) {
                    console.error("Upload error:", err);
                }
            }

            if (!uploadStatus) return;

            if (successCount === files.length) {
                uploadStatus.textContent =
                    `${successCount} document${successCount > 1 ? "s" : ""} uploaded successfully!`;
                uploadStatus.style.color = "green";
            } else if (successCount > 0) {
                uploadStatus.textContent =
                    `${successCount} of ${files.length} documents uploaded. Some failed.`;
                uploadStatus.style.color = "orange";
            } else {
                uploadStatus.textContent = "Upload failed!";
                uploadStatus.style.color = "red";
            }
        });
    }

    //SEND MESSAGE
    async function sendMessage() {
        const message = chatInput.value.trim();
        if (!message) return;

        addMessage("You", message, "user");
        chatInput.value = "";

        try {
            const res = await fetch(`${API_BASE}/chatbot`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message })
            });

            if (!res.ok) {
                console.error("chatbot HTTP error:", res.status);
                addMessage(
                    "Assistant",
                    `Server error (${res.status}) while generating a response.`,
                    "assistant"
                );
                return;
            }

            const data = await res.json();
            addMessage(
                "Assistant",
                data.response || "No response from server.",
                "assistant"
            );
        } catch (err) {
            console.error("Chat error:", err);
            addMessage(
                "Assistant",
                    "There was an error reaching the server.",
                "assistant"
            );
        }
    }

    sendButton.addEventListener("click", sendMessage);
    chatInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") sendMessage();
    });
});
