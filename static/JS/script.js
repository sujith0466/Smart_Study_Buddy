const socket = io();
window.onload = function() {
    setInitialTheme();
    loadChatHistory();
    focusInput();
};

document.getElementById('send-button').addEventListener('click', sendMessage);
document.getElementById('theme').addEventListener('change', toggleTheme);
document.getElementById('user-input').addEventListener('keydown', handleKeyPress);

function sendMessage() {
    const userInputField = document.getElementById('user-input');
    const userInput = userInputField.value.trim();
    if (userInput) {
        appendMessage('You', userInput, 'user');
        socket.emit('message', { message: userInput });
        saveMessageToHistory('You', userInput);
        userInputField.value = '';
        userInputField.style.height = 'auto'; // Reset height
    }
}

function handleKeyPress(event) {
    const input = document.getElementById('user-input');

    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault(); // Prevent newline
        sendMessage();
    } else if (event.key === 'Escape') {
        input.value = '';
        input.style.height = 'auto';
    } else {
        // Auto-grow textarea height
        input.style.height = 'auto';
        input.style.height = input.scrollHeight + 'px';
    }
}

socket.on('response', function (data) {
    showTypingIndicator();
    setTimeout(() => {
        removeTypingIndicator();
        appendMessage('Bot', data.message, 'bot');
        saveMessageToHistory('Bot', data.message);
        vibrate();
        speakText(data.message);  // Speak bot's message
    }, 1000);
});

function getCurrentTime() {
    const now = new Date();
    return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function appendMessage(sender, message, type) {
    const chatbox = document.getElementById('chatbox');
    const msg = document.createElement('div');
    msg.className = 'chat-message fade-in';
    msg.setAttribute('aria-live', 'polite');

    const avatar = document.createElement('img');
    avatar.src = type === 'user' ? '/static/img/user.png' : '/static/img/bot.png';
    avatar.alt = type === 'user' ? 'User' : 'Bot';

    const bubble = document.createElement('div');
    bubble.className = type === 'user' ? 'user-message' : 'bot-message';
    bubble.innerHTML = parseMarkdown(message);

    const timestamp = document.createElement('div');
    timestamp.className = 'timestamp';
    timestamp.innerText = getCurrentTime();

    bubble.appendChild(timestamp);
    msg.appendChild(avatar);
    msg.appendChild(bubble);

    chatbox.appendChild(msg);
    chatbox.scrollTop = chatbox.scrollHeight;
    focusInput();
}

// In your script.js, render buttons and messages dynamically
function renderResponse(response) {
    var responseContainer = document.getElementById("response-container");
    var messageDiv = document.createElement("div");
    messageDiv.textContent = response.message;
    responseContainer.appendChild(messageDiv);

    response.buttons.forEach(button => {
        var buttonElement = document.createElement("button");
        buttonElement.textContent = button.text;
        buttonElement.onclick = function () {
            window.location.href = button.url;
        };
        responseContainer.appendChild(buttonElement);
    });
}

function showTypingIndicator() {
    if (!document.getElementById('typing')) {
        const chatbox = document.getElementById('chatbox');
        const typing = document.createElement('div');
        typing.id = 'typing';
        typing.className = 'chat-message fade-in';
        typing.innerHTML = '<img class="avatar" src="/static/img/bot.png"><span><i>Typing...</i></span>';
        chatbox.appendChild(typing);
        chatbox.scrollTop = chatbox.scrollHeight;
    }
}

function removeTypingIndicator() {
    const typing = document.getElementById('typing');
    if (typing) {
        typing.remove();
    }
}

function vibrate() {
    if (navigator.vibrate) {
        navigator.vibrate(100);  // Vibrate for 100ms
    }
}

function parseMarkdown(text) {
    // Using the marked library to parse the markdown
    return marked(text);
}

function speakText(text) {
    if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(text);
        speechSynthesis.speak(utterance);
    }
}

function toggleTheme() {
    document.body.classList.toggle('light');
    localStorage.setItem('theme', document.body.classList.contains('light') ? 'light' : 'dark');
}

function setInitialTheme() {
    const savedTheme = localStorage.getItem('theme');
    const themeToggle = document.getElementById('theme');
    if (savedTheme === 'light') {
        document.body.classList.add('light');
        themeToggle.checked = false;
    } else {
        document.body.classList.remove('light');
        themeToggle.checked = true;
    }
}

function focusInput() {
    document.getElementById('user-input').focus();
}

function loadChatHistory() {
    const chatHistory = JSON.parse(localStorage.getItem('chatHistory')) || [];
    if (chatHistory.length === 0) {
        // Show welcome message if no history
        appendMessage('Bot', '👋 Hi! I am your Smart Study Buddy. How can I help you today?', 'bot');
    } else {
        chatHistory.forEach(item => {
            appendMessage(item.sender, item.message, item.type);
        });
    }
}

function saveMessageToHistory(sender, message) {
    const chatHistory = JSON.parse(localStorage.getItem('chatHistory')) || [];
    chatHistory.push({ sender, message, type: sender === 'You' ? 'user' : 'bot' });
    localStorage.setItem('chatHistory', JSON.stringify(chatHistory));
}

// Clear chat history when the button is clicked
document.getElementById('clear-chat').addEventListener('click', clearChat);

function clearChat() {
    const chatbox = document.getElementById('chatbox');
    chatbox.innerHTML = '';
    localStorage.removeItem('chatHistory');
    appendMessage('Bot', '👋 Hi! I am your Smart Study Buddy. How can I help you today?', 'bot');
}
