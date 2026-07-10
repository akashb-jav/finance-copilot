from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
import models
from routers import expenses , budget , dashboard , chat , predictor , shopping


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # allows all methods (GET, POST etc)
    allow_headers=["*"],  # allows all headers
)



app.include_router(expenses.router)
app.include_router(budget.router)
app.include_router(dashboard.router)
app.include_router(chat.router)
app.include_router(predictor.router)
app.include_router(shopping.router) 

@app.get("/")
def home():
    return {"message": "AI Finance Copilot is running"}

@app.post("/chat")
def chat(data: dict):
    user_message = data["message"]
    return {"reply": f"You said: {user_message}"}