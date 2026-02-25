from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import uuid
from PyPDF2 import PdfReader
import docx
import google.generativeai as genai

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DOCUMENT_TEXT = ""

# Gemini API
genai.configure(api_key="YOUR_API_KEY_HERE")
model = genai.GenerativeModel("models/gemini-flash-latest")


# ==========================
# SERVE DASHBOARD PAGE
# ==========================

@app.route("/")
def home():
    return send_from_directory(".", "index.html")


@app.route("/index.html")
def index():
    return send_from_directory(".", "index.html")


# ==========================
# SERVE CHATBOT PAGE
# ==========================

@app.route("/chatbot.html")
def chatbot_page():
    return send_from_directory(".", "chatbot.html")


# ==========================
# SERVE CSS & JS FILES
# ==========================

@app.route("/styles.css")
def styles():
    return send_from_directory(".", "styles.css")


@app.route("/chatbot.css")
def chatbot_css():
    return send_from_directory(".", "chatbot.css")


@app.route("/newscript.js")
def script():
    return send_from_directory(".", "newscript.js")


@app.route("/robot.jpg")
def image():
    return send_from_directory(".", "robot.jpg")


# ==========================
# DOCUMENT UPLOAD
# ==========================

@app.route("/upload-document", methods=["POST"])
def upload_document():
    global DOCUMENT_TEXT

    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    filename = str(uuid.uuid4()) + "_" + file.filename
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    text = ""

    if filename.lower().endswith(".pdf"):
        reader = PdfReader(filepath)
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"

    elif filename.lower().endswith(".docx"):
        doc = docx.Document(filepath)
        for p in doc.paragraphs:
            text += p.text + "\n"

    elif filename.lower().endswith(".txt"):
        text = open(filepath, "r", encoding="utf-8").read()

    else:
        return jsonify({"error": "Unsupported file type"}), 400

    if DOCUMENT_TEXT:
        DOCUMENT_TEXT += "\n\n" + text
    else:
        DOCUMENT_TEXT = text

    return jsonify({"message": "Document uploaded successfully!"})


# ==========================
# CLEAR DOCUMENTS
# ==========================

@app.route("/clear-documents", methods=["POST"])
def clear_documents():
    global DOCUMENT_TEXT
    DOCUMENT_TEXT = ""
    return jsonify({"message": "All documents cleared!"})


# ==========================
# CHATBOT RESPONSE
# ==========================

@app.route("/chatbot", methods=["POST"])
def chatbot():
    global DOCUMENT_TEXT

    data = request.get_json()
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    if not DOCUMENT_TEXT:
        return jsonify({"response": "Please upload a document first."})

    prompt = f"""
Answer ONLY using the document content below.

DOCUMENT:
{DOCUMENT_TEXT}

QUESTION:
{user_message}

If answer not found, say:
'I could not find this information in the uploaded document.'
"""

    response = model.generate_content(prompt)
    return jsonify({"response": response.text})


# ==========================

if __name__ == "__main__":
    app.run(debug=True)