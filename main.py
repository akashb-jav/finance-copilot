from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "AI Finance Copilot is running"}

@app.post("/chat")
def chat(data: dict):
    user_message = data["message"]
    return {"reply": f"You said: {user_message}"}