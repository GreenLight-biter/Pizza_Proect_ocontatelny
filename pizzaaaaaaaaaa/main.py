from fastapi import FastAPI
from routes import router

app = FastAPI()

@app.get("/")
async def home():
    return {"message": "Добро пожаловать в Pizza API!"}

# Подключаем все роуты
app.include_router(router)