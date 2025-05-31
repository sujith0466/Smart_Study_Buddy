# =====================
# Imports and App Setup
# =====================
import random
import json
from datetime import datetime
import dateutil.parser
from flask import Flask, render_template
from flask_socketio import SocketIO
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle

app = Flask(__name__)

# =====================
# Load Trained Model (if available)
# =====================
try:
    intent_model = pickle.load(open('intent_model.pkl', 'rb'))
    words = pickle.load(open('words.pkl', 'rb'))
    classes = pickle.load(open('classes.pkl', 'rb'))
    model_loaded = True
except Exception:
    intent_model = None
    words = None
    classes = None
    model_loaded = False

# =====================
# Data Loading & Model
# =====================
def load_intents():
    """Load intents from the intents.json file."""
    with open('intents.json', 'r', encoding='utf-8') as file:
        intents = json.load(file)
    return intents['intents']

intents = load_intents()
corpus = [pattern for intent in intents for pattern in intent.get('patterns', [])]
tfidf_vectorizer = TfidfVectorizer()
tfidf_vectorizer.fit(corpus)

# =====================
# Session Management
# =====================
session_data = {}

def update_user_context(user_id, key, value):
    """Update a user's context in the session data without overwriting other keys."""
    if user_id not in session_data:
        session_data[user_id] = {}
    session_data[user_id][key] = value

# =====================
# Utility Functions
# =====================
def get_time_based_greeting():
    current_hour = datetime.now().hour
    if current_hour < 12:
        return "Good morning!"
    elif 12 <= current_hour < 18:
        return "Good afternoon!"
    else:
        return "Good evening!"

def extract_time(text):
    try:
        parsed_time = dateutil.parser.parse(text, fuzzy=True)
        return parsed_time.strftime("%I:%M %p")
    except ValueError:
        return None

# =====================
# Enhanced Intent Prediction
# =====================
def preprocess_input(sentence):
    import nltk
    from nltk.stem import WordNetLemmatizer
    lemmatizer = WordNetLemmatizer()
    ignore_words = set(['?', '!', '.', ',', 'is', 'a', 'the', 'and', 'to', 'in', 'for', 'on', 'of', 'that', 'it', 'you', 'this', 'are', 'with', 'as', 'at', 'by', 'an', 'be', 'not'])
    sentence_words = nltk.word_tokenize(sentence.lower())
    sentence_words = [lemmatizer.lemmatize(word) for word in sentence_words if word.isalnum() and word not in ignore_words]
    return sentence_words

def predict_intent(user_input):
    if model_loaded and intent_model and words:
        processed_sentence = preprocess_input(user_input)
        bag = [0] * len(words)
        for s in processed_sentence:
            if s in words:
                bag[words.index(s)] = 1
        pred = intent_model.predict([bag])[0]
        # If the model is not confident, fallback to TF-IDF
        proba = getattr(intent_model, 'predict_proba', lambda x: [[1]])([bag])[0]
        confidence = max(proba) if hasattr(proba, '__iter__') else 1
        if confidence < 0.4:
            # fallback to TF-IDF
            input_vec = tfidf_vectorizer.transform([user_input])
            corpus_vecs = tfidf_vectorizer.transform(corpus)
            similarities = cosine_similarity(input_vec, corpus_vecs)[0]
            if similarities.max() < 0.3:
                return None
            best_idx = similarities.argmax()
            pattern_count = 0
            for intent in intents:
                for pattern in intent.get('patterns', []):
                    if pattern_count == best_idx:
                        return intent['tag']
                    pattern_count += 1
            return None
        return classes[pred] if isinstance(pred, int) else pred
    else:
        # fallback to TF-IDF only
        input_vec = tfidf_vectorizer.transform([user_input])
        corpus_vecs = tfidf_vectorizer.transform(corpus)
        similarities = cosine_similarity(input_vec, corpus_vecs)[0]
        if similarities.max() < 0.3:
            return None
        best_idx = similarities.argmax()
        pattern_count = 0
        for intent in intents:
            for pattern in intent.get('patterns', []):
                if pattern_count == best_idx:
                    return intent['tag']
                pattern_count += 1
        return None

# =====================
# Response Handlers
# =====================
def fallback_response(user_input):
    """Return a fallback response based on user input."""
    if "help" in user_input.lower():
        return "Sure! I can help with study schedules, subjects, or videos. What would you like to know more about?"
    elif "sorry" in user_input.lower():
        return "No worries! Just let me know what you need help with."
    else:
        return ("I'm not sure how to help with that. Could you ask something else, or try 'help'?\n"
                "Or, you can ask me things like: 'quiz me', 'set a reminder', 'motivate me', or 'study schedule'.")

def handle_user_input(user_id, user_input):
    """Handle context-based user input for study subject selection."""
    if user_id in session_data and session_data[user_id].get('awaiting_subject'):
        update_user_context(user_id, 'subject', user_input)
        session_data[user_id].pop('awaiting_subject', None)
        return f"Okay, you're studying {user_input}. What specifically would you like help with regarding {user_input}?"
    else:
        update_user_context(user_id, 'awaiting_subject', True)
        return "What subject are you studying today?"

