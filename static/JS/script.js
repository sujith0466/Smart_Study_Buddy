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
  document.getElementById("themeToggle").onchange = toggleTheme;
  document.getElementById("export-chat").onclick = exportChat;

  document.getElementById("user-input").onkeydown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };
}

// === Sidebar Feature: File Upload ===
document.addEventListener("DOMContentLoaded", function() {
  const fileBtn = document.querySelector('.sidebar-btn[title="File Upload"]');
  const fileInput = document.getElementById('sidebar-file-input');
  if (fileBtn && fileInput) {
    fileBtn.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', function() {
      if (fileInput.files.length > 0) {
        const fileName = fileInput.files[0].name;
        appendMessage(`📁 <b>Selected file:</b> ${fileName}`, "user");
        // Send file to backend via AJAX
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        fetch('/upload', {
          method: 'POST',
          body: formData
        })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            appendMessage(`✅ <b>File uploaded:</b> ${data.filename}`, "bot");
          } else {
            appendMessage(`❌ <b>Upload failed:</b> ${data.error || 'Unknown error'}`, "bot");
          }
        })
        .catch(() => {
          appendMessage('❌ <b>Upload failed:</b> Network error', "bot");
        });
      }
    });
  }

  // Image Generation
  const imgBtn = document.querySelector('.sidebar-btn[title="Image Generation"]');
  if (imgBtn) {
    imgBtn.addEventListener('click', function() {
      appendMessage('🖼️ <b>Image Generation:</b> Please describe the image you want to generate.', 'user');
      document.getElementById('user-input').value = 'Generate an image of...';
      document.getElementById('user-input').focus();
    });
  }

  // Listen for user sending an image generation prompt
  document.getElementById('send-button').addEventListener('click', function() {
    const input = document.getElementById('user-input');
    const value = input.value.trim();
    if (/^generate an image of/i.test(value)) {
      fetch('/generate-image', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: value })
      })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          appendMessage(`<b>Generated Image for:</b> ${data.prompt}<br><img src="${data.image_url}" alt="Generated" style="max-width:100%;border-radius:1em;margin-top:0.5em;">`, 'bot');
        } else {
          appendMessage('❌ <b>Image generation failed.</b>', 'bot');
        }
      })
      .catch(() => {
        appendMessage('❌ <b>Image generation failed: Network error.</b>', 'bot');
      });
    }
  });

  // Translate
  const translateBtn = document.querySelector('.sidebar-btn[title="Translate"]');
  if (translateBtn) {
    translateBtn.addEventListener('click', function() {
      appendMessage('🌐 <b>Translate:</b> Please enter the text and target language.', 'user');
      document.getElementById('user-input').value = 'Translate this to Spanish: ...';
      document.getElementById('user-input').focus();
    });
  }

  // Listen for user sending a translate prompt
  document.getElementById('send-button').addEventListener('click', function() {
    const input = document.getElementById('user-input');
    const value = input.value.trim();
    const match = value.match(/^translate (.+) to ([a-zA-Z]+):?\s*(.*)$/i);
    if (match) {
      const text = match[3] ? match[3] : match[1];
      const target = match[2];
      fetch('/translate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, target })
      })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          appendMessage(`<b>Translation:</b> ${data.translated}`, 'bot');
        } else {
          appendMessage('❌ <b>Translation failed.</b>', 'bot');
        }
      })
      .catch(() => {
        appendMessage('❌ <b>Translation failed: Network error.</b>', 'bot');
      });
    }
  });

  // Text-to-Speech
  const ttsBtn = document.querySelector('.sidebar-btn[title="Text-to-Speech"]');
  if (ttsBtn) {
    ttsBtn.addEventListener('click', function() {
      appendMessage('🔊 <b>Text-to-Speech:</b> Enter the text you want to hear.', 'user');
      document.getElementById('user-input').value = 'Read this aloud: ...';
      document.getElementById('user-input').focus();
    });
  }

  // Listen for user sending a TTS prompt
  document.getElementById('send-button').addEventListener('click', function() {
    const input = document.getElementById('user-input');
    const value = input.value.trim();
    const match = value.match(/^read this aloud: (.+)$/i);
    if (match) {
      const text = match[1];
      fetch('/tts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          appendMessage(`<b>Text-to-Speech:</b> <audio controls src="${data.audio_url}"></audio>`, 'bot');
        } else {
          appendMessage('❌ <b>Text-to-Speech failed.</b>', 'bot');
        }
      })
      .catch(() => {
        appendMessage('❌ <b>Text-to-Speech failed: Network error.</b>', 'bot');
      });
    }
  });

  // Reminders
  const reminderBtn = document.querySelector('.sidebar-btn[title="Reminders"]');
  if (reminderBtn) {
    reminderBtn.addEventListener('click', function() {
      appendMessage('⏰ <b>Reminders:</b> What would you like to be reminded about and when?', 'user');
      document.getElementById('user-input').value = 'Remind me to ... at ...';
      document.getElementById('user-input').focus();
    });
  }

  // Listen for user sending a reminder prompt
  document.getElementById('send-button').addEventListener('click', function() {
    const input = document.getElementById('user-input');
    const value = input.value.trim();
    const match = value.match(/^remind me to (.+) at (.+)$/i);
    if (match) {
      const text = match[1];
      const time = match[2];
      fetch('/reminder', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, time })
      })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          appendMessage(`<b>Reminder:</b> ${data.message}`, 'bot');
        } else {
          appendMessage('❌ <b>Reminder failed.</b>', 'bot');
        }
      })
      .catch(() => {
        appendMessage('❌ <b>Reminder failed: Network error.</b>', 'bot');
      });
    }
  });

  // Calendar Export
  const calBtn = document.querySelector('.sidebar-btn[title="Calendar Export"]');
  if (calBtn) {
    calBtn.addEventListener('click', function() {
      appendMessage('📅 <b>Calendar Export:</b> What event would you like to export?', 'user');
      document.getElementById('user-input').value = 'Export my event ... to calendar';
      document.getElementById('user-input').focus();
    });
  }

  // Listen for user sending a calendar export prompt
  document.getElementById('send-button').addEventListener('click', function() {
    const input = document.getElementById('user-input');
    const value = input.value.trim();
    const match = value.match(/^export my event (.+) to calendar$/i);
    if (match) {
      const event = match[1];
      fetch('/calendar-export', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ event })
      })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          appendMessage(`<b>Calendar Export:</b> ${data.message}`, 'bot');
        } else {
          appendMessage('❌ <b>Calendar export failed.</b>', 'bot');
        }
      })
      .catch(() => {
        appendMessage('❌ <b>Calendar export failed: Network error.</b>', 'bot');
      });
    }
  });

  // Quiz Customization
  const quizBtn = document.querySelector('.sidebar-btn[title="Quiz Customization"]');
  if (quizBtn) {
    quizBtn.addEventListener('click', function() {
      appendMessage('📝 <b>Quiz Customization:</b> What topic or difficulty for your quiz?', 'user');
      document.getElementById('user-input').value = 'Give me a quiz on ... (difficulty: ...)';
      document.getElementById('user-input').focus();
    });
  }

  // Listen for user sending a quiz customization prompt
  document.getElementById('send-button').addEventListener('click', function() {
    const input = document.getElementById('user-input');
    const value = input.value.trim();
    const match = value.match(/^give me a quiz on (.+) \(difficulty: (.+)\)$/i);
    if (match) {
      const topic = match[1];
      const difficulty = match[2];
      fetch('/quiz-customization', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic, difficulty })
      })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          appendMessage(`<b>Quiz Customization:</b> ${data.message}`, 'bot');
        } else {
          appendMessage('❌ <b>Quiz customization failed.</b>', 'bot');
        }
      })
      .catch(() => {
        appendMessage('❌ <b>Quiz customization failed: Network error.</b>', 'bot');
      });
    }
  });

  // Progress
  const progressBtn = document.querySelector('.sidebar-btn[title="Progress"]');
  if (progressBtn) {
    progressBtn.addEventListener('click', function() {
      appendMessage('📊 <b>Progress:</b> Show my study progress.', 'user');
      document.getElementById('user-input').value = 'Show my progress';
      document.getElementById('user-input').focus();
    });
  }

  // Listen for user sending a progress prompt
  document.getElementById('send-button').addEventListener('click', function() {
    const input = document.getElementById('user-input');
    const value = input.value.trim();
    if (/^show my progress$/i.test(value)) {
      fetch('/progress', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user: 'You' })
      })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          appendMessage(`<b>Progress:</b> ${data.message}`, 'bot');
        } else {
          appendMessage('❌ <b>Progress fetch failed.</b>', 'bot');
        }
      })
      .catch(() => {
        appendMessage('❌ <b>Progress fetch failed: Network error.</b>', 'bot');
      });
    }
  });

  // Export
  const exportBtn = document.querySelector('.sidebar-btn[title="Export"]');
  if (exportBtn) {
    exportBtn.addEventListener('click', function() {
      appendMessage('⬇️ <b>Export:</b> Export my data or chat history.', 'user');
      document.getElementById('user-input').value = 'Export my chat history';
      document.getElementById('user-input').focus();
    });
  }

  // Listen for user sending an export prompt
  document.getElementById('send-button').addEventListener('click', function() {
    const input = document.getElementById('user-input');
    const value = input.value.trim();
    const match = value.match(/^export my (.+)$/i);
    if (match) {
      const what = match[1];
      fetch('/export', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ what })
      })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          appendMessage(`<b>Export:</b> ${data.message}`, 'bot');
        } else {
          appendMessage('❌ <b>Export failed.</b>', 'bot');
        }
      })
      .catch(() => {
        appendMessage('❌ <b>Export failed: Network error.</b>', 'bot');
      });
    }
  });

  // FAQ
  const faqBtn = document.querySelector('.sidebar-btn[title="FAQ"]');
  if (faqBtn) {
    faqBtn.addEventListener('click', function() {
      appendMessage('❓ <b>FAQ:</b> What do you want to know?', 'user');
      document.getElementById('user-input').value = 'FAQ: ...';
      document.getElementById('user-input').focus();
    });
  }

  // Fun
  const funBtn = document.querySelector('.sidebar-btn[title="Fun"]');
  if (funBtn) {
    funBtn.addEventListener('click', function() {
      appendMessage('🎲 <b>Fun:</b> Want a joke, riddle, or game?', 'user');
      document.getElementById('user-input').value = 'Tell me a joke';
      document.getElementById('user-input').focus();
    });
  }

  // Resources
  const resBtn = document.querySelector('.sidebar-btn[title="Resources"]');
  if (resBtn) {
    resBtn.addEventListener('click', function() {
      appendMessage('📚 <b>Resources:</b> What resources do you need?', 'user');
      document.getElementById('user-input').value = 'Show me resources for ...';
      document.getElementById('user-input').focus();
    });
  }

  // Languages
  const langBtn = document.querySelector('.sidebar-btn[title="Languages"]');
  if (langBtn) {
    langBtn.addEventListener('click', function() {
      appendMessage('🌍 <b>Languages:</b> Which language do you want to use?', 'user');
      document.getElementById('user-input').value = 'Switch language to ...';
      document.getElementById('user-input').focus();
    });
  }

  // Group Chat
  const groupBtn = document.querySelector('.sidebar-btn[title="Group Chat"]');
  if (groupBtn) {
    groupBtn.addEventListener('click', function() {
      appendMessage('👥 <b>Group Chat:</b> Invite others or join a group.', 'user');
      document.getElementById('user-input').value = 'Start a group chat about ...';
      document.getElementById('user-input').focus();
    });
  }

  // Avatar
  const avatarBtn = document.querySelector('.sidebar-btn[title="Avatar"]');
  if (avatarBtn) {
    avatarBtn.addEventListener('click', function() {
      appendMessage('🧑 <b>Avatar:</b> Change or customize your avatar.', 'user');
      document.getElementById('user-input').value = 'Change my avatar to ...';
      document.getElementById('user-input').focus();
    });
  }
});

function sendMessage() {
  const input = document.getElementById("user-input");
  const message = input.value.trim();
  if (!message) return;

  appendMessage(message, "user");
  socket.emit("message", { message, user_id: userId });
  input.value = "";
}

socket.on("response", (data) => {
  appendMessage(data.message, "bot");
  saveToHistory(data.message, "bot");
});

function appendMessage(text, type) {
  const chatbox = document.getElementById("chatbox");
  const msg = document.createElement("div");
  msg.className = `message ${type}`;
  msg.innerHTML = `<div class="bubble">${marked.parse(text || "..." )}</div>`;
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
