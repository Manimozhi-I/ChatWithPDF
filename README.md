## ChatWithPDF

ChatWithPDF is a GenAI-powered web application that allows users to upload documents and interact with them using a chatbot interface. Instead of manually reading lengthy PDFs or documents,users can simply ask questions and get relevant answers instantly based on the uploaded content.

**Features:**

- Upload multiple documents
- Supports PDF, DOCX and TXT files
- AI-powered responses using Gemini API
- Extracts answers based only on document content
- Dashboard + Chatbot Interface
- Smooth navigation between pages
- User-friendly UI for document interaction

Tech Stack

**Frontend:**
- HTML
- CSS
- JavaScript

**Backend:**
- Python (Flask)

**Libraries Used:**
- PyPDF2
- python-docx
- Flask-CORS
- google-generativeai

**AI Model:**
- Gemini API (LLM)

## ⚙️ Installation & Setup

### 1️⃣ Install Dependencies

Run the following command in your terminal:

pip install flask flask-cors PyPDF2 python-docx google-generativeai

---

### 2️⃣ Run Backend Server
python app.py

---

### 3️⃣ Open in Browser

http://127.0.0.1:5000


---

## How It Works

1. Upload one or more documents (PDF, DOCX or TXT)
2. Ask any question related to the uploaded content
3. The chatbot processes the document using AI
4. Relevant answers are generated instantly

---

## Future Enhancements

- Support for more file formats
- Voice-based query input
- Deployment to cloud platform
- Semantic search integration
- Vector Database support for better accuracy

---

## Use Case

This application helps users save time by enabling intelligent document interaction, making it useful for students, researchers, legal professionals and business analysts who deal with large documents regularly.

---