def rich_response(intent_tag):
    """Return a rich response for supported intents."""
    if intent_tag == "study_material":
        # Always return as a string for frontend compatibility
        return ("Here is some study material for you!\n"
                "- [Watch Video](https://youtube.com)\n"
                "- [Read Article](https://example.com)")
    return "I'm not sure about that."

# =====================
# Main Chatbot Logic
# =====================
def get_response(user_input, user_id):
    """Main function to get a chatbot response based on user input and context."""
    intent_tag = predict_intent(user_input)
    if intent_tag is None:
        if user_id in session_data and (session_data[user_id].get('awaiting_subject') or session_data[user_id].get('awaiting_time')):
            return handle_user_input(user_id, user_input)
        return fallback_response(user_input)
    intent_obj = next((i for i in intents if i['tag'] == intent_tag), None)
    if not intent_obj:
        return fallback_response(user_input)
    responses = intent_obj.get('responses', [])
    # Special intent handling
    if intent_tag == "greeting":
        greeting = get_time_based_greeting()
        return f"{greeting}. How can I help you today?"
    elif intent_tag == "set_reminder":
        time_str = extract_time(user_input)
        if time_str:
            update_user_context(user_id, 'reminder_time', time_str)
            return f"Understood. I will set a reminder for you at {time_str} IST."
        else:
            return "To set a reminder, please tell me the specific time (e.g., 'Remind me at 8:00 AM')."
    elif intent_tag == "study_schedule":
        if user_id in session_data and session_data[user_id].get('awaiting_subject'):
            subject = user_input.strip()
            update_user_context(user_id, 'study_subject', subject)
            session_data[user_id].pop('awaiting_subject', None)
            update_user_context(user_id, 'awaiting_time', True)
            return f"Okay, for studying {subject}, what time(s) are you planning? Please specify."
        elif user_id in session_data and session_data[user_id].get('study_subject') and session_data[user_id].get('awaiting_time'):
            study_times = user_input.strip()
            session_data[user_id].pop('awaiting_time', None)
            return f"Acknowledged. You plan to study {session_data[user_id]['study_subject']} at {study_times}. I will keep this in mind."
        else:
            update_user_context(user_id, 'awaiting_subject', True)
            return "To create a study schedule, first, what subject are you focusing on?"
    elif intent_tag == "help":
        return "I can assist you with reminders, study schedules, jokes, and more. Just let me know what you need!"
    elif intent_tag == "joke":
        return random.choice(responses)
    elif intent_tag == "thankyou":
        return random.choice(responses)
    elif intent_tag == "goodbye":
        return random.choice(responses)
    elif intent_tag == "about_bot":
        return random.choice(responses)
    elif intent_tag == "mood_check":
        return random.choice(responses)
    elif intent_tag == "clear_history":
        return random.choice(responses)
    elif intent_tag == "switch_theme":
        return random.choice(responses)
    elif intent_tag == "translate":
        return "To translate, please provide the text and the target language."
    elif intent_tag == "language_support":
        return random.choice(responses)
    elif intent_tag == "motivation":
        return random.choice(responses)
    elif intent_tag == "fallback":
        return random.choice([
            "I'm sorry, I didn't quite understand your request. Could you please rephrase it?",
            "Could you try saying that in a different way? I'm still learning.",
            "I'm not sure I follow. What exactly are you looking for?"
        ])
    elif intent_tag == "study_material":
        return rich_response(intent_tag)
    elif intent_tag == "quiz_me":
        return random.choice(responses)
    elif intent_tag == "daily_goal":
        return random.choice(responses)
    elif intent_tag == "break_reminder":
        return random.choice(responses)
    elif intent_tag == "quote":
        return random.choice(responses)
    elif intent_tag == "bored":
        return random.choice(responses)
    elif intent_tag == "who_made_you":
        return random.choice(responses)
    elif intent_tag == "study_music":
        return random.choice(responses)
    elif intent_tag == "self_care":
        return random.choice(responses)
    elif intent_tag == "how_to_study_subject":
        return random.choice(responses)
    else:
        return random.choice(responses)

# =====================
# Flask Routes & SocketIO
# =====================
@app.route('/')
def home():
    """Render the main chat UI."""
    return render_template('index.html')

@socketio.on('message')
def handle_message(data):
    """Handle incoming messages from the frontend via SocketIO."""
    user_input = data.get('message', '').strip()
    user_id = data.get('user_id', 'default_user')
    if not user_input:
        socketio.emit('response', {'message': "Please enter a message."})
        return
    response = get_response(user_input, user_id)
    socketio.emit('response', {'message': response})

# =====================
# Main Entry Point
# =====================
if __name__ == "__main__":
    from flask_socketio import SocketIO
    socketio = SocketIO(app)
    socketio.run(app, host="0.0.0.0", port=8000)
