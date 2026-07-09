# AI Finance Copilot

An AI-powered personal finance assistant that helps users manage their money through a chat interface.

## Features

- 💰 **Finance Copilot** — Track expenses, set budgets, get AI-powered financial advice
- 📈 **Smart Savings Predictor** — Predicts your month-end balance and warns you before you overspend
- 🛍️ **Shopping Assistant** — Compare product prices and get buy now or wait recommendations

## Tech Stack

- **Backend:** Python, FastAPI, SQLite, SQLAlchemy
- **AI:** Fireworks AI API (Llama 3.1 on AMD hardware)
- **Frontend:** HTML, CSS, JavaScript

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/akashb-jav/finance-copilot.git
cd finance-copilot
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up environment variables
Create a `.env` file in the root folder:
SERPAPI_KEY=your_serpapi_key
FIREWORKS_API_KEY=your_fireworks_api_key

### 4. Run the backend
```bash
uvicorn main:app --reload
```

### 5. Open the API docs
http://127.0.0.1:8000/docs

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /expenses | Add a new expense |
| GET | /expenses/{user_id} | Get all expenses for a user |
| POST | /budget | Set a budget |
| GET | /budget/{user_id} | Get all budgets for a user |
| GET | /dashboard/{user_id} | Get dashboard summary |
| POST | /chat | Chat with AI finance advisor |
| GET | /predict/{user_id} | Get savings prediction |
| GET | /shopping | Search and compare product prices |

## Team

- Akash — Backend
- Kiruthika — Frontend

## Hackathon

Built for AMD Developer Hackathon ACT II — Track 3 Unicorn