Copy the content below and paste it directly into your README.md file on GitHub.

code
Markdown
download
content_copy
expand_less
# 📚 Intelligent Library Assistant - Backend & AI

This is the AI-powered core of the Intelligent Library Assistant. It enables students to "talk to their books" by indexing PDF documents and using Generative AI to provide specific answers with page citations.

---

## 🛠 Tech Stack
- **Framework:** FastAPI (Python)
- **AI Model:** Google Gemini 1.5 Flash
- **Vector Database:** ChromaDB (Local Persistence)
- **Embeddings:** HuggingFace `all-MiniLM-L6-v2` (Local - no quota cost)
- **PDF Processing:** pdfplumber & LangChain Text Splitters

---

## 🚀 Getting Started (Backend Setup)

### 1. Prerequisites
- Python 3.10 or higher
- A Google AI Studio API Key ([Get it here](https://aistudio.google.com/))

### 2. Installation
Clone this repository and install the required packages:
```bash
pip install fastapi uvicorn google-generativeai chromadb pdfplumber langchain-text-splitters sentence-transformers python-multipart
3. Environment Setup

Open main.py and replace the placeholder API key with your own:

code
Python
download
content_copy
expand_less
API_KEY = "YOUR_GEMINI_API_KEY_HERE"
4. Run the Server
code
Bash
download
content_copy
expand_less
python main.py

The server will start at: http://localhost:8000
Interactive Swagger Docs: http://localhost:8000/docs

📡 API Documentation for Frontend (Vue/TS)
1. Upload a PDF

Process and index a new book into the library.

Endpoint: POST /upload

Body: multipart/form-data

Key: file (Binary PDF)

2. Ask a Question

Search the library and get an AI-generated answer.

Endpoint: GET /ask

Params: q=[your question]

Response Format:

code
JSON
download
content_copy
expand_less
{
  "answer": "The specific answer from the AI...",
  "sources": [
    { "source": "biology_textbook.pdf", "page": 12 },
    { "source": "biology_textbook.pdf", "page": 13 }
  ]
}
3. List Books

Get a list of all currently indexed books.

Endpoint: GET /list-books

Method: GET

4. Reset Database

Wipe all indexed books and start fresh.

Endpoint: DELETE /reset

Method: DELETE

💡 Frontend Integration Notes (Vue + TypeScript)
TypeScript Interfaces
code
TypeScript
download
content_copy
expand_less
export interface Source {
  source: string;
  page: number;
}

export interface AskResponse {
  answer: string;
  sources: Source[];
}
Important Tips:

CORS: The backend is configured to allow all origins (*). No extra config needed in Vue.

Loading States: Indexing PDFs takes time (approx. 0.5s per page). Please show a CircularProgress or Skeleton loader during /upload and /ask.

Error Handling: If the backend returns a 429 status code, it means the Gemini Free Tier limit was reached. Suggest the user wait 60 seconds.

Local Database: All uploaded books are saved in the /library_storage folder on the backend. They will persist even if the server restarts.

🧑‍💻 Author

Backend & AI Engineer - [Your Name/Github]

code
Code
download
content_copy
expand_less
