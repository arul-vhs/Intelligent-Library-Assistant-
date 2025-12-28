import os
import shutil
from typing import List
from fastapi import FastAPI, UploadFile, File, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# AI and Database Imports
import google.generativeai as genai
import chromadb
from chromadb.utils import embedding_functions
import pdfplumber
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 1. --- CONFIGURATION & AI SETUP ---
# Replace with your actual Gemini API Key
API_KEY = "AIzaSyBCGMiX429asYZew8ELFWaphUDA-q4Kfac"
genai.configure(api_key=API_KEY)

app = FastAPI(title="Intelligent Library Assistant API")

# Enable CORS so the Vue frontend can communicate with this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. --- VECTOR DATABASE SETUP (LOCAL EMBEDDINGS) ---
# We use 'all-MiniLM-L6-v2' which runs locally on your CPU. 
# It converts text into math vectors without using your Gemini Quota.
local_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

# This creates a folder named 'library_storage' to save your indexed books
client = chromadb.PersistentClient(path="./library_storage")
collection = client.get_or_create_collection(
    name="library_collection", 
    embedding_function=local_ef
)

# 3. --- HELPER FUNCTIONS ---

def extract_pdf_data(file_path):
    """Extracts text from each page of the PDF along with page numbers."""
    pages_content = []
    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                pages_content.append({"text": text, "page": i + 1})
    return pages_content

# 4. --- API ENDPOINTS ---

@app.get("/")
def root():
    return {"message": "Library Assistant API is running!"}

@app.post("/upload")
async def upload_book(file: UploadFile = File(...)):
    """
    Endpoint to upload a PDF. 
    It reads the PDF, splits it into small chunks, and stores them in the vector DB.
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # Extract text page by page
        raw_docs = extract_pdf_data(temp_path)
        
        # Split text into chunks (approx 700 characters each)
        # This helps the AI find very specific sections of a book
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=700, 
            chunk_overlap=100
        )
        
        final_texts = []
        final_metadatas = []
        final_ids = []

        for doc in raw_docs:
            chunks = text_splitter.split_text(doc["text"])
            for j, chunk in enumerate(chunks):
                final_texts.append(chunk)
                final_metadatas.append({
                    "source": file.filename, 
                    "page": doc["page"]
                })
                final_ids.append(f"{file.filename}_{doc['page']}_{j}")

        # Add to ChromaDB
        collection.add(
            documents=final_texts,
            metadatas=final_metadatas,
            ids=final_ids
        )
        
        return {
            "message": f"Successfully indexed {file.filename}", 
            "chunks_created": len(final_texts)
        }
    
    except Exception as e:
        print(f"Error during upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.get("/ask")
async def ask_question(q: str = Query(..., description="The student's question")):
    """
    Endpoint to ask a question.
    1. Searches the Vector DB for the most relevant pages.
    2. Sends that context to Gemini to generate a final answer.
    """
    # Search for top 5 most relevant chunks from the library
    results = collection.query(
        query_texts=[q],
        n_results=5
    )
    
    # Flatten the results into one string for the AI
    context_text = "\n\n".join(results['documents'][0])
    sources = results['metadatas'][0]

    if not context_text:
        return {"answer": "I couldn't find any information on that topic in the library."}

    # Use Gemini 1.5 Flash to generate the answer based on retrieved context
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    You are an Intelligent Library Assistant.
    Use the following book excerpts to answer the student's question.
    If the answer is not in the context, say you don't know.
    
    Context:
    {context_text}
    
    Question:
    {q}
    
    Answer:
    """
    
    try:
        response = model.generate_content(prompt)
        return {
            "answer": response.text,
            "sources": sources
        }
    except Exception as e:
        # Handle Quota 429 errors here
        raise HTTPException(status_code=429, detail="Gemini API busy. Please try again in a minute.")

@app.get("/list-books")
async def list_books():
    """Returns a list of all unique filenames currently in the library."""
    data = collection.get(include=['metadatas'])
    if not data['metadatas']:
        return {"books": []}
    
    # Extract unique source names from metadata
    unique_books = list(set([m['source'] for m in data['metadatas']]))
    return {"books": unique_books}

@app.delete("/reset")
async def reset_library():
    """Clears all stored books and indices."""
    global collection
    client.delete_collection("library_collection")
    collection = client.get_or_create_collection(
        name="library_collection", 
        embedding_function=local_ef
    )
    return {"message": "Library data wiped successfully."}

# 5. --- START THE SERVER ---
if __name__ == "__main__":
    import uvicorn
    # Make sure to run this on 0.0.0.0 so other devices on your network can access it
    uvicorn.run(app, host="0.0.0.0", port=8000)