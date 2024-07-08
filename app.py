from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
from heapq import nlargest
import pickle

app = Flask(__name__)
CORS(app)

# Load the English model for processing text
nlp = spacy.load('en_core_web_sm')

def extractive_summarization(text):
    # Process the text with spaCy
    doc = nlp(text)

    # Create a list of English stop words
    stopwords = list(STOP_WORDS)

    # Initialize punctuation and add newline characters
    punctuation_with_newline = punctuation + '\n'

    # Initialize dictionary for word frequencies
    word_frequencies = {}

    # Calculate word frequencies
    for word in doc:
        if word.text.lower() not in stopwords and word.text.lower() not in punctuation_with_newline:
            if word.text not in word_frequencies.keys():
                word_frequencies[word.text] = 1
            else:
                word_frequencies[word.text] += 1

    # Find maximum frequency
    max_frequency = max(word_frequencies.values())

    # Normalize word frequencies
    for word in word_frequencies.keys():
        word_frequencies[word] = word_frequencies[word] / max_frequency

    # Tokenize into sentences
    sentence_tokens = [sent for sent in doc.sents]

    # Calculate sentence scores based on word frequencies
    sentence_scores = {}
    for sent in sentence_tokens:
        for word in sent:
            if word.text.lower() in word_frequencies.keys():
                if sent not in sentence_scores.keys():
                    sentence_scores[sent] = word_frequencies[word.text.lower()]
                else:
                    sentence_scores[sent] += word_frequencies[word.text.lower()]

    # Determine number of sentences for summary (e.g., 30% of total sentences)
    select_length = int(len(sentence_tokens) * 0.3)

    # Generate summary using nlargest to select top sentences
    summary = nlargest(select_length, sentence_scores, key=sentence_scores.get)

    # Extract text of top sentences for final summary
    final_summary = [sent.text for sent in summary]

    return "\n".join(final_summary)

# Test the function
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.get_json()
    if 'text' not in data:
        return jsonify({"error": "No text provided"}), 400

    text = data['text']
    try:
        summary = extractive_summarization(text)
        return jsonify({"summary": summary})
    except Exception as e:
        print(f"Error during summarization: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
