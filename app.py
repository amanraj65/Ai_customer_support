import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# ✅ Enable CORS for frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],  # Update this for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Load DeepSeek API key
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    raise ValueError("DeepSeek API key is missing! Set it in the '.env' file.")

# ✅ Load dataset
CSV_PATH = "customer_support_tickets.csv"
if not os.path.exists(CSV_PATH):
    raise FileNotFoundError(f"Dataset file '{CSV_PATH}' not found!")

df = pd.read_csv(CSV_PATH)

# ✅ Define customer support-related keywords
support_keywords = [
    "support", "help", "issue", "refund", "payment", "account", "reset", "password",
    "login", "cancel", "billing", "error", "technical", "troubleshoot", "service",
    "order", "shipping", "warranty", "product", "return", "question", "contact",
    "assist", "assistance", "response", "fix", "repair", "helpdesk", "inquiry", "ticket", "customer"
]

# ✅ Extract relevant FAQ data
faq_data = []
for _, row in df.iterrows():
    subject = str(row.get("Ticket Subject", "")).strip().lower()
    description = str(row.get("Ticket Description", "")).strip().lower()
    resolution = str(row.get("Resolution", "")).strip()
    
    question = f"{subject} {description}".strip()
    
    if question and resolution and any(keyword in question for keyword in support_keywords):
        faq_data.append({"question": question, "answer": resolution})

# Ensure valid FAQ data exists
if not faq_data:
    raise ValueError("No valid customer support FAQ data found in the dataset!")

# ✅ Load sentence transformer model
model = SentenceTransformer("all-MiniLM-L6-v2")

# ✅ Convert questions into vector embeddings
faq_questions = [item["question"] for item in faq_data]
faq_vectors = model.encode(faq_questions)

# ✅ Initialize FAISS index
dimension = faq_vectors.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(faq_vectors))

# ✅ Function to check if a question is related to support
def is_support_related(user_question):
    user_question = user_question.lower()
    return any(keyword in user_question for keyword in support_keywords)

# ✅ Function to find the best match
def find_best_match(user_question):
    user_vector = model.encode([user_question])
    distances, closest_index = index.search(np.array(user_vector), 1)

    # ✅ Set a stricter relevance threshold (lower = better match)
    if distances[0][0] > 0.2:  
        return None  # No good match found
    
    return faq_data[closest_index[0][0]]["answer"]

# ✅ Function to get AI-generated response from DeepSeek
def get_deepseek_response(user_question):
    best_match = find_best_match(user_question)

    # ✅ If the question is not related to support, ask DeepSeek to handle it
    if not is_support_related(user_question):
        prompt = f"User asked: {user_question}\nThis does not appear to be related to customer support. Kindly inform the user and redirect them to relevant support topics."
    elif best_match:
        prompt = f"User asked: {user_question}\nFAQ Answer: {best_match}\nIf the FAQ answer is correct, expand on it. If it's incorrect, ignore it and provide a correct response."
    else:
        prompt = f"User asked: {user_question}\nNo matching FAQ found. Generate an appropriate customer support response."

    api_url = "https://api.deepseek.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}"}
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are a helpful customer support AI."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json().get("choices", [{}])[0].get("message", {}).get("content", "No response generated.")
    
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"DeepSeek API error: {str(e)}")

# ✅ API endpoint
@app.get("/chat")
def chat(user_question: str):
    if not user_question.strip():
        raise HTTPException(status_code=400, detail="User question cannot be empty.")

    response = get_deepseek_response(user_question)
    return {"response": response}