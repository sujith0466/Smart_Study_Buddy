from flask import Flask, render_template, request, jsonify, session, send_file, make_response
from flask_socketio import SocketIO
import json, random, logging
import spacy
import os
from difflib import get_close_matches
from werkzeug.utils import secure_filename
from difflib import SequenceMatcher
import datetime

# Load NLP model for keyword extraction
nlp = spacy.load("en_core_web_sm")

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev_secret")  # Added for session security
socketio = SocketIO(app)
logging.basicConfig(level=logging.INFO)

# Load intents
with open("intents.json", encoding="utf-8") as f:
    intents = json.load(f)["intents"]

user_quiz_data = {}  # Stores question index and score per user
# User context for multi-turn
user_context = {}

# Dummy quiz data
quiz_bank = {
    "python": [
        "What is a variable in Python?",
        "Define a function in Python.",
        "What is a list comprehension?",
        "What is the difference between a list and a tuple?",
        "How do you handle exceptions in Python?"
    ],
    "java": [
        "What is a class in Java?",
        "Explain inheritance in Java.",
        "What is JVM?",
        "What are access modifiers?",
        "Difference between overloading and overriding?"
    ],
    "c++": [
        "What is a pointer?",
        "Explain constructors and destructors.",
        "What is the use of 'this' pointer?",
        "What are templates in C++?",
        "Define function overloading."
    ],
    "c": [
        "What is a header file in C?",
        "Difference between malloc() and calloc()?",
        "Explain pointers in C.",
        "What is a static variable?",
        "What are structures in C?"
    ],
    "ai": [
        "What is artificial intelligence?",
        "Name a type of AI.",
        "What is supervised learning?",
        "What is overfitting?",
        "What are neural networks?"
    ]
}

# In-memory FAQ base for demo
FAQ_BASE = [
    {"q": "How do I reset my password?", "a": "Go to settings and click 'Reset Password'."},
    {"q": "How do I start a quiz?", "a": "Click the Quiz button or type 'Start a quiz'."},
    {"q": "What languages are supported?", "a": "English, Spanish, French, German, Hindi, Chinese, Japanese, Russian, Arabic, Italian, Portuguese."},
    {"q": "How do I upload a file?", "a": "Click the File Upload button in the sidebar."},
]

JOKES = [
    "Why did the computer go to the doctor? Because it had a virus!",
    "Why do programmers prefer dark mode? Because light attracts bugs!",
    "Why was the math book sad? Because it had too many problems!",
]
FACTS = [
    "Did you know? The first computer bug was an actual moth.",
    "Python is named after Monty Python, not the snake.",
    "The first 1GB hard disk was announced in 1980 and weighed 550 pounds!",
]
GAMES = [
    "Let's play Rock, Paper, Scissors! Type your choice.",
    "Guess a number between 1 and 10! (Demo only)",
    "Try this riddle: What has keys but can't open locks? (A piano)",
]

RESOURCE_TOPICS = {
    "python": [
        ("Official Python Docs", "https://docs.python.org/3/"),
        ("GeeksforGeeks Python", "https://www.geeksforgeeks.org/tag/python/"),
        ("YouTube Python Tutorials", "https://youtube.com/results?search_query=python+tutorial"),
    ],
    "java": [
        ("Official Java Docs", "https://docs.oracle.com/javase/8/docs/"),
        ("GeeksforGeeks Java", "https://www.geeksforgeeks.org/tag/java/"),
        ("YouTube Java Tutorials", "https://youtube.com/results?search_query=java+tutorial"),
    ],
    "ai": [
        ("Wikipedia AI", "https://en.wikipedia.org/wiki/Artificial_intelligence"),
        ("YouTube AI Tutorials", "https://youtube.com/results?search_query=ai+tutorial"),
    ],
}

SUPPORTED_LANGUAGES = ['English', 'Spanish', 'French', 'German', 'Hindi', 'Chinese', 'Japanese', 'Russian', 'Arabic', 'Italian', 'Portuguese']

UPLOAD_FOLDER = os.path.join('static', 'img', 'avatars')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/health")
def health():
    """Health check endpoint for deployment readiness."""
    return jsonify({'status': 'ok', 'time': datetime.datetime.utcnow().isoformat()})

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file part'}), 400
    file = request.files['file']
    if not file or file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'}), 400
    filename = secure_filename(file.filename)
    if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
        return jsonify({'success': False, 'error': 'Invalid file type'}), 400
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    try:
        file.save(save_path)
    except Exception as e:
        logging.error(f"File save error: {e}")
        return jsonify({'success': False, 'error': 'File save failed'}), 500
    return jsonify({'success': True, 'filename': filename})

