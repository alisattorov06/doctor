import os
import asyncio
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from database import init_db, cleanup_old_chats
from gemini_client import GeminiClient

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    asyncio.create_task(cleanup_task())
    yield

app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

gemini_client = GeminiClient()

@app.get("/")
async def read_index():
    return FileResponse("static/index.html")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/chat")
async def chat_endpoint(request: Request):
    try:
        data = await request.json()
        message = data.get("message", "").strip()
        
        if not message or len(message) > 1000:
            raise HTTPException(status_code=400, detail="Xato so'rov")
        
        ai_response = await gemini_client.generate_medical_response(message)
        return JSONResponse({"response": ai_response})
    except Exception as e:
        raise HTTPException(status_code=500, detail="Server xatosi")

async def cleanup_task():
    while True:
        await asyncio.sleep(300)
        await cleanup_old_chats()