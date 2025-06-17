document.addEventListener('DOMContentLoaded', () => {
    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');

    function addMessageToChatbox(message, type) { // type can be 'user', 'bot', or 'error'
        const messageElement = document.createElement('div');
        messageElement.classList.add('message');
        if (type === 'user') {
            messageElement.classList.add('user-message');
        } else if (type === 'bot') {
            messageElement.classList.add('bot-message');
        } else if (type === 'error') {
            messageElement.classList.add('error-message'); // Add a new class for error styling
        }
        messageElement.textContent = message;
        chatBox.appendChild(messageElement);
        chatBox.scrollTop = chatBox.scrollHeight; // Auto-scroll to the bottom
    }

    async function handleSendMessage() {
        const messageText = userInput.value.trim();
        if (messageText) {
            addMessageToChatbox(messageText, 'user');
            userInput.value = '';

            try {
                const response = await fetch('/send_message', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: messageText }),
                });

                if (!response.ok) {
                    // Network or HTTP error (e.g. 500, 404)
                    // Try to get error message from backend if it sent one, otherwise generic
                    let errorMsg = `Error: Server responded with status ${response.status}.`;
                    try {
                        const errorData = await response.json();
                        if (errorData && errorData.error) {
                            errorMsg = errorData.error;
                        }
                    } catch (e) {
                        // Backend didn't send JSON or it was unparseable
                        errorMsg = `Error: Received an invalid response from the server (status ${response.status}).`;
                    }
                    addMessageToChatbox(errorMsg, 'error');
                    return;
                }

                const data = await response.json();
                if (data.error) {
                    addMessageToChatbox(data.error, 'error');
                } else if (data.reply) {
                    addMessageToChatbox(data.reply, 'bot');
                } else {
                    addMessageToChatbox('Error: Received an unexpected response structure from the server.', 'error');
                }

            } catch (error) { // Catches network errors (e.g., server down) or JS errors in try block
                console.error('Error sending message:', error);
                if (error instanceof TypeError && error.message.includes('NetworkError')) {
                     addMessageToChatbox('Error: Could not connect to the server. Please check your network or try again later.', 'error');
                } else if (error instanceof SyntaxError) {
                    addMessageToChatbox('Error: Received an unparseable response from the server.', 'error');
                }
                else {
                    addMessageToChatbox('An unexpected error occurred. Please try again.', 'error');
                }
            }
        } else {
            // Optionally, provide feedback if the user tries to send an empty message,
            // though the backend will also validate this.
            // addMessageToChatbox("Please type a message.", 'error');
        }
    }

    sendButton.addEventListener('click', handleSendMessage);
    userInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            handleSendMessage();
        }
    });
});
