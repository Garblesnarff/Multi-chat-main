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

    // Enhanced addMessage: supports user/AI, error, and provider/model label
    function addMessage(content, isUser = false, isError = false, provider = null, model = null) {
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
        // Provider/model label for AI
        if (!isUser && provider && model) {
            const label = document.createElement('div');
            label.className = 'text-xs font-semibold text-purple-600 mb-1';
            label.textContent = `${provider}: ${model}`;
            bubble.appendChild(label);
        }
        // Message content
        const contentDiv = document.createElement('div');
        contentDiv.textContent = content;
        bubble.appendChild(contentDiv);
        messageDiv.appendChild(bubble);
        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
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
        console.log('sendMessage function called');
        const message = userInput.value.trim();
        console.log('User input:', message);
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
                        if (!providerResponses[currentProvider]) {
                            providerResponses[currentProvider] = '';
                            const providerDiv = document.createElement('div');
                            providerDiv.id = `streaming-${currentProvider}`;
                            providerDiv.innerHTML = `
                                <h3 class="font-bold text-lg mb-2">${currentProvider.charAt(0).toUpperCase() + currentProvider.slice(1)}</h3>
                                <p class="bg-white rounded p-2"></p>
                            `;
                            comparisonContainer.appendChild(providerDiv);
                        }
                    } else {
                        providerResponses[currentProvider] += event.data;
                        const providerDiv = document.getElementById(`streaming-${currentProvider}`);
                        if (providerDiv) {
                            const responseP = providerDiv.querySelector('p');
                            responseP.textContent = providerResponses[currentProvider];
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
                            displayComparison(data.responses);
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
});
