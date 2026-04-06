from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# import all routers
from routers import upload, chat, quiz, attention, xai

app = FastAPI(title="NeuralLearn AI")

# CORS (for frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ REGISTER ALL ROUTES
app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(quiz.router, prefix="/api/quiz", tags=["Quiz"])
app.include_router(attention.router, prefix="/api/attention", tags=["Attention"])
app.include_router(xai.router, prefix="/api/xai", tags=["XAI"])

# health check
@app.get("/")
def root():
    return {"message": "API running"}

@app.get("/api/health")
def health():
    return {"status": "ok"}
    
@app.get("/health")
def health_simple():
    return {"status": "ok"}