@app.route('/generate-image', methods=['POST'])
def generate_image():
    data = request.get_json()
    prompt = data.get('prompt', '')
    # Placeholder: In production, call an image generation API here
    # For now, return a placeholder image URL
    image_url = 'https://via.placeholder.com/300x200.png?text=Generated+Image'
    return jsonify({'success': True, 'image_url': image_url, 'prompt': prompt})

@app.route('/translate', methods=['POST'])
def translate():
    data = request.get_json()
    text = data.get('text', '')
    target = data.get('target', 'Spanish')
    supported = ['Spanish', 'French', 'German', 'Hindi', 'Chinese', 'Japanese', 'Russian', 'Arabic', 'Italian', 'Portuguese']
    if target.capitalize() not in supported:
        return jsonify({'success': False, 'translated': f"Sorry, '{target}' is not supported. Supported: {', '.join(supported)}."})
    # Placeholder: In production, call a translation API here
    translated = f"[Translated to {target}]: {text}"
    return jsonify({'success': True, 'translated': translated})

@app.route('/tts', methods=['POST'])
def tts():
    data = request.get_json()
    text = data.get('text', '')
    # Placeholder: In production, generate and return a real audio file or URL
    # Here, just return a dummy audio URL
    audio_url = 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3'
    return jsonify({'success': True, 'audio_url': audio_url, 'text': text})

@app.route('/reminder', methods=['POST'])
def reminder():
    data = request.get_json()
    text = data.get('text', '')
    time = data.get('time', '')
    # Placeholder: In production, schedule a real reminder
    # Here, just return a confirmation message
    return jsonify({'success': True, 'message': f"Reminder set for '{text}' at {time if time else '[time not specified]'} (demo only)"})

@app.route('/calendar-export', methods=['POST'])
def calendar_export():
    data = request.get_json()
    event = data.get('event', '')
    # Placeholder: In production, generate and return a real calendar file or link
    # Here, just return a confirmation message
    return jsonify({'success': True, 'message': f"Event '{event}' exported to your calendar (demo only)"})

@app.route('/quiz-customization', methods=['POST'])
def quiz_customization():
    data = request.get_json()
    topic = data.get('topic', 'General')
    difficulty = data.get('difficulty', 'Any')
    # Placeholder: In production, generate a real quiz based on topic/difficulty
    # Here, just return a confirmation message
    return jsonify({'success': True, 'message': f"Quiz customized for topic '{topic}' with difficulty '{difficulty}' (demo only)"})

@app.route('/progress', methods=['POST'])
def progress():
    data = request.get_json()
    user = data.get('user', 'You')
    # Placeholder: In production, fetch real progress data
    # Here, just return a demo progress message
    return jsonify({'success': True, 'message': f"{user}'s progress: 5 quizzes completed, 3 reminders set, 2 study plans created (demo only)"})

@app.route('/export', methods=['POST'])
def export():
    data = request.get_json(silent=True) or {}
    what = data.get('what', 'chat history')
    export_format = data.get('format', 'txt')
    filename = data.get('filename', f"astra_export_{what.replace(' ', '_')}.{export_format}")
    # Demo export content
    export_content = f"Exported data for: {what}\nDate: 2025-06-03\n(This is demo content.)"
    import io
    if export_format == 'json':
        import json as pyjson
        file_obj = io.BytesIO(pyjson.dumps({"exported": what, "date": "2025-06-03", "demo": True}).encode('utf-8'))
        file_obj.seek(0)
        try:
            return send_file(file_obj, as_attachment=True, download_name=filename, mimetype='application/json')
        except TypeError:
            # For older Flask versions
            return send_file(file_obj, as_attachment=True, attachment_filename=filename, mimetype='application/json')
    elif export_format == 'txt':
        file_obj = io.BytesIO(export_content.encode('utf-8'))
        file_obj.seek(0)
        try:
            return send_file(file_obj, as_attachment=True, download_name=filename, mimetype='text/plain')
        except TypeError:
            return send_file(file_obj, as_attachment=True, attachment_filename=filename, mimetype='text/plain')
    else:
        # Fallback: confirmation message
        return jsonify({'success': True, 'message': f"Exported {what} (demo only)"})

