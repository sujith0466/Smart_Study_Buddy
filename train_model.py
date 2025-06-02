import json
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords # Import stopwords for a more comprehensive list
import pickle
import random

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelBinarizer # For one-hot encoding labels if needed for some classifiers

# --- NLTK Data Downloads ---
# Download necessary NLTK data (run once)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    print("Downloading NLTK 'punkt' tokenizer data...")
    nltk.download('punkt')
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    print("Downloading NLTK 'wordnet' corpus data...")
    nltk.download('wordnet')
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    print("Downloading NLTK 'stopwords' corpus data...")
    nltk.download('stopwords')

# --- Initialize Lemmatizer and Stop Words ---
lemmatizer = WordNetLemmatizer()
# Combine custom ignore words with NLTK's English stopwords for a more robust set
ignore_words_set = set(['?', '!', '.', ',', 'is', 'a', 'the', 'and', 'to', 'in', 'for', 'on', 'of', 'that', 'it', 'you', 'this', 'are', 'with', 'as', 'at', 'by', 'an', 'be', 'not']).union(set(stopwords.words('english')))

# --- Custom Tokenizer for TfidfVectorizer ---
# This function will be used by TfidfVectorizer to preprocess text
# It ensures consistency with how you might preprocess text in the chatbot
def custom_tokenizer(text):
    """Tokenizes, lemmatizes, and filters stop words from a sentence."""
    word_list = nltk.word_tokenize(text.lower())
    return [lemmatizer.lemmatize(word) for word in word_list if word.isalnum() and word not in ignore_words_set]

# --- Data Loading ---
def load_intents(filename='intents.json'):
    """Load intents from the intents.json file."""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            intents = json.load(file)
        print(f"Intents loaded successfully from {filename}.")
        return intents['intents']
    except FileNotFoundError:
        print(f"Error: The file {filename} was not found. Please ensure it's in the same directory.")
        return None
    except json.JSONDecodeError:
        print(f"Error: The JSON file {filename} is not properly formatted.")
        return None

# Load intents data
intents_data = load_intents()

# --- Prepare Training Data for Pipeline ---
# The pipeline expects raw text for TF-IDF and corresponding labels
patterns_text = [] # Stores raw text patterns
labels = []        # Stores corresponding intent tags
classes = []       # Stores unique intent tags

if intents_data:
    for intent in intents_data:
        for pattern in intent.get('patterns', []):
            patterns_text.append(pattern) # Append the raw pattern text
            labels.append(intent['tag'])
            if intent['tag'] not in classes:
                classes.append(intent['tag'])

# Sort and save classes
classes = sorted(list(set(classes)))
pickle.dump(classes, open('classes.pkl', 'wb'))
print(f"Classes saved to classes.pkl: {classes}")

# --- Model Training Pipeline ---
# Use a Pipeline to chain TF-IDF vectorization and the classifier
# The TfidfVectorizer will now take raw text from patterns_text
# and use our custom_tokenizer for preprocessing.
intent_model = Pipeline([
    # 'tfidf' step: Converts text to TF-IDF features
    ('tfidf', TfidfVectorizer(
        tokenizer=custom_tokenizer, # Use our custom function for tokenization, lemmatization, stop words
        lowercase=False,            # Set to False because our custom_tokenizer handles lowercasing
        min_df=1,                   # Minimum document frequency to include a term
        ngram_range=(1, 2)          # Consider unigrams and bigrams
    )),
    # 'clf' step: The classifier that trains on the TF-IDF features
    ('clf', MultinomialNB())
])

# Train the model
if patterns_text and labels:
    intent_model.fit(patterns_text, labels) # Fit the pipeline with raw text and labels
    pickle.dump(intent_model, open('intent_model.pkl', 'wb'))
    print('Model training complete. Model and classes saved to disk.')
else:
    print("No training data found. Model not trained.")

# --- Save 'words.pkl' (Optional, for TF-IDF fallback consistency) ---
# If your chatbot's TF-IDF fallback specifically relies on a 'words.pkl'
# for a bag-of-words approach, you can generate it here.
# However, if the TF-IDF fallback in the chatbot also uses TfidfVectorizer,
# this file might not be strictly necessary for the fallback either.
# For now, let's keep it to maintain compatibility with your original chatbot structure.
all_words = []
if intents_data:
    for intent in intents_data:
        for pattern in intent.get('patterns', []):
            word_list = custom_tokenizer(pattern) # Use the same tokenizer
            all_words.extend(word_list)
words = sorted(list(set(all_words)))
pickle.dump(words, open('words.pkl', 'wb'))
print(f"Words saved to words.pkl: {len(words)} unique words.")


if __name__ == '__main__':
    print("Script finished.")
