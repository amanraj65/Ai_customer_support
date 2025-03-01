AI Customer Support Chatbot

📌 Overview

This is an AI-powered customer support chatbot that uses FAISS for vector search and DeepSeek API for AI-generated responses. It allows users to ask questions and receive relevant answers based on a dataset of customer support tickets.

🚀 Features

Vector Database (FAISS) for efficient FAQ retrieval

DeepSeek AI Integration for generating responses

FastAPI Backend to handle API requests

Beautiful Material UI Frontend with a scrollable chatbox

🛠️ Setup Instructions

1️⃣ Clone the Repository

git clone https://github.com/amanraj65/Ai_customer_support.git
cd Ai_customer_support

2️⃣ Install Dependencies

Make sure you have Python installed, then run:

pip install -r requirements.txt

3️⃣ Setup Environment Variables

Create a .env file in the project directory and add your DeepSeek API key:

DEEPSEEK_API_KEY=your_api_key_here

4️⃣ Run the Backend (FastAPI)

uvicorn app:app --reload

This will start the server at: http://127.0.0.1:8000

5️⃣ Open the Frontend

Simply open index.html in your browser or run a local server:

python -m http.server 5500

Now, open http://127.0.0.1:5500 in your browser.

📌 API Endpoints

GET /chat?user_question=your_question → Returns AI-generated responses based on FAQs and DeepSeek API.

🤝 Contributing

Fork the repository 🍴

Create a new branch 🔀 (git checkout -b feature-branch)

Commit changes ✅ (git commit -m "Added a new feature")

Push to GitHub 🚀 (git push origin feature-branch)

Open a Pull Request 📢

📄 License

This project is open-source and available under the MIT License.

💡 Author

Made with ❤️ by Aman Raj

GitHub: amanraj65