@app.route('/faq', methods=['POST'])
def faq():
    data = request.get_json(silent=True) or {}
    question = data.get('question', '')
    if not isinstance(question, str):
        return jsonify({'success': False, 'answer': 'Invalid question format.'})
    question = question.strip()
    if not question:
        return jsonify({'success': False, 'answer': 'Please provide a question.'})
    questions = [item['q'] for item in FAQ_BASE]
    matches = get_close_matches(question, questions, n=1, cutoff=0.4)
    if matches:
        answer = next((item['a'] for item in FAQ_BASE if item['q'] == matches[0]), None)
        return jsonify({'success': True, 'answer': answer})
    else:
        return jsonify({'success': True, 'answer': f"Sorry, I couldn't find an FAQ for '{question}'."})

@app.route('/fun', methods=['POST'])
def fun():
    data = request.get_json(silent=True) or {}
    fun_type = data.get('type', 'joke')
    if not isinstance(fun_type, str):
        fun_type = 'joke'
    fun_type = fun_type.lower()
    if fun_type == 'joke':
        content = random.choice(JOKES)
    elif fun_type == 'fact':
        content = random.choice(FACTS)
    elif fun_type == 'game':
        content = random.choice(GAMES)
    else:
        content = 'Unknown fun type. Try joke, fact, or game.'
    return jsonify({'success': True, 'content': content, 'type': fun_type})

@app.route('/resources', methods=['POST'])
def resources():
    data = request.get_json(silent=True) or {}
    topic = data.get('topic', 'Python')
    if not isinstance(topic, str):
        topic = 'Python'
    topic = topic.lower().strip()
    links = RESOURCE_TOPICS.get(topic, [])
    if not links:
        links = [("Wikipedia", f"https://en.wikipedia.org/wiki/{topic.title()}")]
    resources_list = [f"{name}: {url}" for name, url in links]
    return jsonify({'success': True, 'resources': resources_list, 'topic': topic.title()})

@app.route('/languages', methods=['POST'])
def languages():
    data = request.get_json(silent=True) or {}
    lang = data.get('language')
    if lang:
        if not isinstance(lang, str):
            return jsonify({'success': False, 'message': 'Invalid language format.', 'languages': SUPPORTED_LANGUAGES})
        if lang.capitalize() in SUPPORTED_LANGUAGES:
            session['language'] = lang.capitalize()
            return jsonify({'success': True, 'message': f"Language switched to {lang.capitalize()}.", 'languages': SUPPORTED_LANGUAGES})
        else:
            return jsonify({'success': False, 'message': f"Language '{lang}' not supported.", 'languages': SUPPORTED_LANGUAGES})
    return jsonify({'success': True, 'languages': SUPPORTED_LANGUAGES, 'current': session.get('language', 'English')})

@app.route('/group-chat', methods=['POST'])
def group_chat():
    data = request.get_json(silent=True) or {}
    action = data.get('action', 'info')
    group_name = data.get('group', 'General')
    if not isinstance(action, str):
        action = 'info'
    if not isinstance(group_name, str):
        group_name = 'General'
    action = action.lower()
    if action == 'create':
        return jsonify({'success': True, 'message': f"Group '{group_name}' created! (Demo only)"})
    elif action == 'join':
        return jsonify({'success': True, 'message': f"Joined group '{group_name}'! (Demo only)"})
    elif action == 'info':
        return jsonify({'success': True, 'message': f"Group chat feature is coming soon! (Demo only)"})
    else:
        return jsonify({'success': False, 'message': f"Unknown group chat action: {action}"})

@app.route('/avatar', methods=['POST'])
def avatar():
    if 'file' in request.files:
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No selected file'})
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)
        avatar_url = f"/static/img/avatars/{filename}"
        session['avatar_url'] = avatar_url
        return jsonify({'success': True, 'avatar_url': avatar_url, 'message': 'Avatar updated!'})
    data = request.get_json(silent=True) or {}
    avatar_action = data.get('action', 'get')
    if not isinstance(avatar_action, str):
        avatar_action = 'get'
    avatar_action = avatar_action.lower()
    if avatar_action == 'get':
        avatar_url = session.get('avatar_url', '/static/img/bot.png')
        return jsonify({'success': True, 'avatar_url': avatar_url})
    elif avatar_action == 'set':
        return jsonify({'success': True, 'message': 'Avatar updated! (demo only)'})
    else:
        return jsonify({'success': False, 'error': 'Unknown avatar action.'})

def predict_intent(message):
    message_lower = message.lower()
    for intent in intents:
        for pattern in intent["patterns"]:
            if pattern.lower() in message_lower:
                return intent["tag"]
    return None

