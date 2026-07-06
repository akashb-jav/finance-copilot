from fastapi import FastAPI
from database import engine
import models
from routers import expenses

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(expenses.router)

@app.get("/")
def home():
    return {"message": "AI Finance Copilot is running"}

@app.post("/chat")
def chat(data: dict):
    user_message = data["message"]
    return {"reply": f"You said: {user_message}"}