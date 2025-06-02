const socket = io();
let userId = localStorage.getItem("user_id") || `user_${Date.now()}`;
localStorage.setItem("user_id", userId);

window.onload = () => {
  initTheme();
  loadHistory();
  setupEvents();
};

function setupEvents() {
  document.getElementById("send-button").onclick = sendMessage;
  document.getElementById("clear-chat").onclick = clearChat;
  document.getElementById("mic-button").onclick = () => speakInput();
  document.getElementById("themeToggle").onchange = toggleTheme;
  document.getElementById("user-input").onkeydown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };
}

function sendMessage() {
  const input = document.getElementById("user-input");
  const message = input.value.trim();
  if (!message) return;
  appendMessage(message, "user");
  socket.emit("message", { message, user_id: userId });
  input.value = "";
}

socket.on("response", (data) => {
  appendMessage(data.message || "🤖 I’m here to help!", "bot");
  speak(data.message);
  saveToHistory(data.message, "bot");
});

function appendMessage(text, type) {
  const chatbox = document.getElementById("chatbox");
  const msg = document.createElement("div");
  msg.className = `message ${type}`;
  msg.innerHTML = `<div class="bubble">${marked.parse(text || "🤖 I'm here to help.")}</div>`;
  chatbox.appendChild(msg);
  chatbox.scrollTop = chatbox.scrollHeight;
  saveToHistory(text, type);
}

function clearChat() {
  if (!confirm("Clear chat history?")) return;
  document.getElementById("chatbox").innerHTML = "";
  localStorage.removeItem("chatHistory");
  appendMessage("👋 Hi again! I’m Astra. How can I help?", "bot");
}

function saveToHistory(text, type) {
  const history = JSON.parse(localStorage.getItem("chatHistory") || "[]");
  history.push({ text, type });
  localStorage.setItem("chatHistory", JSON.stringify(history.slice(-100)));
}

function loadHistory() {
  const history = JSON.parse(localStorage.getItem("chatHistory") || "[]");
  history.forEach((msg) => appendMessage(msg.text, msg.type));
}

function speak(text) {
  if (!("speechSynthesis" in window)) return;
  const utterance = new SpeechSynthesisUtterance(text.replace(/<[^>]*>/g, ""));
  utterance.rate = 0.95;
  speechSynthesis.speak(utterance);
}

function toggleTheme() {
  document.body.classList.toggle("light");
  localStorage.setItem("theme", document.body.classList.contains("light") ? "light" : "dark");
}

function initTheme() {
  const saved = localStorage.getItem("theme") || "dark";
  if (saved === "light") document.body.classList.add("light");
  document.getElementById("themeToggle").checked = saved === "light";
}