def extract_keywords(message):
    doc = nlp(message)
    return [token.text for token in doc if token.pos_ in ("NOUN", "PROPN")]

def is_answer_similar(user_answer, expected_keywords):
    """Basic NLP similarity for quiz answers."""
    user_answer = user_answer.lower()
    for keyword in expected_keywords:
        if SequenceMatcher(None, keyword, user_answer).ratio() > 0.7:
            return True
    return False

def get_user_context(user_id, key):
    return user_context.get(user_id, {}).get(key)

def set_user_context(user_id, key, value):
    if user_id not in user_context:
        user_context[user_id] = {}
    user_context[user_id][key] = value

def clear_user_context(user_id):
    if user_id in user_context:
        user_context[user_id] = {}

@socketio.on('message')
def handle_message(data):
    user_input = data.get("message", "").strip()
    user_id = data.get("user_id", "anonymous_user")
    logging.info(f"[{user_id}] Input: {user_input}")

    if not user_input:
        response = "Please type something!"
        socketio.emit("response", {"message": response, "user_id": user_id})
        return

    response, intent_tag = get_response(user_input, user_id)

    # Custom logic for special intents
    if intent_tag == "quiz_request":
        # Reset quiz context
        topic = extract_keywords(user_input)
        chosen_topic = topic[0].lower() if topic else "python"
        questions = quiz_bank.get(chosen_topic, quiz_bank["python"])
        user_quiz_data[user_id] = {
            "topic": chosen_topic,
            "questions": questions,
            "index": 0,
            "score": 0
        }
        question = questions[0]
        set_user_context(user_id, "in_quiz", True)
        response = f"🧪 Starting quiz on {chosen_topic.title()}!\nQuestion 1: {question}"

    elif get_user_context(user_id, "in_quiz"):
        quiz = user_quiz_data.get(user_id)
        user_answer = user_input.lower().strip()
        current_index = quiz["index"]
        topic = quiz["topic"]
        expected_keywords = quiz["questions"][current_index].lower().split()
        # Improved answer checking
        correct = is_answer_similar(user_answer, expected_keywords)

        if correct:
            quiz["score"] += 1

        current_index += 1

        if current_index < len(quiz["questions"]):
            quiz["index"] = current_index
            next_q = quiz["questions"][current_index]
            response = f"✅ Got it!\n\nQuestion {current_index + 1}: {next_q}"
        else:
            score = quiz["score"]
            total = len(quiz["questions"])
            response = (
                f"✅ Quiz complete!\n\nYour Score: {score}/{total}\n"
                f"👏 Great work! Keep practicing!"
            )
            clear_user_context(user_id)
            user_quiz_data.pop(user_id, None)

    elif intent_tag == "study_schedule":
        response += "\n\n📅 Sample Study Plan:\n- Math: 2 hrs\n- Python: 1.5 hrs\n- Review: 30 mins"

    elif intent_tag == "study_material":
        keywords = extract_keywords(user_input)
        subject = keywords[0].lower() if keywords else "python"
        response += f"\n\n📹 YouTube: https://youtube.com/results?search_query={subject}+tutorial\n📖 Article: https://www.geeksforgeeks.org/tag/{subject}/"

    elif intent_tag == "reminder":
        response += "\n\n⏰ Reminder set! (Demo only – reminders don't persist yet)"

    elif intent_tag == "explain_topic":
        keywords = extract_keywords(user_input)
        topic = keywords[0] if keywords else "Python"
        response += f"\n\n📘 Want to learn more about {topic}? Try this: https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}"

    socketio.emit("response", {"message": response, "user_id": user_id})
    logging.info(f"[{user_id}] Response: {response}")

def get_response(user_input, user_id):
    if get_user_context(user_id, "awaiting_subject"):
        clear_user_context(user_id)
        return f"Great! Let's build a schedule for {user_input}.", "study_schedule"

    intent_tag = predict_intent(user_input)

    if not intent_tag:
        return "Hmm... I'm not sure how to help with that. Try asking about study plans, quizzes, or topics.", "fallback"

    intent_obj = next((i for i in intents if i["tag"] == intent_tag), None)
    if not intent_obj:
        return "Oops, something went wrong understanding that.", "fallback"

    set_user_context(user_id, "last_intent", intent_tag)

    # Check for action
    action = intent_obj.get("action")
    if action == "schedule":
        set_user_context(user_id, "awaiting_subject", True)

    responses = intent_obj.get("responses", [])
    return random.choice(responses) if responses else "Let’s continue!", intent_tag

if __name__ == "__main__":
    socketio.run(app, debug=True)
