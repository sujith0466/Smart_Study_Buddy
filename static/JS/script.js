// --- Study Buddy Chat Script ---
// Improvements: input sanitization, error handling, null checks, redundant save prevention, comments

// Requires: marked.js (for Markdown), DOMPurify (for XSS protection), socket.io

const socket = io();
let userId = localStorage.getItem("user_id") || `user_${Date.now()}`;
localStorage.setItem("user_id", userId);

// On page load, initialize theme, load chat history, and set up UI events
window.onload = () => {
  initTheme();
  loadHistory();
  setupEvents();
};

// Attach event listeners to UI elements
function setupEvents() {
  const sendBtn = document.getElementById("send-button");
  const clearBtn = document.getElementById("clear-chat");
  const micBtn = document.getElementById("mic-button");
  const themeToggle = document.getElementById("themeToggle");
  const userInput = document.getElementById("user-input");

  if (sendBtn) sendBtn.onclick = sendMessage;
  if (clearBtn) clearBtn.onclick = clearChat;
  if (micBtn && typeof speakInput === "function") micBtn.onclick = () => speakInput();
  if (themeToggle) themeToggle.onchange = toggleTheme;
  if (userInput) {
    userInput.onkeydown = (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    };
  }
}

// Send a message to the server and add it to chat
function sendMessage() {
  const input = document.getElementById("user-input");
  if (!input) return;
  const message = input.value.trim();
  if (!message) return;
  appendMessage(message, "user");
  socket.emit("message", { message, user_id: userId });
  input.value = "";
}

// Listen for responses from the server
socket.on("response", (data) => {
  appendMessage(data.message || "🤖 I’m here to help!", "bot");
  speak(data.message);
  saveToHistory(data.message, "bot");
});

// Add a new message bubble to the chat UI
function appendMessage(text, type, skipHistory = false) {
  const chatbox = document.getElementById("chatbox");
  if (!chatbox) return;

  const msg = document.createElement("div");
  msg.className = `message ${type}`;

  // Sanitize and render Markdown safely
  let bubbleContent = "🤖 I'm here to help.";
  if (typeof marked !== "undefined" && typeof DOMPurify !== "undefined") {
    bubbleContent = DOMPurify.sanitize(marked.parse(text || bubbleContent));
  } else if (typeof marked !== "undefined") {
    bubbleContent = marked.parse(text || bubbleContent); // Less safe!
  } else {
    bubbleContent = text || bubbleContent;
  }
  msg.innerHTML = `<div class="bubble">${bubbleContent}</div>`;

  chatbox.appendChild(msg);
  chatbox.scrollTop = chatbox.scrollHeight;
  if (!skipHistory) saveToHistory(text, type);
}

// Clear the chat UI and history
function clearChat() {
  if (!confirm("Clear chat history?")) return;
  const chatbox = document.getElementById("chatbox");
  if (chatbox) chatbox.innerHTML = "";
  try {
    localStorage.removeItem("chatHistory");
  } catch (e) {
    console.error("Error clearing chat history:", e);
  }
  appendMessage("👋 Hi again! I’m Astra. How can I help?", "bot");
}

// Save a message to chat history in localStorage, capped at 100 messages
function saveToHistory(text, type) {
  try {
    const history = JSON.parse(localStorage.getItem("chatHistory") || "[]");
    history.push({ text, type });
    localStorage.setItem("chatHistory", JSON.stringify(history.slice(-100)));
  } catch (e) {
    console.error("Failed to save chat history:", e);
  }
}

// Load chat history from localStorage on page load
function loadHistory() {
  try {
    const history = JSON.parse(localStorage.getItem("chatHistory") || "[]");
    history.forEach((msg) => appendMessage(msg.text, msg.type, true)); // skipHistory=true to avoid redundant save
  } catch (e) {
    console.error("Failed to load chat history:", e);
  }
}

// Use the browser's speech synthesis API to read bot messages aloud
function speak(text) {
  if (!("speechSynthesis" in window) || !text) return;
  const utterance = new SpeechSynthesisUtterance(
    text.replace(/<[^>]*>/g, "")
  );
  utterance.rate = 0.95;
  speechSynthesis.speak(utterance);
}

// Toggle between dark and light themes
function toggleTheme() {
  document.body.classList.toggle("light");
  localStorage.setItem(
    "theme",
    document.body.classList.contains("light") ? "light" : "dark"
  );
}

// Initialize the theme on page load
function initTheme() {
  const saved = localStorage.getItem("theme") || "dark";
  if (saved === "light") document.body.classList.add("light");
  const themeToggle = document.getElementById("themeToggle");
  if (themeToggle) themeToggle.checked = saved === "light";
}
