const socket = io();
let userId = localStorage.getItem("user_id") || `user_${Date.now()}`;
localStorage.setItem("user_id", userId);

window.onload = () => {
  loadHistory();
  applyTheme();
  setupEvents();
};

function setupEvents() {
  document.getElementById("send-button").onclick = sendMessage;
  document.getElementById("mic-button").onclick = startVoiceInput;
  document.getElementById("clear-chat").onclick = clearChat;
  document.getElementById("export-chat")?.addEventListener("click", exportChat);

  document.getElementById("themeToggle").onchange = toggleTheme;

  document.getElementById("user-input").onkeydown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };
}

// Quick Reply Support
function sendQuickReply(text) {
  document.getElementById("user-input").value = text;
  sendMessage();
}

// Typing Indicator
function showTyping() {
  const typing = document.getElementById("typing-indicator");
  if (typing) typing.style.display = "flex";
}
function hideTyping() {
  const typing = document.getElementById("typing-indicator");
  if (typing) typing.style.display = "none";
}

function sendMessage() {
  const input = document.getElementById("user-input");
  const message = input.value.trim();
  if (!message) return;

  appendMessage(message, "user");
  showTyping();
  socket.emit("message", { message, user_id: userId });
  input.value = "";
}

socket.on("response", (data) => {
  hideTyping();
  appendMessage(data.message, "bot");
  saveToHistory(data.message, "bot");
  speakText(data.message); // TTS
});

function appendMessage(text, type) {
  const chatbox = document.getElementById("chatbox");
  const msg = document.createElement("div");
  msg.className = `message ${type} animate__animated animate__fadeInUp`;
  msg.innerHTML = `<div class="bubble">${marked.parse(text || "...")}</div>`;
  chatbox.appendChild(msg);
  chatbox.scrollTop = chatbox.scrollHeight;
  saveToHistory(text, type);
}

function clearChat() {
  if (!confirm("Clear chat history?")) return;
  document.getElementById("chatbox").innerHTML = "";
  localStorage.removeItem("chatHistory");
  appendMessage("👋 Hi again! I'm Astra. Let's start fresh.", "bot");
}

function saveToHistory(text, type) {
  const history = JSON.parse(localStorage.getItem("chatHistory") || "[]");
  history.push({ text, type });
  localStorage.setItem("chatHistory", JSON.stringify(history.slice(-300)));
}

function loadHistory() {
  const history = JSON.parse(localStorage.getItem("chatHistory") || "[]");
  history.forEach(msg => appendMessage(msg.text, msg.type));
}

function startVoiceInput() {
  if (!('webkitSpeechRecognition' in window)) {
    alert("Your browser doesn't support speech recognition.");
    return;
  }

  const recognition = new webkitSpeechRecognition();
  recognition.lang = "en-US";
  recognition.continuous = false;
  recognition.interimResults = false;

  recognition.onresult = function (event) {
    const transcript = event.results[0][0].transcript;
    document.getElementById("user-input").value = transcript;
    sendMessage();
  };

  recognition.onerror = function () {
    alert("Speech recognition error.");
  };

  recognition.start();
}

function speakText(text) {
  if (!window.speechSynthesis) return;
  const utterance = new SpeechSynthesisUtterance(stripHTML(text));
  utterance.lang = "en-US";
  speechSynthesis.speak(utterance);
}

function stripHTML(html) {
  const div = document.createElement("div");
  div.innerHTML = html;
  return div.textContent || div.innerText || "";
}

function exportChat() {
  const chatbox = document.getElementById("chatbox");
  let text = "Astra Chat History\n----------------------\n";
  const bubbles = chatbox.querySelectorAll(".message");

  bubbles.forEach(bubble => {
    const content = bubble.innerText;
    const speaker = bubble.classList.contains("user") ? "You" : "Astra";
    text += `${speaker}: ${content}\n\n`;
  });

  const blob = new Blob([text], { type: "text/plain" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = "astra_chat.txt";
  link.click();
}

// Theme handling
function toggleTheme() {
  document.body.classList.toggle("light");
  const isLight = document.body.classList.contains("light");
  localStorage.setItem("theme", isLight ? "light" : "dark");
  document.getElementById("theme-status").textContent = isLight ? "Light" : "Dark";
}

function applyTheme() {
  const saved = localStorage.getItem("theme") || "dark";
  if (saved === "light") document.body.classList.add("light");
  document.getElementById("themeToggle").checked = saved === "light";
  document.getElementById("theme-status").textContent = saved === "light" ? "Light" : "Dark";
}

// Clear chat history on close
window.addEventListener("beforeunload", function () {
  localStorage.removeItem("chatHistory");
});
