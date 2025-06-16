from flask import Flask, render_template, request, jsonify, session, send_file
from flask_socketio import SocketIO
import json, random, logging, os, io
import spacy
from difflib import get_close_matches
from werkzeug.utils import secure_filename
import pickle
intent_model = pickle.load(open("intent_model.pkl", "rb"))
classes = pickle.load(open("classes.pkl", "rb"))

def predict_intent(message):
    try:
        return intent_model.predict([message])[0]
    except Exception as e:
        print("Prediction error:", e)
        return None


# Initialize app
app = Flask(__name__)
socketio = SocketIO(app)
app.secret_key = 'astra_secret_key'
nlp = spacy.load("en_core_web_sm")
logging.basicConfig(level=logging.INFO)

# Load intents
with open("intents.json", encoding="utf-8") as f:
    intents = json.load(f)["intents"]

# Dummy data
user_quiz_data = {}
user_context = {}
UPLOAD_FOLDER = os.path.join('static', 'img', 'avatars')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

quiz_bank = {
    "python": [...],  # Same as before
    "java": [...],
    "c++": [...],
    "c": [...],
    "ai": [...]
}

FAQ_BASE = [
    {"q": "How do I reset my password?", "a": "Go to settings and click 'Reset Password'."},
    ...
]

JOKES = ["Why did the computer go to the doctor? Because it had a virus!", ...]
FACTS = ["Did you know? The first computer bug was an actual moth.", ...]
GAMES = ["Let's play Rock, Paper, Scissors! Type your choice.", ...]
SUPPORTED_LANGUAGES = ['English', 'Spanish', 'French', 'German', 'Hindi', 'Chinese', 'Japanese', 'Russian', 'Arabic', 'Italian', 'Portuguese']
RESOURCE_TOPICS = {
    "python": [...],
    "java": [...],
    "ai": [...]
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('file')
    if not file or file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'})
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return jsonify({'success': True, 'filename': filename})

@app.route('/generate-image', methods=['POST'])
def generate_image():
    data = request.get_json()
    prompt = data.get('prompt', '')
    return jsonify({'success': True, 'image_url': 'https://via.placeholder.com/300x200.png?text=Generated+Image', 'prompt': prompt})

@app.route('/translate', methods=['POST'])
def translate():
    data = request.get_json()
    text = data.get('text', '')
    target = data.get('target', 'Spanish')
    if target.capitalize() not in SUPPORTED_LANGUAGES:
        return jsonify({'success': False, 'translated': f"Sorry, '{target}' is not supported."})
    return jsonify({'success': True, 'translated': f"[Translated to {target}]: {text}"})

@app.route('/tts', methods=['POST'])
def tts():
    data = request.get_json()
    return jsonify({'success': True, 'audio_url': 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3'})

@app.route('/reminder', methods=['POST'])
def reminder():
    data = request.get_json()
    return jsonify({'success': True, 'message': f"Reminder set for '{data.get('text')}' at {data.get('time')}"})

@app.route('/calendar-export', methods=['POST'])
def calendar_export():
    data = request.get_json()
    return jsonify({'success': True, 'message': f"Event '{data.get('event')}' exported to your calendar (demo only)"})

@app.route('/quiz-customization', methods=['POST'])
def quiz_customization():
    data = request.get_json()
    return jsonify({'success': True, 'message': f"Quiz customized for topic '{data.get('topic')}' with difficulty '{data.get('difficulty')}' (demo only)"})

@app.route('/progress', methods=['POST'])
def progress():
    return jsonify({'success': True, 'message': "5 quizzes completed, 3 reminders set."})

@app.route('/export', methods=['POST'])
def export():
    data = request.get_json() or {}
    what = data.get('what', 'chat history')
    export_content = f"Exported data for: {what}\n(This is demo content.)"
    file_obj = io.BytesIO(export_content.encode('utf-8'))
    return send_file(file_obj, as_attachment=True, download_name=f"{what.replace(' ', '_')}.txt", mimetype='text/plain')

@app.route('/faq', methods=['POST'])
def faq():
    data = request.get_json() or {}
    question = data.get("question", "")
    match = get_close_matches(question, [f['q'] for f in FAQ_BASE], n=1, cutoff=0.4)
    if match:
        return jsonify({'success': True, 'answer': next(f['a'] for f in FAQ_BASE if f['q'] == match[0])})
    return jsonify({'success': True, 'answer': f"No match found for: {question}"})

@app.route('/resources', methods=['POST'])
def resources():
    data = request.get_json() or {}
    topic = data.get("topic", "python").lower()
    links = RESOURCE_TOPICS.get(topic, [("Wikipedia", f"https://en.wikipedia.org/wiki/{topic.title()}")])
    return jsonify({'success': True, 'resources': [f"{name}: {url}" for name, url in links]})

@app.route('/languages', methods=['POST'])
def languages():
    data = request.get_json() or {}
    lang = data.get("language")
    if lang and lang.capitalize() in SUPPORTED_LANGUAGES:
        session['language'] = lang.capitalize()
        return jsonify({'success': True, 'message': f"Language set to {lang.capitalize()}."})
    return jsonify({'success': False, 'languages': SUPPORTED_LANGUAGES})

@app.route('/group-chat', methods=['POST'])
def group_chat():
    return jsonify({'success': True, 'message': "Group chat support is a demo only!"})

@app.route('/avatar', methods=['POST'])
def avatar():
    if 'file' in request.files:
        file = request.files['file']
        filename = secure_filename(file.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path)
        session['avatar_url'] = f"/static/img/avatars/{filename}"
        return jsonify({'success': True, 'avatar_url': session['avatar_url']})
    return jsonify({'success': False, 'message': 'Upload failed.'})

# NLP Prediction + Context
def predict_intent(message):
    for intent in intents:
        for pattern in intent["patterns"]:
            if pattern.lower() in message.lower():
                return intent["tag"]
    return None

def extract_keywords(message):
    return [token.text for token in nlp(message) if token.pos_ in ("NOUN", "PROPN")]

def get_user_context(user_id, key):
    return user_context.get(user_id, {}).get(key)

def set_user_context(user_id, key, value):
    user_context.setdefault(user_id, {})[key] = value

def clear_user_context(user_id):
    user_context.pop(user_id, None)

# Main SocketIO Chat Handler
@socketio.on('message')
def handle_message(data):
    user_input = data.get("message", "").strip()
    user_id = data.get("user_id", "anonymous")

    if not user_input:
        socketio.emit("response", {"message": "Please type something!", "user_id": user_id})
        return

    response, intent_tag = get_response(user_input, user_id)

    if intent_tag == "quiz_request":
        topic = extract_keywords(user_input)
        chosen = topic[0].lower() if topic else "python"
        questions = quiz_bank.get(chosen, quiz_bank["python"])
        user_quiz_data[user_id] = {"topic": chosen, "questions": questions, "index": 0, "score": 0}
        set_user_context(user_id, "in_quiz", True)
        response = f"🧪 Starting quiz on {chosen.title()}!\nQuestion 1: {questions[0]}"

    elif get_user_context(user_id, "in_quiz"):
        quiz = user_quiz_data[user_id]
        current_index = quiz["index"]
        if any(word in user_input.lower() for word in quiz["questions"][current_index].lower().split()):
            quiz["score"] += 1
        current_index += 1
        if current_index < len(quiz["questions"]):
            quiz["index"] = current_index
            response = f"✅ Got it!\n\nQuestion {current_index + 1}: {quiz['questions'][current_index]}"
        else:
            response = f"🎉 Quiz done! Score: {quiz['score']}/{len(quiz['questions'])}"
            clear_user_context(user_id)
            user_quiz_data.pop(user_id)

    socketio.emit("response", {"message": response, "user_id": user_id})

def get_response(user_input, user_id):
    if get_user_context(user_id, "awaiting_subject"):
        clear_user_context(user_id)
        return f"Great! Let's build a schedule for {user_input}.", "study_schedule"

    intent_tag = predict_intent(user_input)
    if not intent_tag:
        return "Hmm... I'm not sure how to help with that.", "fallback"

    intent_obj = next((i for i in intents if i["tag"] == intent_tag), None)
    if not intent_obj:
        return "Oops, something went wrong.", "fallback"

    set_user_context(user_id, "last_intent", intent_tag)

    if intent_obj.get("action") == "schedule":
        set_user_context(user_id, "awaiting_subject", True)

    responses = intent_obj.get("responses", [])
    return random.choice(responses) if responses else "Let’s continue!", intent_tag

if __name__ == "__main__":
    socketio.run(app, debug=True)
