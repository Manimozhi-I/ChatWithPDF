from urllib import response
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
import uuid
from PyPDF2 import PdfReader
import docx
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config['UPLOAD_FOLDER'] = "uploads"
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Gemini API
genai.configure(api_key="AIzaSyB7sXag3_ZENBvgs-wii8yd-LHFjCpOJx4")

model = genai.GenerativeModel("models/gemini-flash-latest")

# Stores extracted document text
DOCUMENT_TEXT = ""


# ============================
# SERVE FRONT-END FILES
# ============================

@app.route("/")
def serve_index():
    return send_file("newindex.html")


@app.route("/newindex.html")
def serve_index2():
    return send_file("newindex.html")


@app.route("/newstyle.css")
def css_file():
    return send_file("newstyle.css")


@app.route("/newscript.js")
def js_file():
    return send_file("newscript.js")


# ============================
# UPLOAD DOCUMENT + EXTRACT TEXT
# ============================

@app.route("/upload-document", methods=["POST"])
def upload_document():
    global DOCUMENT_TEXT

    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    filename = str(uuid.uuid4()) + "_" + file.filename
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    text = ""

    # PDF extraction
    if filename.lower().endswith(".pdf"):
        reader = PdfReader(filepath)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    # DOCX extraction
    elif filename.lower().endswith(".docx"):
        doc = docx.Document(filepath)
        for para in doc.paragraphs:
            text += para.text + "\n"

    # TXT extraction
    elif filename.lower().endswith(".txt"):
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()

    else:
        return jsonify({"error": "Unsupported file type"}), 400

    text = text.strip()

    # If there is already text from previous documents, append.
    # This way, you can upload multiple documents and ask from all of them.
    global DOCUMENT_TEXT
    if DOCUMENT_TEXT:
        DOCUMENT_TEXT += "\n\n" + text
    else:
        DOCUMENT_TEXT = text

    return jsonify({"message": "Document uploaded successfully!"})

@app.route("/clear-documents", methods=["POST"])
def clear_documents():
    global DOCUMENT_TEXT
    DOCUMENT_TEXT = ""
    return jsonify({"message": "All documents cleared!"})

# CHATBOT ANSWERS FROM DOCUMENT

@app.route("/chatbot", methods=["POST"])
def chatbot():
    global DOCUMENT_TEXT

    data = request.get_json()
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    if not DOCUMENT_TEXT:
        return jsonify({"response": "Please upload a document first so I can answer from it."})

    prompt = f"""
You are an AI assistant. Answer ONLY using the information from the document below.

DOCUMENT CONTENT:
------------------------------------------------
{DOCUMENT_TEXT}
------------------------------------------------

RULES:
- If the answer is in the document, extract and summarize it.
- If the answer is NOT found, say: "I could not find this information in the uploaded document."

User question: {user_message}
"""

    response = model.generate_content(prompt)
    ai_reply = response.text

    return jsonify({"response": ai_reply})


if __name__ == "__main__":
    app.run(debug=True)
