console.log('main.js loaded');// main.js - Client-side JavaScript for EchoChat UI
// Handles user interactions, sending chat requests, and updating the UI.
//
// Dependencies:
// - Vanilla JavaScript
//
// See also: /app/routes/chat_routes.py for backend chat logic

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOMContentLoaded event fired');
    const chatContainer = document.getElementById('chat-container');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const clearHistoryBtn = document.getElementById('clear-history-btn');
    const providerSelects = document.querySelectorAll('.provider-select');
    const comparisonContainer = document.getElementById('comparison-container');
    const reasoningCheckbox = document.getElementById('reasoning-checkbox');
    const streamingCheckbox = document.getElementById('streaming-checkbox');
    const responseGrid = document.getElementById('response-grid');
    const responsePanelTemplate = document.getElementById('response-panel-template');

    // Enhanced addMessage: supports user/AI, error, and provider/model label
    function addMessage(content, isUser = false, isError = false, provider = null, model = null) {
        if (responseGrid && responseGrid.children.length > 0) {
            // Route to correct panel(s)
            if (isUser) {
                // Add user message to all panels
                Array.from(responseGrid.children).forEach(panel => {
                    const msg = createMessageBubble(content, true, isError, provider, model);
                    panel.querySelector('.messages').appendChild(msg);
                    panel.querySelector('.messages').scrollTop = panel.querySelector('.messages').scrollHeight;
                });
            } else if (provider) {
                // Add provider response only to its panel
                const panel = Array.from(responseGrid.children).find(p => p.dataset.provider === provider);
                if (panel) {
                    const msg = createMessageBubble(content, false, isError, provider, model);
                    panel.querySelector('.messages').appendChild(msg);
                    panel.querySelector('.messages').scrollTop = panel.querySelector('.messages').scrollHeight;
                }
            }
        } else {
            // Fallback: old chatContainer
            const messageDiv = document.createElement('div');
            messageDiv.classList.add('flex', isUser ? 'justify-end' : 'justify-start');
            // Bubble
            const bubble = document.createElement('div');
            bubble.classList.add(
                'max-w-[75%]',
                'rounded-xl',
                'px-4',
                'py-2',
                'mb-1',
                'shadow',
                'whitespace-pre-line',
                'break-words',
                ...(
                    isUser
                        ? ['bg-blue-500', 'text-white', 'self-end']
                        : ['bg-gray-100', 'text-gray-900', 'self-start']
                ),
                ...(
                    isError
                        ? ['border', 'border-red-400', 'text-red-700', 'bg-red-50']
                        : []
                )
            );
            if (!isUser && provider && model) {
                const label = document.createElement('div');
                label.className = 'text-xs font-semibold text-purple-600 mb-1';
                label.textContent = `${provider}: ${model}`;
                bubble.appendChild(label);
            }
            const contentDiv = document.createElement('div');
            contentDiv.textContent = content;
            bubble.appendChild(contentDiv);
            messageDiv.appendChild(bubble);
            if (chatContainer) {
                chatContainer.appendChild(messageDiv);
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }
        }
    }

    function createMessageBubble(content, isUser, isError, provider, model) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('flex', isUser ? 'justify-end' : 'justify-start');
        const bubble = document.createElement('div');
        bubble.classList.add(
            'max-w-[75%]',
            'rounded-xl',
            'px-4',
            'py-2',
            'mb-1',
            'shadow',
            'whitespace-pre-line',
            'break-words',
            ...(isUser ? ['bg-blue-500', 'text-white', 'self-end'] : ['bg-gray-100', 'text-gray-900', 'self-start']),
            ...(isError ? ['border', 'border-red-400', 'text-red-700', 'bg-red-50'] : [])
        );
        if (!isUser && provider && model) {
            const label = document.createElement('div');
            label.className = 'text-xs font-semibold text-purple-600 mb-1';
            label.textContent = `${provider}: ${model}`;
            bubble.appendChild(label);
        }
        const contentDiv = document.createElement('div');
        contentDiv.textContent = content;
        bubble.appendChild(contentDiv);
        messageDiv.appendChild(bubble);
        return messageDiv;
    }

    function getProviderColor(provider) {
        // Assign a consistent color per provider (Tailwind palette)
        const colorMap = {
            groq: '#6366f1',      // Indigo-500
            gemini: '#06b6d4',    // Cyan-500
            cerebras: '#f59e42',  // Orange-400
        };
        return colorMap[provider] || '#6366f1';
    }

    function updateResponseGrid() {
        // Clear grid
        responseGrid.innerHTML = '';
        const selectedProviders = getSelectedProviders();
        const providerKeys = Object.keys(selectedProviders);
        if (providerKeys.length === 0) {
            responseGrid.className = 'grid gap-4 mb-6';
            return;
        }
        // Set grid columns
        responseGrid.className = `grid gap-4 mb-6 grid-cols-${providerKeys.length}`;
        providerKeys.forEach(provider => {
            // Clone panel template
            const panel = responsePanelTemplate.firstElementChild.cloneNode(true);
            panel.classList.remove('hidden');
            panel.dataset.provider = provider;
            // Set provider header
            const header = panel.querySelector('.provider-header');
            header.textContent = provider.charAt(0).toUpperCase() + provider.slice(1);
            header.style.backgroundColor = getProviderColor(provider);
            // Clear messages
            panel.querySelector('.messages').innerHTML = '';
            responseGrid.appendChild(panel);
        });
    }

    function getSelectedProviders() {
        const selectedProviders = {};
        providerSelects.forEach(select => {
            if (select.value) {
                const provider = select.id.split('-')[0];
                selectedProviders[provider] = select.value;
            }
        });
        return selectedProviders;
    }

    // Modified displayComparison: append each AI response as a bubble
    function displayComparison(responses) {
        const selectedProviders = getSelectedProviders();
        for (const [provider, data] of Object.entries(responses)) {
            // If response is an object with model & content, use them; else fallback
            let model = null, content = '';
            if (typeof data === 'object' && data !== null && ('model' in data) && ('content' in data)) {
                model = data.model;
                content = data.content;
            } else {
                // Use the selected model from the dropdown for this provider
                model = selectedProviders[provider] || '';
                content = data;
            }
            addMessage(content, false, String(content).startsWith('Error:'), provider.charAt(0).toUpperCase() + provider.slice(1), model);
        }
    }

    async function sendMessage() {
        updateResponseGrid();
        const message = userInput.value.trim();
        const selectedProviders = getSelectedProviders();
        const useReasoning = reasoningCheckbox && reasoningCheckbox.checked;
        const useStreaming = streamingCheckbox && streamingCheckbox.checked;

        if (message && Object.keys(selectedProviders).length > 0) {
            addMessage(message, true);
            userInput.value = '';

            if (useStreaming) {
                comparisonContainer.innerHTML = '';
                comparisonContainer.classList.remove('hidden');
                
                const eventSource = new EventSource(`/chat?message=${encodeURIComponent(message)}&providers=${encodeURIComponent(JSON.stringify(selectedProviders))}&use_reasoning=${useReasoning}&use_streaming=true`);
                
                let currentProvider = '';
                let providerResponses = {};

                eventSource.onmessage = function(event) {
                    if (event.data === '[DONE]') {
                        currentProvider = '';
                    } else if (currentProvider === '') {
                        currentProvider = event.data;
                        providerResponses[currentProvider] = '';
                    } else {
                        providerResponses[currentProvider] += event.data;
                        // Update in the correct panel
                        const panel = Array.from(responseGrid.children).find(p => p.dataset.provider === currentProvider);
                        if (panel) {
                            let msgList = panel.querySelector('.messages');
                            let lastMsg = msgList.lastElementChild;
                            if (!lastMsg || !lastMsg.classList.contains('ai-stream')) {
                                // New streaming bubble
                                const bubble = document.createElement('div');
                                bubble.className = 'ai-stream flex justify-start';
                                const inner = document.createElement('div');
                                inner.className = 'max-w-[75%] rounded-xl px-4 py-2 mb-1 shadow whitespace-pre-line break-words bg-gray-100 text-gray-900 self-start';
                                inner.textContent = '';
                                bubble.appendChild(inner);
                                msgList.appendChild(bubble);
                                lastMsg = bubble;
                            }
                            lastMsg.querySelector('div').textContent = providerResponses[currentProvider];
                            msgList.scrollTop = msgList.scrollHeight;
                        }
                    }
                };

                eventSource.onerror = function(event) {
                    console.error('EventSource failed:', event);
                    eventSource.close();
                    addMessage('Error: Unable to get a streaming response from the server.', false, true);
                };
            } else {
                try {
                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ 
                            message, 
                            providers: selectedProviders, 
                            use_reasoning: useReasoning, 
                            use_streaming: useStreaming 
                        }),
                    });

                    if (response.ok) {
                        const data = await response.json();
                        if (data.error) {
                            addMessage(`Error: ${data.error}`, false, true);
                        } else {
                            // Route each response to its panel
                            const responses = data.responses;
                            Object.entries(responses).forEach(([provider, resp]) => {
                                let model = null, content = '';
                                if (typeof resp === 'object' && resp !== null && ('model' in resp) && ('content' in resp)) {
                                    model = resp.model;
                                    content = resp.content;
                                } else {
                                    model = selectedProviders[provider] || '';
                                    content = resp;
                                }
                                addMessage(content, false, String(content).startsWith('Error:'), provider, model);
                            });
                        }
                    } else {
                        const errorData = await response.json();
                        addMessage(`Error: ${errorData.error || 'Unable to get a response from the server.'}`, false, true);
                    }
                } catch (error) {
                    console.error('Error:', error);
                    addMessage('Error: Unable to connect to the server.', false, true);
                }
            }
        } else if (Object.keys(selectedProviders).length === 0) {
            addMessage('Please select at least one provider and model.', false, true);
        }
    }

    async function clearHistory() {
        const selectedProviders = getSelectedProviders();
        for (const provider of Object.keys(selectedProviders)) {
            try {
                const response = await fetch('/clear_history', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ provider }),
                });

                if (response.ok) {
                    console.log(`Cleared history for ${provider}`);
                } else {
                    console.error(`Failed to clear history for ${provider}`);
                    const errorData = await response.json();
                    addMessage(`Error clearing history for ${provider}: ${errorData.error}`, false, true);
                }
            } catch (error) {
                console.error('Error:', error);
                addMessage(`Error clearing history for ${provider}: ${error.message}`, false, true);
            }
        }

        chatContainer.innerHTML = '';
        comparisonContainer.innerHTML = '';
        comparisonContainer.classList.add('hidden');
        addMessage('Conversation history cleared.');
    }

    providerSelects.forEach(select => {
        select.addEventListener('change', updateResponseGrid);
    });

    if (sendBtn) {
        sendBtn.addEventListener('click', () => {
            console.log('Send button clicked');
            sendMessage();
        });
    }
    
    if (userInput) {
        userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                console.log('Enter key pressed');
                sendMessage();
            }
        });
    }

    if (clearHistoryBtn) {
        clearHistoryBtn.addEventListener('click', clearHistory);
    }

    updateResponseGrid();
});
