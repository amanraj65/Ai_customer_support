import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # Import CORS middleware
import pandas as pd
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import requests
from dotenv import load_dotenv  # Load environment variables from .env file

# Load .env file
load_dotenv()

app = FastAPI()

# ✅ Add CORS Middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to ["http://127.0.0.1:5500"] for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load DeepSeek API key from .env
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    raise ValueError("DeepSeek API key is missing! Set it in the '.env' file.")

# 1️⃣ Load dataset (Ensure file exists)
CSV_PATH = "customer_support_tickets.csv"
if not os.path.exists(CSV_PATH):
    raise FileNotFoundError(f"Dataset file '{CSV_PATH}' not found!")

df = pd.read_csv(CSV_PATH)

# 2️⃣ Extract questions and answers
faq_data = []
for _, row in df.iterrows():
    question = str(row.get("Ticket Subject", "")).strip()
    answer = str(row.get("Resolution", "")).strip()
    if question and answer:
        faq_data.append({"question": question, "answer": answer})

if not faq_data:
    raise ValueError("No valid FAQ data found in the dataset!")

# 3️⃣ Load sentence transformer model
model = SentenceTransformer("all-MiniLM-L6-v2")

# 4️⃣ Convert questions into vector embeddings
faq_questions = [item["question"] for item in faq_data]
faq_vectors = model.encode(faq_questions)

# 5️⃣ Initialize FAISS index
dimension = faq_vectors.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(faq_vectors))

# 6️⃣ Function to find best match
def find_best_match(user_question):
    user_vector = model.encode([user_question])
    _, closest_index = index.search(np.array(user_vector), 1)
    return faq_data[closest_index[0][0]]["answer"]

# 7️⃣ Function to get AI-generated response
def get_deepseek_response(user_question):
    try:
        best_match = find_best_match(user_question)

        api_url = "https://api.deepseek.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}"}
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "You are a customer support AI assistant."},
                {"role": "user", "content": f"User asked: {user_question}\nFAQ Answer: {best_match}\nProvide a detailed response."}
            ]
        }

        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()  # Raise error for bad status codes
        return response.json().get("choices", [{}])[0].get("message", {}).get("content", "No response generated.")

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"DeepSeek API error: {str(e)}")

# 8️⃣ API endpoint
@app.get("/chat")
def chat(user_question: str):
    if not user_question.strip():
        raise HTTPException(status_code=400, detail="User question cannot be empty.")

    response = get_deepseek_response(user_question)
    return {"response": response}