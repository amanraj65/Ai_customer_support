async function getResponse() {
    const userQuestion = document.getElementById("questionInput").value.trim();
    const chatMessages = document.getElementById("chat-messages");

    if (!userQuestion) {
        return;
    }

    // Display user message in chat
    appendMessage("You: " + userQuestion, "user-message");

    // Show "typing..." effect
    const typingMessage = appendMessage("AI is thinking...", "bot-message");

    try {
        const res = await fetch(`http://127.0.0.1:8000/chat?user_question=${encodeURIComponent(userQuestion)}`);

        if (!res.ok) {
            throw new Error(`Server responded with ${res.status}`);
        }

        const data = await res.json();
        typingMessage.remove(); // Remove "typing..." message
        appendMessage("AI: " + data.response, "bot-message");
    } catch (error) {
        typingMessage.remove();
        appendMessage("Error: Failed to get response.", "bot-message");
    }

    document.getElementById("questionInput").value = ""; // Clear input
}

// Function to append a message to the chat
function appendMessage(text, className) {
    const chatMessages = document.getElementById("chat-messages");
    const messageElement = document.createElement("div");
    messageElement.className = `message ${className}`;
    messageElement.innerHTML = text.replace(/\n/g, "<br>"); // Preserve line breaks
    chatMessages.appendChild(messageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight; // Auto-scroll to bottom
    return messageElement;
}

// Allow sending message with "Enter" key
function handleKeyPress(event) {
    if (event.key === "Enter") {
        getResponse();
    }
}