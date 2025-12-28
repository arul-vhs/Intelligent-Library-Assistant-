📚 Intelligent Library Assistant - API Documentation
This is the backend "AI Brain" for the Library Assistant. It uses FastAPI, ChromaDB for local vector search, and Google Gemini 1.5 Flash for natural language generation.
🌐 Server Details
Base URL: http://localhost:8000
Swagger UI (Interactive Docs): http://localhost:8000/docs
CORS: Enabled for all origins (*).
🛠 Prerequisites for Frontend Team
If you need to run this backend locally:
Install Python 3.10+
Install dependencies:
code
Bash
pip install fastapi uvicorn google-generativeai chromadb pdfplumber langchain-text-splitters sentence-transformers python-multipart
Run the server:
code
Bash
python main.py
(Note: On the very first run, it will download an 80MB embedding model. Please wait for the terminal to say "Uvicorn running").
📡 API Endpoints
1. Upload a Book
Uploads a PDF file to the library. The backend will parse the PDF and index it for searching.
URL: /upload
Method: POST
Content-Type: multipart/form-data
Body:
file: (Binary PDF file)
Response (200):
code
JSON
{
  "message": "Successfully indexed biology_101.pdf",
  "chunks_created": 142
}
2. Ask a Question
Queries the library for an answer. The AI will look through all uploaded books to find the relevant context.
URL: /ask
Method: GET
Params:
q: (string) The student's question.
Response (200):
code
JSON
{
  "answer": "Photosynthesis is the process used by plants... [Page 12]",
  "sources": [
    { "source": "biology_101.pdf", "page": 12 },
    { "source": "biology_101.pdf", "page": 13 }
  ]
}
3. List All Books
Returns a list of all unique PDF filenames currently indexed.
URL: /list-books
Method: GET
Response (200):
code
JSON
{
  "books": ["biology_101.pdf", "chemistry_notes.pdf"]
}
4. Reset Library
Wipes the entire database. Use this to start fresh during testing.
URL: /reset
Method: DELETE
🏗 TypeScript Interfaces
You can use these interfaces in your Vue components:
code
TypeScript
export interface Source {
  source: string;
  page: number;
}

export interface AskResponse {
  answer: string;
  sources: Source[];
}

export interface BookListResponse {
  books: string[];
}
⚠️ Important Notes
Upload Latency: Indexing a PDF involves text extraction and vector math. For a 50-page PDF, it might take 10-15 seconds. Please implement a loading spinner in the UI.
AI Latency: The /ask endpoint takes about 2-4 seconds as it communicates with Google Gemini.
Error 429: If you hit the Gemini Free Tier limit, the API will return a 429 error. Please catch this and tell the user to wait 60 seconds.
PDF Only: The backend currently only accepts files ending in .pdf.
Example Axios Implementation (Vue)
code
TypeScript
import axios from 'axios';

const API_BASE = "http://localhost:8000";

// Asking a question
async function getAnswer(query: string) {
  try {
    const response = await axios.get<AskResponse>(`${API_BASE}/ask`, {
      params: { q: query }
    });
    return response.data;
  } catch (error) {
    console.error("AI Assistant Error", error);
  }
}
