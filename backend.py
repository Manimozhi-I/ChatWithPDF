from flask import Flask, request, jsonify
from flask_cors import CORS
from PyPDF2 import PdfReader
import docx
from openai import OpenAI
import os
import uuid

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DOCUMENT_TEXT = ""

client = OpenAI(
    api_key="",

    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# DOCUMENT UPLOAD + EXTRACTION

@app.route("/upload-doc", methods=["POST"])
def upload_doc():
    global DOCUMENT_TEXT

    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    filename = f"{uuid.uuid4()}_{file.filename}"
    path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(path)

    text = ""

    if filename.lower().endswith(".pdf"):
        reader = PdfReader(path)
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"

    elif filename.lower().endswith(".docx"):
        doc = docx.Document(path)
        for p in doc.paragraphs:
            text += p.text + "\n"

    elif filename.lower().endswith(".txt"):
        text = open(path, "r", encoding="utf-8").read()

    else:
        return jsonify({"error": "Unsupported file type"}), 400

    DOCUMENT_TEXT = text.strip()

    return jsonify({"message": "Document uploaded"})

# QUESTION ANSWERING

@app.route("/query", methods=["POST"])
def query():
    global DOCUMENT_TEXT

    data = request.get_json()
    question = data.get("query", "").strip()

    if not question:
        return jsonify({"answer": "No question received."})

    if not DOCUMENT_TEXT:
        return jsonify({"answer": "Please upload a document first."})

    prompt = f"""
You are an assistant. Answer ONLY based on the document below.

---------------------
DOCUMENT CONTENT:
{DOCUMENT_TEXT}
---------------------

RULES:
- If answer exists → give it clearly.
- If answer does NOT exist → say:
  "I could not find this information in the uploaded document."

QUESTION: {question}
"""

    response = client.chat.completions.create(
        model="models/gemini-2.5-pro",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
    )

    answer = response.choices[0].message.content
    return jsonify({"answer": answer})


if __name__ == "__main__":
    app.run(port=8001, debug=True)
