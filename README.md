# Smart Study Buddy ChatBot

A modern, interactive study assistant chatbot built with Flask, Socket.IO, and JavaScript. It helps students with study tips, reminders, quizzes, motivation, and more—all in a beautiful, user-friendly interface.

## Features
- Real-time chat with a friendly AI bot
- Study tips, motivational quotes, jokes, and quizzes
- Theme switcher (light/dark mode)
- Chat history saved in your browser
- Responsive, modern UI with glassmorphism

## Project Structure
```
ChatBot/
├── app.py                # Main Flask backend
├── intents.json          # Bot intents and responses
├── requirements.txt      # Python dependencies
├── train_model.py        # (If using ML/NLP model training)
├── static/
│   ├── css/
│   │   └── styles.css
│   ├── img/
│   │   ├── bot.png
│   │   └── user.png
│   └── js/
│       └── script.js
└── templates/
    └── index.html
```

## Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/ChatBot.git
cd ChatBot
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the app
```bash
python app.py
```

The chatbot will be available at `http://localhost:5000`.

## Customization
- Edit `intents.json` to add or change bot responses.
- Update `static/css/styles.css` for custom styles.
- Change the UI in `templates/index.html`.

## License
MIT
