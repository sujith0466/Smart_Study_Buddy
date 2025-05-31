import json
import nltk
from nltk.stem import WordNetLemmatizer
import pickle
import random

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

# Initialize lemmatizer
lemmatizer = WordNetLemmatizer()
ignore_words = set(['?', '!', '.', ',', 'is', 'a', 'the', 'and', 'to', 'in', 'for', 'on', 'of', 'that', 'it', 'you', 'this', 'are', 'with', 'as', 'at', 'by', 'an', 'be', 'not'])

# Download necessary NLTK data (run once)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

def load_intents(filename='intents.json'):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            intents = json.load(file)
        return intents['intents']
    except FileNotFoundError:
        print(f"Error: The file {filename} was not found.")
        return None
    except json.JSONDecodeError:
        print("Error: The JSON file is not properly formatted.")
        return None

intents_data = load_intents()
words = []
classes = []
documents = []

if intents_data:
    for intent in intents_data:
        for pattern in intent.get('patterns', []):
            word_list = nltk.word_tokenize(pattern.lower())
            words.extend([lemmatizer.lemmatize(word) for word in word_list if word.isalnum() and word not in ignore_words])
            documents.append((word_list, intent['tag']))
            if intent['tag'] not in classes:
                classes.append(intent['tag'])

words = sorted(list(set(words)))
classes = sorted(list(set(classes)))

pickle.dump(words, open('words.pkl', 'wb'))
pickle.dump(classes, open('classes.pkl', 'wb'))

# Train a simple intent classifier
training_data = []
output_empty = [0] * len(classes)
for doc in documents:
    bag = []
    pattern_words = [lemmatizer.lemmatize(word.lower()) for word in doc[0] if word.isalnum() and word not in ignore_words]
    for word in words:
        bag.append(1) if word in pattern_words else bag.append(0)
    output_row = list(output_empty)
    output_row[classes.index(doc[1])] = 1
    training_data.append([bag, output_row])

random.shuffle(training_data)
train_x = [item[0] for item in training_data]
train_y = [item[1] for item in training_data]

intent_model = Pipeline([
    ('tfidf', TfidfVectorizer(vocabulary=words)),
    ('clf', MultinomialNB())
])
intent_model.fit(train_x, train_y)
pickle.dump(intent_model, open('intent_model.pkl', 'wb'))

if __name__ == '__main__':
    print('Model training complete. Model and data saved to disk.')