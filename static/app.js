document.addEventListener('DOMContentLoaded', () => {
    // State
    let currentThreadId = null;

    // DOM Elements
    const threadsListEl = document.getElementById('threads-list');
    const newChatBtn = document.getElementById('new-chat-btn');
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const messagesContainer = document.getElementById('messages-container');
    const welcomeContainer = document.getElementById('welcome-container');
    const messagesListEl = document.getElementById('messages-list');
    const typingIndicator = document.getElementById('typing-indicator');
    const currentChatTitle = document.getElementById('current-chat-title');
    const routeIndicator = document.getElementById('route-indicator');
    const routeText = document.getElementById('route-text');
    const uploadDropzone = document.getElementById('upload-dropzone');
    const fileInput = document.getElementById('file-input');
    const uploadStatus = document.getElementById('upload-status');
    const uploadStatusText = document.getElementById('upload-status-text');
    const clearViewBtn = document.getElementById('clear-view-btn');

    // Configure Marked JS with Highlight.js
    if (window.marked) {
        marked.setOptions({
            highlight: function(code, lang) {
                if (lang && hljs.getLanguage(lang)) {
                    return hljs.highlight(code, { language: lang }).value;
                }
                return hljs.highlightAuto(code).value;
            },
            breaks: true,
        });
    }

    // Auto-resize Textarea & Toggle Send Button
    userInput.addEventListener('input', () => {
        userInput.style.height = 'auto';
        userInput.style.height = Math.min(userInput.scrollHeight, 150) + 'px';
        sendBtn.disabled = userInput.value.trim() === '';
    });

    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (userInput.value.trim() !== '') {
                chatForm.dispatchEvent(new Event('submit'));
            }
        }
    });

    // Form Submit (Send Message)
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const messageText = userInput.value.trim();
        if (!messageText) return;

        // Reset input
        userInput.value = '';
        userInput.style.height = 'auto';
        sendBtn.disabled = true;

        await sendUserMessage(messageText);
    });

    // New Chat Button
    newChatBtn.addEventListener('click', () => {
        resetChatView();
    });

    // Clear View Button
    clearViewBtn.addEventListener('click', () => {
        resetChatView();
    });

    // Suggestion Cards Click
    document.querySelectorAll('.suggestion-card').forEach(card => {
        card.addEventListener('click', () => {
            const prompt = card.getAttribute('data-prompt');
            if (prompt) {
                sendUserMessage(prompt);
            }
        });
    });

    // Upload Dropzone Click
    uploadDropzone.addEventListener('click', () => {
        fileInput.click();
    });

    // File Input Change
    fileInput.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (file) {
            await handleFileUpload(file);
        }
    });

    // Drag & Drop File
    uploadDropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadDropzone.style.borderColor = 'var(--accent-color)';
    });

    uploadDropzone.addEventListener('dragleave', () => {
        uploadDropzone.style.borderColor = 'var(--border-color)';
    });

    uploadDropzone.addEventListener('drop', async (e) => {
        e.preventDefault();
        uploadDropzone.style.borderColor = 'var(--border-color)';
        if (e.dataTransfer.files.length > 0) {
            const file = e.dataTransfer.files[0];
            await handleFileUpload(file);
        }
    });

    // API Functions

    async function fetchThreads() {
        try {
            const res = await fetch('/api/threads');
            if (!res.ok) return;
            const threads = await res.json();
            renderThreadsList(threads);
        } catch (err) {
            console.error('Failed to fetch threads:', err);
        }
    }

    function renderThreadsList(threads) {
        threadsListEl.innerHTML = '';
        if (threads.length === 0) {
            threadsListEl.innerHTML = '<li class="thread-item" style="color: var(--text-dim); font-size:12px;">No past conversations</li>';
            return;
        }

        threads.forEach(t => {
            const li = document.createElement('li');
            li.className = `thread-item ${t.id === currentThreadId ? 'active' : ''}`;
            li.innerHTML = `
                <i class="fa-regular fa-message" style="margin-right: 8px;"></i>
                <span class="thread-item-title">${escapeHtml(t.title)}</span>
                <button class="btn-delete-thread" title="Delete thread" data-id="${t.id}">
                    <i class="fa-solid fa-trash-can"></i>
                </button>
            `;

            li.addEventListener('click', (e) => {
                if (e.target.closest('.btn-delete-thread')) return;
                loadThread(t.id);
            });

            const deleteBtn = li.querySelector('.btn-delete-thread');
            deleteBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                deleteThread(t.id);
            });

            threadsListEl.appendChild(li);
        });
    }

    async function loadThread(threadId) {
        try {
            const res = await fetch(`/api/threads/${threadId}`);
            if (!res.ok) return;
            const data = await res.json();

            currentThreadId = data.id;
            currentChatTitle.textContent = data.title;
            welcomeContainer.classList.add('hidden');
            messagesListEl.innerHTML = '';

            data.messages.forEach(m => {
                appendMessageBubble(m.role, m.content);
            });

            routeIndicator.classList.add('hidden');
            scrollToBottom();
            fetchThreads();
        } catch (err) {
            console.error('Failed to load thread:', err);
        }
    }

    async function deleteThread(threadId) {
        if (!confirm('Are you sure you want to delete this conversation?')) return;
        try {
            const res = await fetch(`/api/threads/${threadId}`, { method: 'DELETE' });
            if (res.ok) {
                if (currentThreadId === threadId) {
                    resetChatView();
                }
                fetchThreads();
            }
        } catch (err) {
            console.error('Failed to delete thread:', err);
        }
    }

    function resetChatView() {
        currentThreadId = null;
        currentChatTitle.textContent = 'New Chat';
        routeIndicator.classList.add('hidden');
        messagesListEl.innerHTML = '';
        welcomeContainer.classList.remove('hidden');
        fetchThreads();
    }

    async function sendUserMessage(text) {
        // Hide welcome screen
        welcomeContainer.classList.add('hidden');

        // Append User Message Bubble
        appendMessageBubble('user', text);

        // Show Typing Indicator
        typingIndicator.classList.remove('hidden');
        scrollToBottom();

        try {
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    thread_id: currentThreadId,
                    message: text,
                }),
            });

            typingIndicator.classList.add('hidden');

            if (!res.ok) {
                const errData = await res.json();
                appendMessageBubble('assistant', `⚠️ Error: ${errData.detail || 'Failed to get response.'}`);
                return;
            }

            const data = await res.json();

            // Update thread state
            currentThreadId = data.thread_id;
            if (data.title) {
                currentChatTitle.textContent = data.title;
            }

            // Update Route Badge
            if (data.route) {
                routeIndicator.className = `route-badge ${data.route}`;
                routeText.textContent = data.route === 'rag' ? 'RAG: Document Match' : 'Direct LLM';
                routeIndicator.classList.remove('hidden');
            }

            // Append Assistant Message Bubble
            appendMessageBubble('assistant', data.answer, data.route);

            // Refresh thread sidebar list
            fetchThreads();
        } catch (err) {
            typingIndicator.classList.add('hidden');
            appendMessageBubble('assistant', `⚠️ Error: Network request failed (${err.message}).`);
            console.error('Chat error:', err);
        }
    }

    function appendMessageBubble(role, content, route = null) {
        const row = document.createElement('div');
        row.className = `message-row ${role === 'user' ? 'user-row' : 'assistant-row'}`;

        const avatar = document.createElement('div');
        avatar.className = `avatar ${role === 'user' ? 'user-avatar' : 'assistant-avatar'}`;
        avatar.innerHTML = role === 'user' ? '<i class="fa-solid fa-user"></i>' : '<i class="fa-solid fa-robot"></i>';

        const wrapper = document.createElement('div');
        wrapper.className = 'message-bubble-wrapper';

        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';

        if (role === 'user') {
            bubble.textContent = content;
        } else {
            // Render Assistant response with Markdown
            if (window.marked) {
                bubble.innerHTML = marked.parse(content);
            } else {
                bubble.textContent = content;
            }
        }

        wrapper.appendChild(bubble);

        // Metadata / route info
        const meta = document.createElement('div');
        meta.className = 'message-meta';
        if (role === 'assistant' && route) {
            meta.innerHTML = `<span>${route === 'rag' ? '🔍 Document RAG Search' : '💬 Direct Model'}</span>`;
            wrapper.appendChild(meta);
        }

        row.appendChild(avatar);
        row.appendChild(wrapper);

        messagesListEl.appendChild(row);

        // Apply syntax highlighting to code blocks
        if (role === 'assistant' && window.hljs) {
            bubble.querySelectorAll('pre code').forEach((block) => {
                hljs.highlightElement(block);
            });
        }

        scrollToBottom();
    }

    async function handleFileUpload(file) {
        const formData = new FormData();
        formData.append('file', file);

        uploadStatus.classList.remove('hidden');
        uploadStatusText.textContent = `Uploading ${file.name}...`;

        try {
            const res = await fetch('/api/upload', {
                method: 'POST',
                body: formData,
            });

            if (res.ok) {
                const data = await res.json();
                uploadStatusText.textContent = `Uploaded ${file.name}!`;
                setTimeout(() => {
                    uploadStatus.classList.add('hidden');
                }, 3000);
            } else {
                const errData = await res.json();
                alert(`Upload failed: ${errData.detail || 'Server error'}`);
                uploadStatus.classList.add('hidden');
            }
        } catch (err) {
            alert(`Upload error: ${err.message}`);
            uploadStatus.classList.add('hidden');
        }
    }

    function scrollToBottom() {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function escapeHtml(str) {
        if (!str) return '';
        return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    }

    // Initial Load
    fetchThreads();
});
